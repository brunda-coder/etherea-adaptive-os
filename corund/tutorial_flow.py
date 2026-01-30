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
        self.avatar = AvatarEngine(key_password=avatar_password)
        self.docs_loader = MDLoader(docs_folder)
        # { "topic/file.md": "content..." }
        self.docs = self.docs_loader.load_all()

        # Tutorial steps
        self.steps = []
        self.current_step = 0

        # Load or initialize tutorial state
        tutorial_state = self.memory.get_all_preferences().get("tutorial_state")
        if tutorial_state:
            try:
                self.tutorial_state = tutorial_state
                self.current_step = self.tutorial_state.get("current_step", 0)
            except Exception:
                self.tutorial_state = {"current_step": 0}
                self.current_step = 0
        else:
            self.tutorial_state = {"current_step": 0}

    # --- Step Management ---

    def add_step(self, step_fn):
        """Add a function representing a tutorial step"""
        self.steps.append(step_fn)

    def next_step(self):
        """Execute next step and update memory"""
        if self.current_step < len(self.steps):
            try:
                self.steps[self.current_step]()
            except Exception as e:
                debug_print("TutorialFlow", f"Step execution error: {e}")
            self.current_step += 1
            self._save_state()
        else:
            debug_print("TutorialFlow", "Tutorial finished!")

    def reset(self):
        """Reset tutorial flow"""
        self.current_step = 0
        self._save_state()

    def _save_state(self):
        """Save tutorial state to memory"""
        self.memory.update_preference(
            "tutorial_state", {"current_step": self.current_step})

    # --- Dynamic Data Injection ---

    def ask_bot(self, user_text: str) -> str:
        """
        Sends user input to AvatarEngine (Etherea AI)
        Optionally prepends docs knowledge from MDLoader
        """
        # Combine loaded docs into one context string
        docs_context = "\n".join(self.docs.values())
        prompt = f"Use the following Etherea docs to respond:\n{docs_context}\n\nUser: {user_text}"

        # Generate response from AvatarEngine
        try:
            response = self.avatar.speak(prompt)
        except Exception as e:
            debug_print("TutorialFlow", f"AvatarEngine error: {e}")
            response = "Etherea encountered an internal error."

        # Update memory with last interaction
        try:
            interactions = self.memory.get_all_preferences().get("interactions", [])
            interactions.append({"user": user_text, "bot": response})
            self.memory.update_preference("interactions", interactions)
        except Exception as e:
            debug_print("TutorialFlow", f"Memory update error: {e}")

        return response

    # --- Utility Functions ---

    def list_docs(self):
        """Return list of loaded docs"""
        return list(self.docs.keys())

    def get_doc(self, doc_key: str) -> str:
        """Return content of a specific doc"""
        return self.docs.get(doc_key, "")

    def check_triggers(self, context: dict) -> str:
        """
        Evaluate rules for showing pop-ups.
        Returns a tutorial message or None.
        """
        # Rule 1: First launch
        if self.current_step == 0 and context.get("startup", False):
            return "Welcome to Etherea. I am your operating system. How may I assist you today?"

        # Rule 2: High stress
        if context.get("stress", 0) > 0.8:
            return "I notice signs of stress. Would you like to enable Focus Mode?"
        
        return None
