"""
Dialog Mode UI - Two-way translation conversation
"""

import logging
from typing import Optional, Literal
from PySide6 import QtWidgets, QtCore, QtGui

logger = logging.getLogger(__name__)


class DialogWindow(QtWidgets.QDialog):
    """Dialog mode window for two-way translation conversations."""
    
    # Signals
    start_recording = QtCore.Signal(str)  # Emit current speaker's language
    stop_recording = QtCore.Signal()
    closed = QtCore.Signal()
    
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Dialog-Modus")
        self.setWindowFlag(QtCore.Qt.Window)
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)
        
        # Current state
        self._current_speaker: Literal["A", "B"] = "A"
        self._language_a: str = "Deutsch"
        self._language_b: str = "Englisch"
        self._is_recording: bool = False
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Build the dialog mode interface."""
        
        # Main layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        
        # Title
        title = QtWidgets.QLabel("🗣️ Dialog-Modus")
        title.setStyleSheet("""
            font-size: 20pt; font-weight: 700; color: #ffffff; padding: 8px 0px;
        """)
        layout.addWidget(title)
        
        # Language selection area
        lang_group = QtWidgets.QGroupBox("Sprachen")
        lang_group.setStyleSheet("""
            QGroupBox { 
                font-size: 11pt; font-weight: 600; color: #f0f0f0; 
                border: 2px solid #4a4a4a; border-radius: 8px; padding: 12px;
                margin-top: 8px;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 8px; }
        """)
        lang_layout = QtWidgets.QHBoxLayout(lang_group)
        lang_layout.setSpacing(16)
        
        # Speaker A
        speaker_a_container = QtWidgets.QVBoxLayout()
        speaker_a_label = QtWidgets.QLabel("🎤 Sprecher A:")
        speaker_a_label.setStyleSheet("font-size: 10pt; color: #a0a0a0;")
        
        self._lang_a_combo = QtWidgets.QComboBox()
        self._lang_a_combo.addItems(["Deutsch", "Englisch", "Spanisch", "Französisch", "Italienisch", "Arabisch"])
        self._lang_a_combo.setCurrentText("Deutsch")
        self._lang_a_combo.setStyleSheet("""
            QComboBox { 
                background-color: #2a2a2a; color: #f0f0f0; border: 1.5px solid #4a4a4a; 
                border-radius: 6px; padding: 8px 10px; font-size: 10pt; 
            }
            QComboBox:hover { border-color: #6a6a6a; }
            QComboBox QAbstractItemView { background-color: #2a2a2a; color: #f0f0f0; selection-background-color: #4a6a8a; }
        """)
        self._lang_a_combo.currentTextChanged.connect(self._update_languages)
        
        speaker_a_container.addWidget(speaker_a_label)
        speaker_a_container.addWidget(self._lang_a_combo)
        
        # Arrow
        arrow_label = QtWidgets.QLabel("↔️")
        arrow_label.setStyleSheet("font-size: 24pt; padding: 20px 12px;")
        
        # Speaker B
        speaker_b_container = QtWidgets.QVBoxLayout()
        speaker_b_label = QtWidgets.QLabel("🎤 Sprecher B:")
        speaker_b_label.setStyleSheet("font-size: 10pt; color: #a0a0a0;")
        
        self._lang_b_combo = QtWidgets.QComboBox()
        self._lang_b_combo.addItems(["Deutsch", "Englisch", "Spanisch", "Französisch", "Italienisch", "Arabisch"])
        self._lang_b_combo.setCurrentText("Englisch")
        self._lang_b_combo.setStyleSheet("""
            QComboBox { 
                background-color: #2a2a2a; color: #f0f0f0; border: 1.5px solid #4a4a4a; 
                border-radius: 6px; padding: 8px 10px; font-size: 10pt; 
            }
            QComboBox:hover { border-color: #6a6a6a; }
            QComboBox QAbstractItemView { background-color: #2a2a2a; color: #f0f0f0; selection-background-color: #4a6a8a; }
        """)
        self._lang_b_combo.currentTextChanged.connect(self._update_languages)
        
        speaker_b_container.addWidget(speaker_b_label)
        speaker_b_container.addWidget(self._lang_b_combo)
        
        lang_layout.addLayout(speaker_a_container)
        lang_layout.addWidget(arrow_label, alignment=QtCore.Qt.AlignCenter)
        lang_layout.addLayout(speaker_b_container)
        
        layout.addWidget(lang_group)
        
        # Current speaker indicator
        self._speaker_indicator = QtWidgets.QLabel("🎙️ Sprecher A ist dran (Deutsch)")
        self._speaker_indicator.setAlignment(QtCore.Qt.AlignCenter)
        self._speaker_indicator.setStyleSheet("""
            font-size: 14pt; font-weight: 600; color: #4287f5; 
            background-color: #2a3a4a; border-radius: 8px; padding: 16px;
        """)
        layout.addWidget(self._speaker_indicator)
        
        # Conversation history
        history_label = QtWidgets.QLabel("📜 Gesprächsverlauf")
        history_label.setStyleSheet("font-size: 11pt; font-weight: 600; color: #f0f0f0; padding: 8px 0px;")
        
        self._history_text = QtWidgets.QPlainTextEdit()
        self._history_text.setReadOnly(True)
        self._history_text.setPlaceholderText("Der Gesprächsverlauf wird hier angezeigt...")
        self._history_text.setStyleSheet("""
            QPlainTextEdit {
                background-color: #242424; border: 2px solid #4a4a4a; border-radius: 8px;
                padding: 12px; font-size: 10pt; color: #f0f0f0; font-family: 'Segoe UI', sans-serif;
            }
        """)
        
        layout.addWidget(history_label)
        layout.addWidget(self._history_text, stretch=1)
        
        # Status label
        self._status_label = QtWidgets.QLabel("")
        self._status_label.setAlignment(QtCore.Qt.AlignCenter)
        self._status_label.setStyleSheet("""
            font-size: 9pt; color: #a0a0a0; padding: 6px 0px;
        """)
        layout.addWidget(self._status_label)
        
        # Control buttons
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(12)
        
        self._record_btn = QtWidgets.QPushButton("🎙️ Aufnahme starten")
        self._record_btn.setStyleSheet("""
            QPushButton { 
                background-color: #4287f5; color: #ffffff; font-weight: 600; 
                padding: 12px 20px; border-radius: 8px; font-size: 11pt;
            }
            QPushButton:hover { background-color: #3a7ae0; }
            QPushButton:pressed { background-color: #2a6ad0; }
        """)
        self._record_btn.clicked.connect(self._toggle_recording)
        
        self._switch_btn = QtWidgets.QPushButton("🔄 Sprecher wechseln")
        self._switch_btn.setStyleSheet("""
            QPushButton { 
                background-color: #2a5a5a; color: #ffffff; font-weight: 600; 
                padding: 12px 20px; border-radius: 8px; font-size: 11pt;
            }
            QPushButton:hover { background-color: #3a6a6a; }
        """)
        self._switch_btn.clicked.connect(self._switch_speaker)
        
        self._clear_btn = QtWidgets.QPushButton("🗑️ Verlauf löschen")
        self._clear_btn.setStyleSheet("""
            QPushButton { 
                background-color: #8a2a2a; color: #ffe0e0; font-weight: 600; 
                padding: 12px 20px; border-radius: 8px; font-size: 11pt;
            }
            QPushButton:hover { background-color: #9a3a3a; }
        """)
        self._clear_btn.clicked.connect(self._clear_history)
        
        self._close_btn = QtWidgets.QPushButton("❌ Schließen")
        self._close_btn.setStyleSheet("""
            QPushButton { 
                background-color: #3a3a3a; color: #f0f0f0; font-weight: 600; 
                padding: 12px 20px; border-radius: 8px; font-size: 11pt;
            }
            QPushButton:hover { background-color: #4a4a4a; }
        """)
        self._close_btn.clicked.connect(self.close)
        
        btn_layout.addWidget(self._record_btn)
        btn_layout.addWidget(self._switch_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self._clear_btn)
        btn_layout.addWidget(self._close_btn)
        
        layout.addLayout(btn_layout)
        
        # Initial state
        self._update_speaker_indicator()
    
    def _update_languages(self) -> None:
        """Update stored language selections."""
        self._language_a = self._lang_a_combo.currentText()
        self._language_b = self._lang_b_combo.currentText()
        self._update_speaker_indicator()
    
    def _update_speaker_indicator(self) -> None:
        """Update the visual indicator for current speaker."""
        if self._current_speaker == "A":
            self._speaker_indicator.setText(f"🎙️ Sprecher A ist dran ({self._language_a})")
            self._speaker_indicator.setStyleSheet("""
                font-size: 14pt; font-weight: 600; color: #4287f5; 
                background-color: #2a3a4a; border-radius: 8px; padding: 16px;
            """)
        else:
            self._speaker_indicator.setText(f"🎙️ Sprecher B ist dran ({self._language_b})")
            self._speaker_indicator.setStyleSheet("""
                font-size: 14pt; font-weight: 600; color: #f5a742; 
                background-color: #4a3a2a; border-radius: 8px; padding: 16px;
            """)
    
    def _toggle_recording(self) -> None:
        """Start or stop recording."""
        if not self._is_recording:
            # Start recording
            current_lang = self._language_a if self._current_speaker == "A" else self._language_b
            self._is_recording = True
            self._record_btn.setText("⏹️ Aufnahme beenden")
            self._record_btn.setStyleSheet("""
                QPushButton { 
                    background-color: #8a2a2a; color: #ffe0e0; font-weight: 600; 
                    padding: 12px 20px; border-radius: 8px; font-size: 11pt;
                }
                QPushButton:hover { background-color: #9a3a3a; }
            """)
            self._switch_btn.setEnabled(False)
            self._lang_a_combo.setEnabled(False)
            self._lang_b_combo.setEnabled(False)
            self.start_recording.emit(current_lang)
        else:
            # Stop recording
            self._is_recording = False
            self._record_btn.setText("🎙️ Aufnahme starten")
            self._record_btn.setStyleSheet("""
                QPushButton { 
                    background-color: #4287f5; color: #ffffff; font-weight: 600; 
                    padding: 12px 20px; border-radius: 8px; font-size: 11pt;
                }
                QPushButton:hover { background-color: #3a7ae0; }
            """)
            self._switch_btn.setEnabled(True)
            self._lang_a_combo.setEnabled(True)
            self._lang_b_combo.setEnabled(True)
            self.stop_recording.emit()
    
    def _switch_speaker(self) -> None:
        """Switch to the other speaker."""
        if not self._is_recording:
            self._current_speaker = "B" if self._current_speaker == "A" else "A"
            self._update_speaker_indicator()
    
    def _clear_history(self) -> None:
        """Clear conversation history."""
        self._history_text.clear()
        self._status_label.setText("Verlauf gelöscht")
    
    def add_to_history(self, speaker: str, language: str, original: str, translated: str) -> None:
        """Add a conversation turn to history."""
        entry = f"[{speaker} - {language}]\n{original}\n\n[→ Übersetzt]\n{translated}\n\n" + ("="*60) + "\n\n"
        self._history_text.appendPlainText(entry)
        # Auto-scroll to bottom
        cursor = self._history_text.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        self._history_text.setTextCursor(cursor)
    
    def set_status(self, text: str) -> None:
        """Update status label."""
        self._status_label.setText(text)
    
    def reset_recording_state(self) -> None:
        """Reset recording button to initial state (after error or cancel)."""
        self._is_recording = False
        self._record_btn.setText("🎙️ Aufnahme starten")
        self._record_btn.setStyleSheet("""
            QPushButton { 
                background-color: #4287f5; color: #ffffff; font-weight: 600; 
                padding: 12px 20px; border-radius: 8px; font-size: 11pt;
            }
            QPushButton:hover { background-color: #3a7ae0; }
        """)
        self._switch_btn.setEnabled(True)
        self._lang_a_combo.setEnabled(True)
        self._lang_b_combo.setEnabled(True)
    
    def auto_switch_speaker(self) -> None:
        """Automatically switch to next speaker after successful turn."""
        self._current_speaker = "B" if self._current_speaker == "A" else "A"
        self._update_speaker_indicator()
    
    def get_current_speaker(self) -> str:
        """Get current speaker (A or B)."""
        return self._current_speaker
    
    def get_target_language(self) -> str:
        """Get the target language for translation (opposite of current speaker)."""
        if self._current_speaker == "A":
            return self._language_b
        else:
            return self._language_a
    
    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """Handle window close."""
        self.closed.emit()
        super().closeEvent(event)
