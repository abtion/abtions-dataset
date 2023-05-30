import os
import json
from dotenv import load_dotenv
import openai
from gitignore_parser import parse_gitignore

# Load environment variables from .env file
load_dotenv()

# OpenAI API credentials
API_KEY = os.getenv("OPENAI_API_KEY")

# Set OpenAI API key
openai.api_key = API_KEY

EMBEDDING_MODEL = "text-embedding-ada-002"


# Function to call OpenAI Embedding API
def call_openai_embedding_api(text):
    response = openai.Embedding.create(
        model=EMBEDDING_MODEL,
        input=text,
    )
    return response


def is_ignored(path, matches):
    return matches(path)


def process_folder(folder_abs_path):
    embedding_ignore_path = os.path.join(folder_abs_path, ".embedding_ignore")
    if os.path.exists(embedding_ignore_path):
        matches = parse_gitignore(embedding_ignore_path)
    else:
        matches = []

    for root, dirs, files in os.walk(folder_abs_path):
        # Remove ignored directories
        dirs[:] = [d for d in dirs if not is_ignored(os.path.join(root, d), matches)]
        files[:] = [f for f in files if not is_ignored(os.path.join(root, f), matches)]

        for file in files:
            if file.endswith(".md") or file.endswith(".txt"):
                file_path = os.path.join(root, file)

                # Read the contents of the markdown file as a single string
                markdown_text = ""
                with open(file_path, "r") as f:
                    for line in f:
                        markdown_text += line.strip()

                # Call OpenAI Embedding API
                response = call_openai_embedding_api(markdown_text)

                # Save the query embedding in a JSON file with the same name
                json_file_path = os.path.splitext(file_path)[0] + ".json"
                with open(json_file_path, "w") as f:
                    json.dump(response, f)

                print(f"Saved query embedding for {file} in {json_file_path}")


# Usage
folder_abs_path = "."
process_folder(folder_abs_path)
