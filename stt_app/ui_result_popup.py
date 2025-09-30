from __future__ import annotations

from typing import Optional

from PySide6 import QtCore, QtGui, QtWidgets


class ResultPopup(QtWidgets.QDialog):
    """Popup that shows transcribed text with copy/paste actions.

    Supports auto-close with a countdown and a pin toggle to prevent closing.
    Shows both original and corrected versions when grammar correction is applied.
    """
    
    # Signal emitted when user wants to correct grammar
    grammar_correction_requested = QtCore.Signal()

    def __init__(self, text: str, auto_close_seconds: int = 10, show_correct_button: bool = True, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Transkription")
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.setMinimumWidth(620)
        self.setMinimumHeight(360)
        
        # Dark mode styling
        self.setStyleSheet("""
            QDialog {
                background-color: #181818;
            }
        """)

        self._pinned = False
        self._remaining = auto_close_seconds
        self._original_text = text
        self._corrected_text: Optional[str] = None
        self._active_version = "original"  # or "corrected"

        # Title label - dark mode
        title_label = QtWidgets.QLabel("Transkription erfolgreich")
        title_label.setStyleSheet("""
            font-size: 16pt;
            font-weight: 700;
            color: #ffffff;
            padding: 8px 0px;
        """)
        
        # Original text area
        original_header = QtWidgets.QLabel("📝 Original")
        original_header.setStyleSheet("font-size: 11pt; font-weight: 600; color: #f0f0f0; padding: 4px 0px;")
        
        self._original_text_edit = QtWidgets.QPlainTextEdit()
        self._original_text_edit.setPlainText(text)
        self._original_text_edit.setReadOnly(True)
        self._original_text_edit.setMinimumHeight(110)
        self._original_text_edit.setStyleSheet("""
            QPlainTextEdit {
                background-color: #242424;
                border: 2px solid #4a8a4a;
                border-radius: 8px;
                padding: 12px;
                font-size: 10.5pt;
                color: #f0f0f0;
            }
        """)
        
        # Original buttons
        self._copy_original_btn = QtWidgets.QPushButton("📋 Kopieren (Original)")
        self._copy_original_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a5a2a;
                color: #ffffff;
                font-weight: 600;
                padding: 8px 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #3a6a3a;
            }
        """)
        
        # Corrected text area (initially hidden)
        self._corrected_container = QtWidgets.QWidget()
        corrected_layout = QtWidgets.QVBoxLayout(self._corrected_container)
        corrected_layout.setContentsMargins(0, 8, 0, 0)
        corrected_layout.setSpacing(6)
        
        corrected_header = QtWidgets.QLabel("✨ Korrigiert")
        corrected_header.setStyleSheet("font-size: 11pt; font-weight: 600; color: #6ab4ff; padding: 4px 0px;")
        
        self._corrected_text_edit = QtWidgets.QPlainTextEdit()
        self._corrected_text_edit.setReadOnly(True)
        self._corrected_text_edit.setMinimumHeight(110)
        self._corrected_text_edit.setStyleSheet("""
            QPlainTextEdit {
                background-color: #242424;
                border: 2px solid #4a7a9a;
                border-radius: 8px;
                padding: 12px;
                font-size: 10.5pt;
                color: #f0f0f0;
            }
        """)
        
        # Corrected buttons
        self._copy_corrected_btn = QtWidgets.QPushButton("📋 Kopieren (Korrigiert)")
        self._copy_corrected_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a5a8a;
                color: #ffffff;
                font-weight: 600;
                padding: 8px 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #3a6a9a;
            }
        """)
        
        corrected_layout.addWidget(corrected_header)
        corrected_layout.addWidget(self._corrected_text_edit)
        corrected_layout.addWidget(self._copy_corrected_btn)
        
        # Initially hide corrected container
        self._corrected_container.hide()
        
        # Action buttons
        self._paste_btn = QtWidgets.QPushButton("Einfügen")
        self._correct_btn = QtWidgets.QPushButton("✓ Korrigieren")
        self._correct_btn.setStyleSheet("""
            QPushButton {
                background-color: #5a6a2a;
                color: #ffffff;
                font-weight: 600;
                padding: 8px 16px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #6a7a3a;
            }
            QPushButton:disabled {
                background-color: #3a3a3a;
                color: #808080;
            }
        """)
        self._dismiss_btn = QtWidgets.QPushButton("Verwerfen")
        self._pin_btn = QtWidgets.QPushButton("Anheften")
        self._pin_btn.setCheckable(True)
        
        # Show correct button based on parameter
        if not show_correct_button:
            self._correct_btn.hide()

        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addWidget(self._paste_btn)
        btn_row.addWidget(self._correct_btn)
        btn_row.addStretch(1)
        btn_row.addWidget(self._pin_btn)
        btn_row.addWidget(self._dismiss_btn)

        self._status_label = QtWidgets.QLabel("")
        self._status_label.setStyleSheet("""
            color: #a0a0a0;
            font-size: 9pt;
            padding: 6px 0px;
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(10)
        layout.addWidget(title_label)
        layout.addWidget(original_header)
        layout.addWidget(self._original_text_edit)
        layout.addWidget(self._copy_original_btn)
        layout.addWidget(self._corrected_container)
        layout.addLayout(btn_row)
        layout.addWidget(self._status_label)

        # Disable auto-close to allow users to read and correct text
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._tick)
        # Auto-close disabled for better UX
        # if auto_close_seconds > 0:
        #     self._timer.start(1000)
        #     self._update_status()

        self._copy_original_btn.clicked.connect(self._copy_original)
        self._copy_corrected_btn.clicked.connect(self._copy_corrected)
        self._paste_btn.clicked.connect(self._paste)
        self._correct_btn.clicked.connect(self._on_correct_clicked)
        self._dismiss_btn.clicked.connect(self.reject)
        self._pin_btn.toggled.connect(self._set_pinned)

    def _set_pinned(self, checked: bool) -> None:
        self._pinned = checked
        self._update_status()

    def _tick(self) -> None:
        if self._pinned:
            return
        self._remaining -= 1
        if self._remaining <= 0:
            self.accept()
            return
        self._update_status()

    def _update_status(self) -> None:
        # Auto-close disabled, no need to show countdown
        pass
        # if self._pinned:
        #     self._status_label.setText("Angeheftet; automatisch Schließen ist pausiert.")
        # else:
        #     self._status_label.setText(f"Schließt automatisch in {self._remaining}s")

    def _copy_original(self) -> None:
        QtWidgets.QApplication.clipboard().setText(self._original_text)
        self._active_version = "original"
        self._status_label.setText("✓ Original in Zwischenablage kopiert.")

    def _copy_corrected(self) -> None:
        if self._corrected_text:
            QtWidgets.QApplication.clipboard().setText(self._corrected_text)
            self._active_version = "corrected"
            self._status_label.setText("✓ Korrigierte Version in Zwischenablage kopiert.")

    def _paste(self) -> None:
        # Paste the active version
        text_to_paste = self._corrected_text if self._active_version == "corrected" and self._corrected_text else self._original_text
        QtWidgets.QApplication.clipboard().setText(text_to_paste)
        # Delay slightly to ensure clipboard set before paste
        QtCore.QTimer.singleShot(50, self._send_paste)

    def _send_paste(self) -> None:
        # Import locally to avoid hard dependency for non-Windows users
        try:
            import keyboard
            keyboard.send("ctrl+v")
        except Exception:
            pass

    def get_text(self) -> str:
        """Get the currently active text (original or corrected)."""
        if self._active_version == "corrected" and self._corrected_text:
            return self._corrected_text
        return self._original_text
    
    @QtCore.Slot(str)
    def set_corrected_text(self, corrected_text: str) -> None:
        """Set and display the corrected text."""
        self._corrected_text = corrected_text
        self._corrected_text_edit.setPlainText(corrected_text)
        self._corrected_container.show()
        self._active_version = "corrected"  # Switch to corrected by default
        self._correct_btn.setEnabled(True)
        self._status_label.setText("✓ Grammatik korrigiert! Korrigierte Version ist aktiv.")
        # Increase dialog height to accommodate corrected text
        self.setMinimumHeight(560)
    
    def _on_correct_clicked(self) -> None:
        """Handle grammar correction button click."""
        self._status_label.setText("Korrigiere Grammatik...")
        self._correct_btn.setEnabled(False)
        self.grammar_correction_requested.emit()