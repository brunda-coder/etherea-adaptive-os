# core/tutorial_flow.py
"""
Tutorial Flow for Etherea
- Orchestrates step-by-step sequences or dynamic knowledge injection
- Integrates AvatarEngine, MDLoader, and MemoryStore
"""

from corund.avatar_engine import AvatarEngine
from corund.memory_store import MemoryStore
from corund.md_loader import MDLoader
from corund.utils import debug_print


class TutorialFlow:
    def __init__(self, docs_folder="docs", avatar_password=None):
        """
        Initialize TutorialFlow with:
        - MDLoader for docs_folder
        - AvatarEngine for AI responses
        - MemoryStore for persistent state
        """
        # Core systems
        self.memory = MemoryStore()  # MemoryStore uses global SQLite by default
        try:
            self.avatar = AvatarEngine(key_password=avatar_password)
        except Exception as e:
            debug_print("TutorialFlow", f"AvatarEngine init failed (AI disabled): {e}")
            self.avatar = None
        self.docs_loader = MDLoader(docs_folder)
        # { "topic/file.md": "content..." }
        self.docs_cache = {}

    def load_docs(self, topic_file: str):
        """
        Load tutorial markdown doc into memory.
        """
        if topic_file in self.docs_cache:
            return self.docs_cache[topic_file]

        content = self.docs_loader.load_file(topic_file)
        self.docs_cache[topic_file] = content
        return content

    def run_step(self, topic_file: str, user_input: str):
        """
        Execute a tutorial step based on a topic file and user response.
        """
        doc = self.load_docs(topic_file)

        prompt = f"""
You are guiding a user through an Etherea tutorial.
Here is the tutorial content:
{doc}

User input:
{user_input}

Reply as Etherea in 1-2 short paragraphs.
"""

        # Generate response from AvatarEngine (optional)
        if self.avatar is None:
            response = "AI is offline (no GEMINI_API_KEY configured). Tutorial can continue without AI."
        else:
            try:
                response = self.avatar.speak(prompt)
            except Exception as e:
                debug_print("TutorialFlow", f"AvatarEngine error: {e}")
                response = "AI is offline or encountered an error."

        # Save memory of this step
        try:
            self.memory.save_step(topic_file, user_input, response)
        except Exception as e:
            debug_print("TutorialFlow", f"Failed to save step memory: {e}")

        return response
