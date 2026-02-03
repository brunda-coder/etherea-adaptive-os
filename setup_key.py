import tkinter as tk
from tkinter import simpledialog, messagebox
import os


def setup_api_key():
    root = tk.Tk()
    root.withdraw()  # Hide main window

    key = simpledialog.askstring(
        "Gemini API Key Setup",
        "Enter your Gemini API Key (Google AI Studio):\n\n"
        "This will be saved to .env locally as GEMINI_API_KEY.\n"
        "No key = AI disabled mode (UI still works).",
        show="*",
    )

    if key:
        with open(".env", "w", encoding="utf-8") as f:
            f.write(f"GEMINI_API_KEY={key}\n")
            # Optional convenience flags
            f.write("AI_PROVIDER=gemini\n")

        messagebox.showinfo("Success", "Gemini API key saved to .env ✅")
    else:
        messagebox.showwarning("No Key", "No key entered. AI will remain disabled (UI still works).")


if __name__ == "__main__":
    setup_api_key()
