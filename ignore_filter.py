from gitignore_parser import parse_gitignore
import os


class IgnoreFilter:
    """
    Class to filter out files and directories based on a .embedding_ignore file
    The structure of the .embedding_ignore file is the same as a .gitignore file.
    """

    def __init__(self, ignore_file_path):
        if os.path.exists(ignore_file_path):
            self.ignore_file_path = ignore_file_path
            self.matches = parse_gitignore(ignore_file_path)
        else:
            print("[WARNING] Ignore file not found, not using ignore filter.")
            self.ignore_file_path = None
            self.matches = lambda x: False

    def is_ignored(self, path):
        """
        Returns True if the path is ignored by the filter, False otherwise
        """
        return self.matches(path)


if __name__ == "__main__":
    ignore_filter = IgnoreFilter(".embedding_ignore")
    print(
        "Should ignore requirements.txt:", ignore_filter.is_ignored("requirements.txt")
    )
