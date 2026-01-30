import os
import sys


class MDLoader:
    """
    Simple Markdown loader for Etherea documentation.
    Scans a folder recursively and reads all `.md` files,
    storing their contents keyed by relative path.
    """

    def __init__(self, docs_folder: str):
        # Handle PyInstaller _MEIPASS
        if hasattr(sys, "_MEIPASS"):
            base_path = sys._MEIPASS
        else:
            base_path = os.getcwd()

        self.docs_folder = os.path.join(base_path, docs_folder)
        self.documents = {}

    def load_all(self) -> dict:
        """
        Reads all markdown files in docs_folder and stores
        content keyed by relative path.

        :return: dict {relative_path: file_content}
        """
        if not os.path.exists(self.docs_folder) or not os.path.isdir(self.docs_folder):
            print(
                f"MDLoader Warning: Docs folder '{self.docs_folder}' not found or not a directory.")
            return {}

        for root, dirs, files in os.walk(self.docs_folder):
            for file in files:
                if file.lower().endswith(".md"):
                    path = os.path.join(root, file)
                    rel_path = os.path.relpath(path, self.docs_folder)
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            self.documents[rel_path] = f.read()
                    except Exception as e:
                        print(f"MDLoader Error: Failed to read '{path}': {e}")

        # return a copy to prevent external mutation
        return dict(self.documents)
