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
        """Initialize TutorialFlow with local-first modules."""
        self.memory = MemoryStore()
        try:
            self.avatar = AvatarEngine(key_password=avatar_password)
        except Exception as e:
            debug_print("TutorialFlow", f"AvatarEngine init failed (offline fallback): {e}")
            self.avatar = None
        self.docs_loader = MDLoader(docs_folder)
        self.docs_cache = {}

    def load_docs(self, topic_file: str):
        if topic_file in self.docs_cache:
            return self.docs_cache[topic_file]
        content = self.docs_loader.load_file(topic_file)
        self.docs_cache[topic_file] = content
        return content

    def run_step(self, topic_file: str, user_input: str):
        doc = self.load_docs(topic_file)
        prompt = f"""
You are guiding a user through an Etherea tutorial.
Here is the tutorial content:
{doc}

User input:
{user_input}

Reply as Etherea in 1-2 short paragraphs.
"""

        if self.avatar is None:
            response = "I’m Etherea, and I can continue this tutorial locally without network features."
        else:
            try:
                response = self.avatar.speak(prompt)
            except Exception as e:
                debug_print("TutorialFlow", f"AvatarEngine error: {e}")
                response = "I’m Etherea. I hit a temporary issue, so I’m continuing in local tutorial mode."

        try:
            self.memory.save_step(topic_file, user_input, response)
        except Exception as e:
            debug_print("TutorialFlow", f"Failed to save step memory: {e}")

        return response
