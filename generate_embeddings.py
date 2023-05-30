import os
import json
import openai
from config import Config
from ignore_filter import IgnoreFilter


EMBEDDING_MODEL = "text-embedding-ada-002"

# Set OpenAI API key
openai.api_key = Config.OPENAI_API_KEY


# Function to call OpenAI Embedding API
def call_openai_embedding_api(text):
    response = openai.Embedding.create(
        model=EMBEDDING_MODEL,
        input=text,
    )
    return response


def process_folder(folder_abs_path, ignore_filter):
    for root, dirs, files in os.walk(folder_abs_path):
        # Remove ignored directories
        dirs[:] = [
            d for d in dirs if not ignore_filter.is_ignored(os.path.join(root, d))
        ]
        # Remove ignored files
        files[:] = [
            f for f in files if not ignore_filter.is_ignored(os.path.join(root, f))
        ]

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

# Load ignore filter
embedding_ignore_path = os.path.join(folder_abs_path, ".embedding_ignore")
ignore_filter = IgnoreFilter(embedding_ignore_path)

process_folder(folder_abs_path, ignore_filter)
