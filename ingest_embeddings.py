import redis
from redis_client import RedisClient
from redis.commands.search.field import TagField, TextField, VectorField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
import os
import json
import numpy as np
from ignore_filter import IgnoreFilter
import argparse
import yaml


# Define index name and document prefix
INDEX_NAME = "index"
DOC_PREFIX = "doc:"
VECTOR_DIMENSIONS = 1536


def delete_index():
    try:
        r.ft(INDEX_NAME).dropindex(delete_documents=True)
        print("Index deleted!")
    except:
        print("Index does not exist!")


def create_index(vector_dimensions: int):
    try:
        # check to see if index exists
        r.ft(INDEX_NAME).info()
        print("Index already exists!")
    except:
        # schema
        schema = (
            TagField("tag"),
            TextField("content"),
            VectorField(
                "vector",
                "FLAT",  # FLAT OR HSNW
                {
                    "TYPE": "FLOAT32",  # FLOAT32 or FLOAT64
                    "DIM": vector_dimensions,  # Number of Vector Dimensions
                    "DISTANCE_METRIC": "COSINE",  # Vector Search Distance Metric
                },
            ),
            TextField("link"),
            TextField("filename"),
            TagField("category"),
        )

        # index Definition
        definition = IndexDefinition(prefix=[DOC_PREFIX], index_type=IndexType.HASH)

        # create Index
        r.ft(INDEX_NAME).create_index(fields=schema, definition=definition)


# Function to insert embeddings into Redis index
def insert_embedding(pipe: redis.client.Pipeline, file_name: str, category: str):
    # Load the JSON data from file
    with open(file_name, "r") as f:
        json_data = json.load(f)

    # Extract the embedding from the JSON data
    embedding = json_data["data"][0]["embedding"]

    # Open the file with the same name but ending in .md or .txt
    base_name = os.path.splitext(os.path.basename(file_name))[0]
    file_dir = os.path.dirname(file_name)
    content = None

    for extension in [".md", ".txt"]:
        try:
            with open(
                os.path.join(file_dir, base_name + extension), "r", encoding="utf8"
            ) as f:
                content = f.read()
                break
        except FileNotFoundError:
            continue

    if content is None:
        print(f"No text file (.md or .txt) found for {file_name}")
        return

    yaml_file_path = os.path.join(file_dir, base_name + ".yaml")

    pipe.hset(
        f"{DOC_PREFIX}{file_dir}/{base_name}",
        mapping={
            "content": content,
            "vector": np.array(embedding).astype(np.float32).tobytes(),
            "tag": "openai",
            "link": get_link_from_yaml(yaml_file_path),
            "filename": base_name,
            "category": category
        },
    )

    print(f"Inserted {file_name}")

def get_link_from_yaml(file_path):
    try:
        # Open the file
        with open(file_path, 'r') as file:
            # Load the YAML data
            data = yaml.safe_load(file)
            # Get the value of the key 'link'
            value = data.get('link')
    except FileNotFoundError:
        value = ""

    return value


def get_category_from_path(file_path: str):
    return os.path.basename(os.path.dirname(os.path.normpath(file_path)))

def process_file(pipe, file_path, ignore_filter):
    if file_path.endswith(".json") and not ignore_filter.is_ignored(file_path):
        category = get_category_from_path(file_path)
        insert_embedding(pipe, file_path, category)


def process_folder(pipe, folder_abs_path, ignore_filter):
    for root, dirs, files in os.walk(folder_abs_path):
        # Remove ignored directories
        dirs[:] = [
            d for d in dirs if not ignore_filter.is_ignored(os.path.join(root, d))
        ]

        for file in files:
            file_path = os.path.join(root, file)
            process_file(pipe, file_path, ignore_filter)


# Argument Parser
parser = argparse.ArgumentParser(
    description="Insert embeddings for specific file or directory into Redis index"
)
parser.add_argument(
    "path",
    type=str,
    nargs="?",
    default=".",
    help="The path to the specific file or directory",
)
parser.add_argument(
    "--reset", action="store_true", help="Reset the index before inserting embeddings"
)
args = parser.parse_args()

# Determine the directory of this script
script_directory = os.path.dirname(os.path.realpath(__file__))

# Load ignore filter
embedding_ignore_path = os.path.join(script_directory, ".embedding_ignore")
ignore_filter = IgnoreFilter(embedding_ignore_path)

# Create the index
with RedisClient() as r:
    # Delete the index if the reset flag was provided
    if args.reset:
        delete_index()

    create_index(vector_dimensions=VECTOR_DIMENSIONS)

    # Check if path is a file or a directory
    if os.path.isfile(args.path):
        pipe = r.pipeline()
        process_file(pipe, args.path, ignore_filter)
        pipe.execute()
    elif os.path.isdir(args.path):
        pipe = r.pipeline()
        process_folder(pipe, args.path, ignore_filter)
        pipe.execute()
    else:
        print(f"{args.path} is not a valid file or directory.")
