import tkinter as tk
from tkinter import simpledialog, messagebox
import os


def setup_api_key():
    root = tk.Tk()
    root.withdraw()  # Hide main window

    key = simpledialog.askstring("OpenAI API Key Needs Setup",
                                 "Enter your OpenAI API Key (starts with sk-...):\n\n This will be saved to .env locally.",
                                 show="*")

    if key:
        with open(".env", "w", encoding="utf-8") as f:
            f.write(f"OPENAI_API_KEY={key}\n")
            f.write(f"OPENAI_API_KEY2={key}\n")  # keep compatibility with GitHub secret naming
        messagebox.showinfo(
            "Success", "API Key saved to .env!\n\nRestart Etherea to apply.")
    else:
        messagebox.showwarning(
            "Cancelled", "No key entered. Etherea will run in offline mode.")


if __name__ == "__main__":
    setup_api_key()
