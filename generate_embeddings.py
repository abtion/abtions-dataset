import os
import json
import openai
import argparse
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
            file_path = os.path.join(root, file)
            process_file(file_path)


def process_file(file_path):
    if file_path.endswith(".md") or file_path.endswith(".txt"):
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

        print(
            f"Saved query embedding for {os.path.basename(file_path)} in {json_file_path}"
        )


# Argument Parser
parser = argparse.ArgumentParser(
    description="Generate embeddings for specific file or directory"
)
parser.add_argument(
    "path",
    type=str,
    nargs="?",
    default=".",
    help="The path to the specific file or directory",
)
args = parser.parse_args()

# Determine the directory of this script
script_directory = os.path.dirname(os.path.realpath(__file__))

# Load ignore filter
embedding_ignore_path = os.path.join(script_directory, ".embedding_ignore")
ignore_filter = IgnoreFilter(embedding_ignore_path)

# Check if path is a file or a directory
if os.path.isfile(args.path):
    process_file(args.path)
elif os.path.isdir(args.path):
    process_folder(args.path, ignore_filter)
else:
    print(f"{args.path} is not a valid file or directory.")
