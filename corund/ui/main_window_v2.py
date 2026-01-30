from __future__ import annotations

from corund.ui.command_palette import CommandPalette
from corund.workspace_ai.workspace_controller import WorkspaceController

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QFrame,
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QFrame,
)

from corund.ui.command_palette import CommandPalette
from corund.ui.avatar_heroine_widget import AvatarHeroineWidget
from corund.ui.aurora_canvas_widget import AuroraCanvasWidget

from corund.gestures.gesture_engine import GestureEngine
from corund.gestures.presets import regression_preset
from corund.behavior.behavior_planner import plan_behavior
from corund.avatar_motion.motion_controller import AvatarMotionController
from corund.ui.beat_sync import BeatSyncScheduler
from corund.audio_analysis.beat_detector import estimate_bpm_and_beats
from corund.audio_analysis.song_resolver import resolve_song
from corund.audio_analysis.beat_to_ui import beats_to_ui_effects
from corund.aurora_actions import ActionRegistry
from corund.aurora_pipeline import AuroraDecisionPipeline
from corund.aurora_state import AuroraStateStore
from corund.workspace_manager import WorkspaceManager
from corund.workspace_registry import WorkspaceRegistry
from corund.os_adapter import OSAdapter
from corund.os_pipeline import OSPipeline


