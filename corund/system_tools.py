import subprocess
import os
import sys


class SystemTools:
    @staticmethod
    def execute(command: str) -> str:
        """
        Executes a shell command and returns output.
        Basic safety checks included to prevent destructive commands.
        """
        if not command:
            return ""

        # Safety blocks to prevent destructive commands
        unsafe_keywords = ["rm -rf", "format", "del /s", "rd /s"]
        if any(keyword in command.lower() for keyword in unsafe_keywords):
            return "Safety Protocol: Command blocked due to destructive potential."

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            output = result.stdout or ""
            if result.stderr:
                output += f"\nErrors: {result.stderr}"
            return output.strip()
        except subprocess.TimeoutExpired:
            return "Execution Error: Command timed out."
        except Exception as e:
            return f"Execution Error: {e}"

    @staticmethod
    def open_file_explorer(path: str = ".") -> str:
        """
        Opens the system file explorer at the given path.
        Works on Windows, macOS, and Linux.
        """
        abs_path = os.path.abspath(path)

        try:
            if sys.platform.startswith("win"):
                os.startfile(abs_path)
            elif sys.platform.startswith("darwin"):
                subprocess.run(["open", abs_path])
            else:  # Linux and others
                subprocess.run(["xdg-open", abs_path])
            return f"Opened {abs_path}"
        except Exception as e:
            return f"Failed to open path '{abs_path}': {e}"
