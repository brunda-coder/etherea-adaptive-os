from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QPushButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor, QPainter

from corund.voice import VoiceEngine

class SettingsWidget(QWidget):
    """
    Minimalist Settings Panel.
    - Glassmorphism style.
    - Text-only Language Selector.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Main Layout (Centered Box)
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        
        # Content Frame
        self.frame = QFrame()
        self.frame.setFixedSize(500, 600)
        self.frame.setStyleSheet("""
            QFrame {
                background-color: rgba(10, 15, 20, 240);
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 20px;
            }
        """)
        main_layout.addWidget(self.frame)
        
        # Frame Layout
        layout = QVBoxLayout(self.frame)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # 1. Title
        title = QLabel("SYSTEM SETTINGS")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: white; font-size: 18px; font-weight: bold; letter-spacing: 4px;")
        layout.addWidget(title)
        
        layout.addSpacing(20)
        
        # 2. Section: Voice Language
        lbl_lang = QLabel("VOICE LANGUAGE")
        lbl_lang.setStyleSheet("color: rgba(255,255,255,150); font-size: 12px; font-weight: bold; letter-spacing: 2px;")
        layout.addWidget(lbl_lang)
        
        # Language List
        self.languages = [
            ("ENGLISH", "en"),
            ("HINDI", "hi"),
            ("KANNADA", "kn"),
            ("TELUGU", "te"),
            ("MARATHI", "mr")
        ]
        
        self.lang_buttons = []
        
        for label_text, code in self.languages:
            btn = QPushButton(label_text)
            btn.setCheckable(True)
            btn.setFixedHeight(50)
            btn.setCursor(Qt.PointingHandCursor)
            # Custom Style for "Radio" look using PushButton
            btn.setStyleSheet(self._get_btn_style(False))
            btn.clicked.connect(lambda checked, c=code, b=btn: self.on_language_selected(c, b))
            
            layout.addWidget(btn)
            self.lang_buttons.append((btn, code))
            
        layout.addSpacing(30)
        
        # 3. Section: Expressive Modes
        lbl_expr = QLabel("EXPRESSIVE MODES")
        lbl_expr.setStyleSheet("color: rgba(255,255,255,150); font-size: 12px; font-weight: bold; letter-spacing: 2px;")
        layout.addWidget(lbl_expr)
        
        self.btn_dance = QPushButton("SLOW DANCE")
        self.btn_dance.setCheckable(True)
        self.btn_dance.setFixedHeight(50)
        self.btn_dance.setStyleSheet(self._get_btn_style(False))
        self.btn_dance.clicked.connect(self._toggle_dance)
        layout.addWidget(self.btn_dance)
        
        self.btn_hum = QPushButton("SOFT HUMMING")
        self.btn_hum.setCheckable(True)
        self.btn_hum.setFixedHeight(50)
        self.btn_hum.setStyleSheet(self._get_btn_style(False))
        self.btn_hum.clicked.connect(self._toggle_hum)
        layout.addWidget(self.btn_hum)
        
        layout.addStretch()
        
        # Select Default (English)
        self.on_language_selected("en", self.lang_buttons[0][0])

    def _toggle_dance(self, checked):
        self.btn_dance.setStyleSheet(self._get_btn_style(checked))
        if checked: 
             self.btn_hum.setChecked(False) # Mutual exclusive for simplicity
             self.btn_hum.setStyleSheet(self._get_btn_style(False))
        
        mode = "dance" if checked else "idle"
        from corund.state import AppState
        AppState.instance().set_expressive_mode(mode)

    def _toggle_hum(self, checked):
        self.btn_hum.setStyleSheet(self._get_btn_style(checked))
        if checked: 
             self.btn_dance.setChecked(False)
             self.btn_dance.setStyleSheet(self._get_btn_style(False))
             
        mode = "humming" if checked else "idle"
        from corund.state import AppState
        AppState.instance().set_expressive_mode(mode)

    def _get_btn_style(self, active: bool):
        if active:
            return """
                QPushButton {
                    background-color: rgba(0, 240, 255, 40);
                    border: 1px solid rgba(0, 240, 255, 100);
                    color: white;
                    font-size: 14px;
                    border-radius: 5px;
                    text-align: left;
                    padding-left: 20px;
                }
            """
        else:
             return """
                QPushButton {
                    background-color: rgba(255, 255, 255, 5);
                    border: 1px solid rgba(255, 255, 255, 10);
                    color: rgba(255, 255, 255, 150);
                    font-size: 14px;
                    border-radius: 5px;
                    text-align: left;
                    padding-left: 20px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 15);
                    color: white;
                }
            """

    def on_language_selected(self, code, sender_btn):
        # Update UI state
        for btn, c in self.lang_buttons:
            is_active = (btn == sender_btn)
            btn.setChecked(is_active)
            btn.setStyleSheet(self._get_btn_style(is_active))
            
        # Update Engine
        VoiceEngine.instance().set_language(code)
        print(f"DEBUG: Language set to {code}")