def _etherea_ui_log(msg: str):
    try:
        with open("etherea_boot.log", "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception:
        pass
from corund.workspace_ai.workspace_controller import WorkspaceController
from corund.workspace_manager import WorkspaceManager
from corund.workspace_registry import WorkspaceRegistry
from corund.aurora_actions import ActionRegistry
from corund.aurora_pipeline import AuroraDecisionPipeline
from corund.aurora_state import AuroraStateStore

# ðŸ§  AppState drives expressive_mode ("dance"/"humming"/"idle") used by AvatarHeroineWidget
try:
    from corund.state import AppState
except Exception:
    AppState = None

# optional gesture / beat sync extras (kept safe)
try:
    from corund.gestures.gesture_engine import GestureEngine
    from corund.gestures.presets import regression_preset
except Exception:
    GestureEngine = None
    regression_preset = None

try:
    from corund.ui.beat_sync import BeatSyncScheduler
except Exception:
    BeatSyncScheduler = None

try:
    from corund.voice_engine import get_voice_engine
except Exception:
    get_voice_engine = None

# âœ… Use existing agent brain + optional FocusGuardian supervisor
try:
    from corund.agent import IntelligentAgent, FocusGuardian
except Exception:
    IntelligentAgent = None
    FocusGuardian = None

# signals are optional; window still runs without them
try:
    from corund.signals import signals
except Exception:
    signals = None


def _etherea_ui_log(msg: str) -> None:
    try:
        with open("etherea_boot.log", "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception:
        pass


class EthereaMainWindowV2(QMainWindow):
    """
    Hero demo window:
      - Avatar + Aurora + Console
      - Single command pipeline (typed + voice) -> WorkspaceController.handle_command()
      - Mode layout switching (study/coding/exam/calm/deep_work)
      - Focus timer UI + avatar persona hint
      - Voice: push-to-talk + optional wake loop

    Spice layer:
      - Presenter mode (ambient pulses, alive UI)
      - Co-present script: avatar speaks short lines that complement YOU
        Commands: present on/off, co-present, next, skip
      - Avatar commands: dance / hum / surprise (always work)
    """

    def __init__(self) -> None:
        super().__init__()
        _etherea_ui_log("UI: EthereaMainWindowV2 created")
        self.setWindowTitle("Etherea OS â€” Heroine Avatar v2")
        self.resize(1200, 720)

        root = QWidget()
        self.setCentralWidget(root)

        main = QHBoxLayout(root)
        main.setContentsMargins(14, 14, 14, 14)
        main.setSpacing(12)

        # ---- Core managers ----
        self.workspace_manager = WorkspaceManager()
        self.ws_controller = WorkspaceController(self.workspace_manager)

        self.workspace_registry = WorkspaceRegistry()
        self.action_registry = ActionRegistry.default()
        self.aurora_state_store = AuroraStateStore(self.action_registry)
        self.aurora_pipeline = AuroraDecisionPipeline(
            registry=self.action_registry,
            workspace_registry=self.workspace_registry,
            workspace_manager=self.workspace_manager,
            state_store=self.aurora_state_store,
            log_cb=self.log,
        )

        # ---- LEFT: Command + Avatar ----
        left = QVBoxLayout()
        left.setSpacing(10)

        self.command_palette = CommandPalette()
        self.command_palette.submitted.connect(lambda cmd: self.execute_user_command(cmd, source="ui"))

        self.avatar = AvatarHeroineWidget()
        self.avatar.setStyleSheet("""
            QWidget { background: #0b0b12; border-radius: 18px; }
        """)
        self.aurora_ring = self.avatar
        left.addWidget(self.command_palette)
        left.addWidget(self.avatar, 1)

        self.gestures = GestureEngine(self.avatar, on_log=self.log)
        self.motion = AvatarMotionController()
        self.beatsync = BeatSyncScheduler(self._apply_ui_effect, log_cb=self.log)
        self.workspace_manager = WorkspaceManager()
        self.ws_controller = WorkspaceController(self.workspace_manager)
        self.workspace_registry = WorkspaceRegistry()
        self.os_pipeline = OSPipeline(OSAdapter(dry_run=False))
        self.action_registry = ActionRegistry.default()
        self.aurora_state_store = AuroraStateStore(self.action_registry)
        self.aurora_pipeline = AuroraDecisionPipeline(
            registry=self.action_registry,
            workspace_registry=self.workspace_registry,
            workspace_manager=self.workspace_manager,
            state_store=self.aurora_state_store,
            os_pipeline=self.os_pipeline,
            log_cb=self.log,
        )

        # Controls row
        self.avatar.setStyleSheet("QWidget { background: #0b0b12; border-radius: 18px; }")
        self.aurora_ring = self.avatar  # ring FX exposed by avatar widget

        controls = QHBoxLayout()

        self.btn_voice = QPushButton("ðŸŽ™ï¸ Voice (push)")
        self.btn_demo = QPushButton("Demo: Regression")
        self.btn_theme = QPushButton("Theme: Dark/Light")
        self.btn_accent = QPushButton("Accent: Violet/Blue")
        self.btn_present = QPushButton("ðŸŽ¥ Present")
        self.btn_copresent = QPushButton("ðŸ¤ Co-present")

        self.btn_voice.clicked.connect(self._voice_push_to_talk)
        self.btn_demo.clicked.connect(self.run_regression_demo)
        self.btn_theme.clicked.connect(self.toggle_theme)
        self.btn_accent.clicked.connect(self.toggle_accent)
        self.btn_present.clicked.connect(self.toggle_presenter_mode)
        self.btn_copresent.clicked.connect(self.start_copresent)

        controls.addWidget(self.btn_voice)
        controls.addWidget(self.btn_demo)
        controls.addWidget(self.btn_theme)
        controls.addWidget(self.btn_accent)
        controls.addWidget(self.btn_present)
        controls.addWidget(self.btn_copresent)

        left.addWidget(self.command_palette)
        left.addWidget(self.avatar, 1)
        left.addLayout(controls)

        # ---- RIGHT: Aurora + Console + Status ----
        right = QVBoxLayout()
        right.setSpacing(10)

        title = QLabel("Etherea Console")
        title.setStyleSheet("font-size:18px; font-weight:700; color:white;")
        right.addWidget(title)

        self.aurora_canvas = AuroraCanvasWidget()
        self.aurora_canvas.intent_requested.connect(self._on_aurora_intent)
        self.aurora_state_store.subscribe(self.aurora_canvas.apply_state)
        right.addWidget(self.aurora_canvas)

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet(
            "QTextEdit { background:#11121a; color:#e8e8ff; border:1px solid #22243a;"
            "border-radius:14px; padding:10px; font-family:monospace; font-size:13px; }"
        )
        right.addWidget(self.console, 1)

        status = QFrame()
        status.setStyleSheet(
            "QFrame { background:#101018; border:1px solid #1f2135; border-radius:16px; padding:10px; }"
            "QLabel { color:#dcdcff; font-size:13px; }"
        )
        s = QVBoxLayout(status)

        self.l_mode = QLabel("Mode: study")
        self.l_focus = QLabel("Focus: --")
        self.l_stress = QLabel("Stress: --")
        self.l_energy = QLabel("Energy: --")
        self.l_timer = QLabel("Focus timer: --")

        s.addWidget(self.l_mode)
        s.addWidget(self.l_timer)
        s.addWidget(self.l_focus)
        s.addWidget(self.l_stress)
        s.addWidget(self.l_energy)
        right.addWidget(status)

        main.addLayout(left, 1)
        main.addLayout(right, 2)

        # ---- optional gesture / beat extras ----
        self.gestures = None
        if GestureEngine is not None:
            try:
                self.gestures = GestureEngine(self.avatar, on_log=self.log)
            except Exception:
                self.gestures = None

        self.beatsync = None
        if BeatSyncScheduler is not None:
            try:
                self.beatsync = BeatSyncScheduler(self._apply_ui_effect, log_cb=self.log)
            except Exception:
                self.beatsync = None

        # ---- internal UI state ----
        self._theme_is_dark = True
        self._accent_alt = False
        self._current_mode = "study"

        # ---- Presenter state ----
        self._presenter_on = False
        self._copresent_queue = []
        self._copresent_idx = 0

        # ---- focus timer tick ----
        self._focus_timer_tick = QTimer(self)
        self._focus_timer_tick.setInterval(1000)
        self._focus_timer_tick.timeout.connect(self._tick_focus)
        self._focus_timer_tick.start()

        # ---- ambient presenter tick (always running but only animates when presenter ON) ----
        self._ambient_tick = QTimer(self)
        self._ambient_tick.setInterval(1100)
        self._ambient_tick.timeout.connect(self._presenter_ambient_tick)
        self._ambient_tick.start()

        # ---- signal wiring ----
        if signals is not None:
            try:
                if hasattr(signals, "emotion_updated"):
                    signals.emotion_updated.connect(self.on_emotion_updated)
                if hasattr(signals, "command_received_ex"):
                    signals.command_received_ex.connect(self._on_command_ex)
                elif hasattr(signals, "command_received"):
                    signals.command_received.connect(lambda cmd: self.execute_user_command(cmd, source="voice"))
                if hasattr(signals, "mode_changed"):
                    signals.mode_changed.connect(self._on_mode_changed_signal)
                if hasattr(signals, "focus_started"):
                    signals.focus_started.connect(self._on_focus_started_signal)
                if hasattr(signals, "focus_stopped"):
                    signals.focus_stopped.connect(self._on_focus_stopped_signal)
                if hasattr(signals, "voice_state"):
                    signals.voice_state.connect(self._on_voice_state)
            except Exception:
                pass

        self.log_ui("âœ… Heroine avatar online (Disney-like 2.5D).")
        self.log_ui("ðŸŽ­ Smooth blink + breathing + glow aura + calm motion.")
        self.log_ui("ðŸ”— EI signals: " + ("connected" if signals is not None else "not found (still OK)"))
        self._sync_aurora_state()

    def log_ui(self, msg: str) -> None:
        self.console.append(msg)

    def log(self, msg: str) -> None:
        if signals is not None and hasattr(signals, "system_log"):
            try:
                signals.system_log.emit(msg)
                return
            except Exception:
                pass
        self.log_ui(msg)

    def _sync_aurora_state(self) -> None:
        current = self.workspace_registry.get_current()
        emotion_tag = getattr(self.avatar, "emotion_tag", "calm")
        self.aurora_state_store.update(
            workspace_id=current.workspace_id if current else None,
            workspace_name=current.name if current else None,
            session_active=current is not None,
            last_saved=current.last_saved if current else None,
            emotion_tag=emotion_tag,
        )

    def _update_aurora_from_ei(self, vec: dict) -> None:
        emotion_tag = getattr(self.avatar, "emotion_tag", "calm")
        self.aurora_state_store.update(
            focus=float(vec.get("focus", 0.4)),
            stress=float(vec.get("stress", 0.2)),
            energy=float(vec.get("energy", 0.6)),
            emotion_tag=emotion_tag,
        )

    def _on_aurora_intent(self, action_id: str) -> None:
        result = self.aurora_pipeline.handle_intent(action_id)
        self.log(f"ðŸŒŒ Aurora action: {result}")
        # ---- voice engine instance ----
        self.voice_engine = None
        if get_voice_engine is not None:
            try:
                self.voice_engine = get_voice_engine()
            except Exception:
                self.voice_engine = None

        # ---- start wake loop (optional) ----
        if self.voice_engine is not None:
            try:
                self.voice_engine.start_wake_word_loop()
                self.log("ðŸŽ™ï¸ Voice wake loop armed (say: 'Etherea ...').")
            except Exception as e:
                self.log(f"âš ï¸ Voice wake loop not started: {e}")
        else:
            self.log("ðŸŽ™ï¸ Voice engine not available (still OK).")

        # ---- Agent brain + FocusGuardian supervisor (optional-safe) ----
        self.agent = None
        if IntelligentAgent is not None:
            try:
                self.agent = IntelligentAgent()
                self.log("ðŸ§  IntelligentAgent ready (Plan â†’ Execute â†’ Observe â†’ Verify).")
            except Exception as e:
                self.log(f"âš ï¸ IntelligentAgent init failed: {e}")

        self.guardian = None
        if FocusGuardian is not None:
            try:
                self.guardian = FocusGuardian(self.ws_controller, voice_engine=self.voice_engine, log_cb=self.log)
                self.guardian.start()
            except Exception as e:
                self.log(f"âš ï¸ FocusGuardian failed: {e}")

        # ---- boot logs ----
        self.log_ui("ðŸŽ‚ Etherea Birthday Build â€” presenter spice online.")
        self.log_ui("âœ… Commands: present on/off | co-present | next | skip | dance | hum | surprise")
        self._sync_aurora_state()

    # -------------------------
    # Logging
    # -------------------------
    def log_ui(self, msg: str) -> None:
        self.console.append(msg)

    def log(self, msg: str) -> None:
        if signals is not None and hasattr(signals, "system_log"):
            try:
                signals.system_log.emit(msg)
                return
            except Exception:
                pass
        self.log_ui(msg)

    # -------------------------
    # Presenter Mode (Spice)
    # -------------------------
    def toggle_presenter_mode(self, force: Optional[bool] = None) -> None:
        if force is None:
            self._presenter_on = not self._presenter_on
        else:
            self._presenter_on = bool(force)

        state = "ON" if self._presenter_on else "OFF"
        self.log(f"ðŸŽ¥ Presenter mode: {state}")

        try:
            self.aurora_ring.pulse(intensity=1.25 if self._presenter_on else 1.05, duration=0.28)
        except Exception:
            pass

    def _presenter_ambient_tick(self) -> None:
        if not self._presenter_on:
            return
        try:
            self.aurora_ring.pulse(intensity=1.12, duration=0.20)
        except Exception:
            pass

    def start_copresent(self) -> None:
        self.toggle_presenter_mode(force=True)

        self._copresent_queue = [
            ("greet", "Hi Professor. Iâ€™m Etherea â€” a desktop-first living OS. Bru and I will co-present today."),
            ("overview", "My core loop is: sense, decide, adapt. The user stays in control with explicit modes."),
            ("avatar", "Iâ€™m the emotional interface. I react to context without taking silent control."),
            ("workspace", "The workspace stays task-focused: study, coding, and exam modes. Exam mode minimizes distractions."),
            ("demo", "We can trigger visible behavior: dance for expressiveness, surprise for UI effects, and voice for hands-free commands."),
            ("close", "Goal: a comfortable, human-feeling desktop companion that improves productivity and reduces cognitive load."),
        ]
        self._copresent_idx = 0
        self.log("ðŸ¤ Co-present started. Use: next / skip")
        self._copresent_say_current()

    def _copresent_say_current(self) -> None:
        if not self._copresent_queue:
            self.log("ðŸ¤ Co-present queue empty.")
            return
        if self._copresent_idx < 0 or self._copresent_idx >= len(self._copresent_queue):
            self.log("ðŸ¤ Co-present finished.")
            return

        tag, line = self._copresent_queue[self._copresent_idx]
        self.log(f"ðŸ¤ [{tag.upper()}] {line}")

        try:
            if self.voice_engine is not None:
                self.voice_engine.speak(line, language="en-IN")
        except Exception:
            pass

        try:
            self.aurora_ring.pulse(intensity=1.35, duration=0.32)
        except Exception:
            pass

    def _copresent_next(self) -> None:
        if not self._copresent_queue:
            self.log("ðŸ¤ No co-present running.")
            return
        self._copresent_idx += 1
        if self._copresent_idx >= len(self._copresent_queue):
            self.log("ðŸ¤ Co-present finished. Presenter mode stays ON.")
            return
        self._copresent_say_current()

    def _copresent_skip(self) -> None:
        if not self._copresent_queue:
            self.log("ðŸ¤ No co-present running.")
            return
        self.log("â­ï¸ Skipped.")
        self._copresent_next()

    # -------------------------
    # Avatar expressive control
    # -------------------------
    def _set_expressive_mode(self, mode: str) -> None:
        if AppState is None:
            self.log("âš ï¸ AppState not available; expressive animations not wired.")
            return
        try:
            AppState.instance().set_expressive_mode(mode)
            self.log(f"âœ¨ Avatar expressive_mode â†’ {mode}")
            try:
                self.aurora_ring.pulse(intensity=1.45, duration=0.28)
            except Exception:
                pass
        except Exception as e:
            self.log(f"âš ï¸ set_expressive_mode failed: {e}")

    def _handle_avatar_commands(self, cmd: str) -> bool:
        low = (cmd or "").strip().lower()

        # Dance
        if low in ("dance", "start dance", "dance mode", "avatar dance"):
            self._set_expressive_mode("dance")
            return True
        if low in ("stop dance", "dance off", "end dance"):
            self._set_expressive_mode("idle")
            return True

        # Humming
        if low in ("hum", "humming", "start hum", "start humming", "avatar hum"):
            self._set_expressive_mode("humming")
            return True
        if low in ("stop hum", "stop humming", "hum off"):
            self._set_expressive_mode("idle")
            return True

        # Surprise
        if low in ("surprise", "avatar surprise", "magic", "sparkle"):
            try:
                if hasattr(self.avatar, "perform_gesture"):
                    self.avatar.perform_gesture("summon")
                self.log("ðŸŽ‡ Surprise triggered (summon + glow).")
                try:
                    self.aurora_ring.pulse(intensity=1.8, duration=0.40)
                except Exception:
                    pass
                try:
                    self.aurora_ring.pulse(intensity=1.25, duration=0.18)
                except Exception:
                    pass
            except Exception as e:
                self.log(f"âš ï¸ Surprise failed: {e}")
            return True

        # Presenter commands
        if low in ("present on", "present", "presenter on", "presentation on"):
            self.toggle_presenter_mode(force=True)
            return True
        if low in ("present off", "presenter off", "presentation off"):
            self.toggle_presenter_mode(force=False)
            return True
        if low in ("co-present", "copresent", "present with me", "start presentation"):
            self.start_copresent()
            return True
        if low in ("next", "next point", "continue"):
            self._copresent_next()
            return True
        if low in ("skip", "skip point"):
            self._copresent_skip()
            return True

        return False

    # -------------------------
    # Aurora state
    # -------------------------
    def _sync_aurora_state(self) -> None:
        current = self.workspace_registry.get_current()
        emotion_tag = getattr(self.avatar, "emotion_tag", "calm")
        self.aurora_state_store.update(
            current_mode=self._current_mode,
            workspace_id=current.workspace_id if current else None,
            workspace_name=current.name if current else None,
            session_active=current is not None,
            last_saved=current.last_saved if current else None,
            emotion_tag=emotion_tag,
        )

    def _update_aurora_from_ei(self, vec: dict) -> None:
        emotion_tag = getattr(self.avatar, "emotion_tag", "calm")
        try:
            self.aurora_state_store.update(
                focus=float(vec.get("focus", 0.4)),
                stress=float(vec.get("stress", 0.2)),
                energy=float(vec.get("energy", 0.6)),
                emotion_tag=emotion_tag,
            )
        except Exception:
            pass

    def _on_aurora_intent(self, action_id: str) -> None:
        result = self.aurora_pipeline.handle_intent(action_id)
        self.log(f"ðŸŒŒ Aurora action: {result}")

    # -------------------------
    # Theme / Accent
    # -------------------------
    def toggle_theme(self) -> None:
        self._theme_is_dark = not self._theme_is_dark
        try:
            self.avatar.set_theme_mode("dark" if self._theme_is_dark else "light")
        except Exception:
            pass
        self.log(f"ðŸŽ¨ Theme switched â†’ {'dark' if self._theme_is_dark else 'light'}")

    def toggle_accent(self) -> None:
        self._accent_alt = not self._accent_alt
        try:
            if self._accent_alt:
                self.avatar.set_accent_colors((120, 220, 255), (120, 255, 210))
                self.log("ðŸ’  Accent switched â†’ cyan/teal")
            else:
                self.avatar.set_accent_colors((160, 120, 255), (255, 210, 120))
                self.log("ðŸ’œ Accent switched â†’ violet/gold")
        except Exception:
            pass

    # -------------------------
    # EI updates
    # -------------------------
    def on_emotion_updated(self, vec: dict) -> None:
        f = vec.get("focus", None)
        s = vec.get("stress", None)
        e = vec.get("energy", None)

        if isinstance(f, (int, float)):
            self.l_focus.setText(f"Focus: {float(f):.2f}")
        if isinstance(s, (int, float)):
            self.l_stress.setText(f"Stress: {float(s):.2f}")
        if isinstance(e, (int, float)):
            self.l_energy.setText(f"Energy: {float(e):.2f}")
        if isinstance(c, (int, float)):
            self.l_curiosity.setText(f"Curiosity: {float(c):.2f}")
        self._update_aurora_from_ei(vec)

        self._update_aurora_from_ei(vec)

        try:
            self.avatar.update_ei(vec)
        except Exception:
            pass

    # -------------------------
    # Demo gesture preset
    # -------------------------
    def run_regression_demo(self) -> None:
        if self.gestures is None or regression_preset is None:
            self.log("ðŸ“š Demo not available in this build (still OK).")
            return
        self.log("ðŸ“š Demo: Explaining regression (gestures + ring FX).")
        plan = regression_preset()
        self.gestures.play(plan)
        # ðŸ’« Beat-synced ring effects (real-time)
        try:
            self.beatsync.load(plan.get('ui_effects') or [])
            self.beatsync.start()
        except Exception as _:
            pass

        # NEW: if dance requested, generate an original routine
        d = plan.get('dance')
        if d:
            self.motion.play_dance(
                duration_s=float(d.get('duration_s', 18.0)),
                bpm=float(d.get('bpm', 128.0)),
                style=str(d.get('style', 'bolly_pop')),
                energy=1.25
            )

        m = plan.get('motion') or {}
        clip = m.get('clip', 'idle_breathe_01')
        intensity = float(m.get('intensity', 1.0))
        loop = bool(m.get('loop', True))
        self.motion.play(clip, intensity=intensity, loop=loop)


    def speak_and_perform(self, text: str, language: str = "en"):
        """Speak + run gesture timeline based on behavior planner."""
        try:
            plan = regression_preset()
            self.gestures.play(plan)
            if self.beatsync is not None:
                try:
                    self.beatsync.load(plan.get("ui_effects") or [])
                    self.beatsync.start()
                except Exception:
                    pass
        except Exception as e:
            self.log(f"âš ï¸ Regression demo failed: {e}")

    def _apply_ui_effect(self, effect: dict) -> None:
        etype = effect.get("type")
        if etype == "ring_pulse":
            intensity = float(effect.get("intensity", 1.2))
            dur = float(effect.get("dur", 0.2))
            try:
                self.aurora_ring.pulse(intensity=intensity, duration=dur)
            except Exception:
                pass

    # -------------------------
    # Voice
    # -------------------------
    def _voice_push_to_talk(self) -> None:
        if self.voice_engine is None:
            self.log("ðŸŽ™ï¸ Voice engine not installed/available (still OK).")
            return

        def worker():
            ve = self.voice_engine
            if ve is None:
                self.log("ðŸŽ™ï¸ Voice engine unavailable.")
                return
            if not getattr(ve, "has_mic", False):
                self.log("ðŸŽ™ï¸ No microphone detected.")
                return
            self.log("ðŸŽ™ï¸ Listening (push)â€¦")
            text = ve.listen_once(timeout_s=5, phrase_limit_s=10)
            if not text:
                self.log("ðŸŽ™ï¸ Heard nothing.")
                return

            low = text.lower()
            cmd = text
            for w in ("etherea", "ethera"):
                if w in low:
                    cmd = low.split(w, 1)[1].strip(" ,.!:;") or "hello etherea"
                    break

            self.execute_user_command(cmd, source="voice")
            try:
                ve.speak("Done.", language="en-IN")
            except Exception:
                pass

        threading.Thread(target=worker, daemon=True).start()

    def _on_voice_state(self, state: str, meta: dict) -> None:
        if state == "LISTENING":
            self.log("ðŸŽ™ï¸ Voice: LISTENING")
        elif state == "THINKING":
            self.log("ðŸ§  Voice: THINKING")

    # -------------------------
    # Unified command pipeline
    # -------------------------
    def _on_command_ex(self, text: str, meta: dict) -> None:
        source = str((meta or {}).get("source", "voice"))
        self.execute_user_command(text, source=source)

    def execute_user_command(self, cmd: str, *, source: str = "ui") -> None:
        cmd = (cmd or "").strip()
        if not cmd:
            return

        self.log(f"âš¡ CMD[{source}]: {cmd}")

        # âœ… avatar/presenter commands always handled here
        if self._handle_avatar_commands(cmd):
            self._sync_aurora_state()
            return

        try:
            out = self.ws_controller.handle_command(cmd, source=source)
        except Exception as e:
            self.log(f"âŒ command failed: {e}")
            return

        if isinstance(out, dict) and out.get("action") == "blocked_by_focus_policy":
            reply = str(out.get("reply", "Locked in.")).strip()
            self.log(reply)
            if self.voice_engine is not None:
                try:
                    self.voice_engine.speak(reply, language="en-IN")
                except Exception:
                    pass
                self.aurora_state_store.update(current_mode=str(mode))
            self._sync_aurora_state()
            return

        self.log(f"âœ… OUT: {out}")

        if isinstance(out, dict) and out.get("action") == "set_mode":
            mode = str(out.get("mode") or "study")
            self._apply_mode_layout(mode)
            try:
                self.aurora_ring.pulse(intensity=1.35, duration=0.35)
            except Exception:
                print("command failed:", e)
                pass

        if isinstance(out, dict) and out.get("action") == "self_explain":
            self.log("\n" + str(out.get("text", "")).strip())

        if isinstance(out, dict) and out.get("action") == "greet":
            reply = str(out.get("reply", "")).strip()
            if reply:
                self.log(reply)
                if self.voice_engine is not None:
                    try:
                        self.voice_engine.speak(reply, language="en-IN")
                    except Exception:
                        pass

        self._sync_aurora_state()

    # -------------------------
    # Mode layouts
    # -------------------------
    def _apply_mode_layout(self, mode: str) -> None:
        self._current_mode = mode
        self.l_mode.setText(f"Mode: {mode}")

        if mode in ("coding",):
            self.aurora_canvas.setVisible(False)
            self.avatar.setVisible(True)
            self.console.setVisible(True)
        elif mode in ("exam",):
            self.aurora_canvas.setVisible(False)
            self.avatar.setVisible(False)
            self.console.setVisible(True)
        elif mode in ("calm",):
            self.aurora_canvas.setVisible(True)
            self.avatar.setVisible(True)
            self.console.setVisible(False)
        else:
            self.aurora_canvas.setVisible(True)
            self.avatar.setVisible(True)
            self.console.setVisible(True)

        try:
            if hasattr(self.avatar, "set_mode_persona"):
                self.avatar.set_mode_persona(mode)
        except Exception:
            pass

        self.aurora_state_store.update(current_mode=mode)

    # -------------------------
    # Focus timer UI tick
    # -------------------------
    def _tick_focus(self) -> None:
        try:
            secs = int(self.ws_controller.focus_seconds_left())
        except Exception:
            secs = 0

        if secs <= 0:
            self.l_timer.setText("Focus timer: --")
            return

        mm = secs // 60
        ss = secs % 60
        self.l_timer.setText(f"Focus timer: {mm:02d}:{ss:02d} remaining")

    # -------------------------
    # Signal handlers
    # -------------------------
    def _on_mode_changed_signal(self, mode: str, meta: dict) -> None:
        self._apply_mode_layout(str(mode))

    def _on_focus_started_signal(self, minutes: int, meta: dict) -> None:
        self.log(f"â±ï¸ Focus started: {minutes} minutes")
        try:
            self.aurora_ring.pulse(intensity=1.5, duration=0.45)
        except Exception:
            pass

    def _on_focus_stopped_signal(self, meta: dict) -> None:
        self.log("â¹ï¸ Focus stopped")
        try:
            self.aurora_ring.pulse(intensity=1.1, duration=0.25)
        except Exception:
            pass
