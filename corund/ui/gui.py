# ui/gui.py
"""
Aurora GUI (refined)
- Thread-safe UI updates (never touch Tk widgets from worker threads)
- Buttons: Read Aloud, Regenerate, 👍 / 👎 Feedback
- Works with avatars exposing either `generate_response` or `speak`
- Integrates VoiceEngine and MemoryStore
"""

import tkinter as tk
from tkinter import scrolledtext, Label, Entry, Frame, Button
import threading
import time
import random
from typing import Any, Dict

# Import VoiceEngine & MemoryStore (make sure core package path is correct)
from corund.voice_engine import VoiceEngine
from corund.memory_store import MemoryStore


# -------------------------
# Visuals / Floating Animations
# -------------------------
class Visuals:
    def __init__(self, gui_root: tk.Tk, visual_canvas: tk.Canvas, aura_item: int, status_label: tk.Label):
        self.root = gui_root
        self.visual_canvas = visual_canvas
        self.aura_item = aura_item
        self.status_label = status_label
        self.focused = False
        self.float_offset = 0
        self.direction = 1
        self.current_visual_text = "💡 Idle Visual"
        self.visual_label = None
        self.init_label()
        # start animations on the main thread
        self.root.after(0, self.animate_aura)
        self.root.after(0, self.animate_visuals)

    # Aura pulse animation (runs on main thread via after)
    def animate_aura(self):
        try:
            color = "#00ffdd" if not self.focused else "#ffdd00"
            self.visual_canvas.itemconfig(self.aura_item, outline=color)
            width = random.randint(2, 5)
            self.visual_canvas.itemconfig(self.aura_item, width=width)
        except Exception:
            pass
        self.root.after(500, self.animate_aura)

    # Floating visual up/down
    def animate_visuals(self):
        try:
            self.float_offset += self.direction * 2
            if abs(self.float_offset) > 20:
                self.direction *= -1
            self.visual_canvas.coords(
                self.visual_label, 200, 100 + self.float_offset)
        except Exception:
            pass
        self.root.after(50, self.animate_visuals)

    # Update floating visual text (safe to call from main thread only)
    def update_visual(self, text: str):
        self.current_visual_text = text
        try:
            self.visual_canvas.itemconfig(self.visual_label, text=text)
        except Exception:
            pass

    # Set EI focus state
    def set_focus(self, focused: bool):
        self.focused = focused
        try:
            self.status_label.config(
                text="Status: Focused" if focused else "Status: Calm")
        except Exception:
            pass

    # Initialize label
    def init_label(self):
        # create_text returns an item id
        self.visual_label = self.visual_canvas.create_text(
            200, 100, text=self.current_visual_text, fill="#00ffdd", font=("Arial", 16)
        )


