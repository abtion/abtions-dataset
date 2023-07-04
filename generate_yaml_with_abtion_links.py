import os
import yaml

# Define the directory
directory = 'inside.abtion.com'

# Loop over the directories and files recursively
for dirpath, dirnames, filenames in os.walk(directory):
    # Loop over the files in the current directory
    for filename in filenames:
        # Check if the file is a .json
        if filename.endswith('.json'):
            # Get the file name without extension
            file_without_ext = os.path.splitext(filename)[0]
            # Get the relative directory path
            relative_dir_path = os.path.relpath(dirpath, directory)
            # Construct the URL-style link
            link = relative_dir_path.replace(os.sep, '/') + '/' + file_without_ext
            print(f"https://inside.abtion.com/{link}.html")
            # Create a dictionary with the link key
            data = {'link': f"https://inside.abtion.com/{link}.html"}
            # Create the yaml file name
            yaml_filename = os.path.join(dirpath, file_without_ext + '.yaml')
            # Create the yaml file with the data
            with open(yaml_filename, 'w') as yaml_file:
                yaml.dump(data, yaml_file)