# -------------------------
# Aurora GUI with Cinematic Logo Intro
# -------------------------
class AuroraGUI:
    def __init__(self, avatar: Any):
        self.avatar = avatar
        self.voice_engine = VoiceEngine()          # Read aloud engine (optional)
        self.memory = MemoryStore()                # Memory tracking
        self.last_user_input = ""
        self.last_avatar_response = ""
        self._metrics_running = False

        # Root window
        self.root = tk.Tk()
        self.root.title("Etherea – Adaptive Workspace 🌟")
        self.root.geometry("1024x768")
        self.root.configure(bg="#1e1e2f")  # dark futuristic background

        # Intro canvas
        self.intro_canvas = tk.Canvas(
            self.root, width=1024, height=768, bg="#1e1e2f", highlightthickness=0)
        self.intro_canvas.place(x=0, y=0)

        self.intro_aura = self.intro_canvas.create_oval(
            412, 284, 612, 484, outline="#00ffdd", width=4)
        self.logo_square = self.intro_canvas.create_rectangle(
            450, 320, 574, 444, outline="#ffffff", width=3)
        self.logo_brain = self.intro_canvas.create_oval(
            460, 330, 564, 438, outline="#00ffdd", width=2)

        # Start intro
        self.root.after(100, self.run_intro)

    # ---------------- Cinematic Intro Animation ----------------
    def run_intro(self):
        # run short animation (blocking here is ok because it's the intro)
        for i in range(30):
            offset = 5 + i
            try:
                self.intro_canvas.coords(
                    self.intro_aura, 412 - offset, 284 - offset, 612 + offset, 484 + offset)
                color = "#00ffdd" if i % 2 == 0 else "#00ffff"
                self.intro_canvas.itemconfig(
                    self.intro_aura, outline=color, width=2 + i // 10)
                scale = 1 + i * 0.01
                self.scale_item(self.logo_square, 512, 384, scale)
                self.scale_item(self.logo_brain, 512, 384, scale)
            except Exception:
                pass
            self.root.update()
            time.sleep(0.03)

        # Fade intro
        for alpha in range(20, -1, -1):
            try:
                val = max(0, min(255, alpha * 12))
                color_val = f"#{val:02x}{val:02x}{val:02x}"
                self.intro_canvas.configure(bg=color_val)
            except Exception:
                pass
            self.root.update()
            time.sleep(0.02)

        # Destroy intro and init workspace
        try:
            self.intro_canvas.destroy()
        except Exception:
            pass
        self.init_workspace()

    # ---------------- Utility: Scale a canvas item ----------------
    def scale_item(self, item: int, cx: float, cy: float, scale: float):
        try:
            coords = self.intro_canvas.coords(item)
            if len(coords) >= 4:
                x0, y0, x1, y1 = coords[:4]
                new_coords = [
                    cx + (x0 - cx) * scale,
                    cy + (y0 - cy) * scale,
                    cx + (x1 - cx) * scale,
                    cy + (y1 - cy) * scale
                ]
                self.intro_canvas.coords(item, *new_coords)
        except Exception:
            pass

    # ---------------- Initialize Workspace ----------------
    def init_workspace(self):
        # Left Panel (Avatar + Aura)
        self.left_panel = tk.Canvas(
            self.root, width=200, height=200, bg="#1e1e2f", highlightthickness=0)
        self.left_panel.place(x=20, y=20)

        self.avatar_label = Label(self.left_panel, text="💫 Avatar", fg="#ffffff", bg="#1e1e2f",
                                  font=("Arial", 16, "bold"))
        self.avatar_label.place(x=30, y=20)

        self.status_label = Label(self.left_panel, text="Status: Calm", fg="#00ffdd", bg="#1e1e2f",
                                  font=("Arial", 12, "italic"))
        self.status_label.place(x=20, y=60)

        self.aura_item = self.left_panel.create_oval(
            10, 10, 180, 180, outline="#00ffdd", width=4)

        # Main Workspace Panel
        self.workspace = scrolledtext.ScrolledText(self.root, width=80, height=15, font=("Consolas", 12),
                                                   bg="#2e2e3e", fg="#f0f0f0")
        self.workspace.place(x=240, y=20)

        # Floating visuals canvas
        self.visual_canvas = tk.Canvas(
            self.root, width=400, height=200, bg="#2e2e3e", highlightthickness=0)
        self.visual_canvas.place(x=240, y=320)

        # Input box
        self.user_input_var = tk.StringVar()
        self.input_box = Entry(self.root, textvariable=self.user_input_var, font=("Consolas", 12),
                               bg="#2e2e3e", fg="#f0f0f0")
        self.input_box.place(x=240, y=650, width=600)
        self.input_box.bind("<Return>", self.submit_input)

        # Response box
        self.response_box = scrolledtext.ScrolledText(self.root, width=80, height=5, font=("Consolas", 12),
                                                      bg="#2e2e3e", fg="#a0ffa0")
        self.response_box.place(x=240, y=520)

        # Feedback Buttons Frame (below response_box)
        self.button_frame = Frame(self.root, bg="#1e1e2f")
        self.button_frame.place(x=240, y=595, width=600, height=40)

        # Buttons
        self.read_button = Button(self.button_frame, text="🔊 Read Aloud", command=self.read_aloud, bg="#00ffdd",
                                  fg="#1e1e2f")
        self.read_button.pack(side="left", padx=5, pady=5)

        self.regen_button = Button(self.button_frame, text="🔄 Regenerate", command=self.regenerate_response,
                                   bg="#ffdd00", fg="#1e1e2f")
        self.regen_button.pack(side="left", padx=5, pady=5)

        self.thumb_up_button = Button(self.button_frame, text="👍", command=lambda: self.send_feedback(True),
                                      bg="#00ffaa", fg="#1e1e2f")
        self.thumb_up_button.pack(side="left", padx=5, pady=5)

        self.thumb_down_button = Button(self.button_frame, text="👎", command=lambda: self.send_feedback(False),
                                        bg="#ff5555", fg="#1e1e2f")
        self.thumb_down_button.pack(side="left", padx=5, pady=5)

        # EI Label
        self.ei_label = Label(self.root, text="EI State: Neutral", bg="#1e1e2f", fg="#a0a0ff",
                              font=("Consolas", 12))
        self.ei_label.place(x=20, y=240)

        # Visuals & Animations
        self.visuals = Visuals(self.root, self.visual_canvas,
                               self.aura_item, self.status_label)

        # Intro finished message
        self.workspace.insert(
            tk.END, "Workspace ready. Start typing commands...\n")
        self.root.update()

        # Start periodic EI/metrics updates
        self._metrics_running = True
        self.root.after(1000, self._metrics_loop)

    # ---------------- User Input ----------------
    def get_user_input(self) -> str:
        self.root.update()
        return self.user_input_var.get()

    def submit_input(self, event=None):
        user_text = self.user_input_var.get()
        if user_text.strip() != "":
            # append user input to workspace (main thread)
            self.last_user_input = user_text
            self.workspace.insert(tk.END, f"User: {user_text}\n")
            self.user_input_var.set("")
            # start worker thread to generate response
            threading.Thread(target=self._background_generate,
                             args=(user_text,), daemon=True).start()

    # ---------------- Avatar Integration (thread-safe) ----------------
    def _background_generate(self, user_text: str):
        """
        Worker thread: calls avatar (generate_response or speak),
        then schedules UI update on main thread.
        """
        try:
            if hasattr(self.avatar, "generate_response"):
                response = self.avatar.generate_response(user_text)
            elif hasattr(self.avatar, "speak"):
                response = self.avatar.speak(user_text)
            else:
                response = "Avatar has no response method."
        except Exception as e:
            response = f"[Error generating response: {e}]"

        # schedule UI update on main thread
        self.root.after(
            0, lambda: self._handle_response_ui(response, user_text))

    def _handle_response_ui(self, response: str, user_text: str):
        # update last response and UI widgets (main thread only)
        self.last_avatar_response = response
        self.response_box.insert(tk.END, f"{response}\n")
        self.response_box.see(tk.END)

        # update workspace log too (optional)
        try:
            self.workspace.insert(tk.END, f"AI: {response}\n")
            self.workspace.see(tk.END)
        except Exception:
            pass

        # Visuals: request a visual text from avatar if available
        try:
            if hasattr(self.avatar, "get_visual_for_response"):
                visual_text = self.avatar.get_visual_for_response(response)
            else:
                visuals = ["💡 Lightbulb", "🔥 Focus Flame",
                           "🧘 Relax Aura", "⚡ Energy Pulse"]
                visual_text = random.choice(visuals)
        except Exception:
            visual_text = "💡 Idle Visual"

        # schedule visual update on main thread
        try:
            self.visuals.update_visual(visual_text)
        except Exception:
            pass

        # Optionally save interaction to memory (non-blocking)
        try:
            data = self.memory.load()
            interactions = data.get("interactions", [])
            interactions.append({"user": user_text, "bot": response,
                                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")})
            self.memory.update_key("interactions", interactions)
        except Exception:
            pass

    # ---------------- Voice & Buttons ----------------
    def read_aloud(self):
        if not self.last_avatar_response:
            return
        # get EI state (can be string or dict)
        ei_state = None
        try:
            if hasattr(self.avatar, "get_current_ei_state"):
                ei_state = self.avatar.get_current_ei_state()
            # normalize to dict expected by voice_engine (tone/intensity)
            if isinstance(ei_state, str):
                ei_state = {"tone": ei_state.lower(), "intensity": 0.6}
            elif isinstance(ei_state, dict):
                pass
            else:
                ei_state = {"tone": "neutral", "intensity": 0.5}
        except Exception:
            ei_state = {"tone": "neutral", "intensity": 0.5}

        # speak in worker thread (pyttsx3 is blocking)
        threading.Thread(target=self.voice_engine.speak, args=(
            self.last_avatar_response, ei_state), daemon=True).start()

    def regenerate_response(self):
        if not self.last_user_input:
            return
        # regenerate by running background generate with last user input
        threading.Thread(target=self._background_generate, args=(
            self.last_user_input,), daemon=True).start()

    def send_feedback(self, positive: bool):
        feedback_entry = {
            "session_id": 1,
            "response": self.last_avatar_response,
            "positive": bool(positive),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
        }
        # store feedback in memory (calls are quick; keep on main thread)
        try:
            data = self.memory.load()
            feedback_list = data.get("feedback", [])
            feedback_list.append(feedback_entry)
            self.memory.update_key("feedback", feedback_list)
        except Exception:
            pass
        # small UI ack
        try:
            self.response_box.insert(
                tk.END, f"[Feedback {'👍' if positive else '👎'} recorded]\n")
            self.response_box.see(tk.END)
        except Exception:
            pass

    # ---------------- EI / Metrics Loop ----------------
    def _metrics_loop(self):
        try:
            if hasattr(self.avatar, "get_current_ei_state"):
                ei_state = self.avatar.get_current_ei_state()
                # normalize for display
                if isinstance(ei_state, dict):
                    label = ei_state.get("tone", "Neutral").capitalize()
                else:
                    label = str(ei_state).capitalize()
                self.ei_label.config(text=f"EI State: {label}")

                color_map = {"neutral": "#00ffdd",
                             "focused": "#ffdd00", "excited": "#ff00ff"}
                color = color_map.get(label.lower(), "#00ffdd")
                self.visuals.focused = label.lower() == "focused"
                try:
                    self.visual_canvas.itemconfig(
                        self.visuals.visual_label, fill=color)
                except Exception:
                    pass
        except Exception:
            pass

        # schedule next run
        if self._metrics_running:
            self.root.after(1500, self._metrics_loop)

    # ---------------- Run GUI ----------------
    def run(self):
        try:
            self.root.mainloop()
        finally:
            self._metrics_running = False


# -------------------------
# Example usage (test without AI)
# -------------------------
if __name__ == "__main__":
    class DummyAvatar:
        def load_onboarding_data(self):
            pass

        def generate_response(self, text: str) -> str:
            return f"Avatar says: {text[::-1]}"

        def get_visual_for_response(self, response: str) -> str:
            visuals = ["💡 Lightbulb", "🔥 Focus Flame",
                       "🧘 Relax Aura", "⚡ Energy Pulse"]
            return random.choice(visuals)

        def get_current_ei_state(self):
            # return either a string or dict — both are supported by the GUI
            return random.choice(["Neutral", "Focused", "Excited"])

    avatar = DummyAvatar()
    gui = AuroraGUI(avatar)
    gui.run()
