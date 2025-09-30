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
    # Signal emitted when user wants to translate text (text, target_language)
    translation_requested = QtCore.Signal(str, str)

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
        
        # Translation controls
        translate_label = QtWidgets.QLabel("🌍 Übersetzen:")
        translate_label.setStyleSheet("font-size: 10pt; color: #f0f0f0; padding: 4px 0px;")
        
        self._translate_combo = QtWidgets.QComboBox()
        self._translate_combo.addItem("-- Keine Übersetzung --", "")
        self._translate_combo.addItem("🇬🇧 Englisch", "Englisch")
        self._translate_combo.addItem("🇪🇸 Spanisch", "Spanisch")
        self._translate_combo.addItem("🇫🇷 Französisch", "Französisch")
        self._translate_combo.addItem("🇮🇹 Italienisch", "Italienisch")
        self._translate_combo.addItem("🇸🇦 Arabisch", "Arabisch")
        self._translate_combo.addItem("✏️ Andere Sprache...", "custom")
        self._translate_combo.setMinimumWidth(200)
        self._translate_combo.setStyleSheet("""
            QComboBox {
                background-color: #2a2a2a;
                color: #f0f0f0;
                border: 1.5px solid #4a4a4a;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 10pt;
            }
            QComboBox:hover {
                border-color: #6a6a6a;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #2a2a2a;
                color: #f0f0f0;
                selection-background-color: #4a6a8a;
            }
        """)
        
        self._custom_language_input = QtWidgets.QLineEdit()
        self._custom_language_input.setPlaceholderText("z.B. Japanisch, Russisch, ...")
        self._custom_language_input.hide()
        self._custom_language_input.setStyleSheet("""
            QLineEdit {
                background-color: #2a2a2a;
                color: #f0f0f0;
                border: 1.5px solid #4a4a4a;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 10pt;
            }
            QLineEdit:focus {
                border-color: #6a8aaa;
            }
        """)
        
        self._translate_btn = QtWidgets.QPushButton("🌐 Übersetzen")
        self._translate_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a5a6a;
                color: #ffffff;
                font-weight: 600;
                padding: 8px 16px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #3a6a7a;
            }
            QPushButton:disabled {
                background-color: #3a3a3a;
                color: #808080;
            }
        """)
        
        # Connect translation combo to show/hide custom input
        self._translate_combo.currentIndexChanged.connect(self._on_translation_changed)
        
        translate_row = QtWidgets.QHBoxLayout()
        translate_row.addWidget(translate_label)
        translate_row.addWidget(self._translate_combo)
        translate_row.addWidget(self._custom_language_input)
        translate_row.addWidget(self._translate_btn)
        translate_row.addStretch()
        
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
        layout.addLayout(translate_row)
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
        self._translate_btn.clicked.connect(self._on_translate_clicked)
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
    
    def _on_translation_changed(self, index: int) -> None:
        """Handle translation language selection change."""
        selected_value = self._translate_combo.currentData()
        # Show custom language input if "Andere Sprache..." is selected
        if selected_value == "custom":
            self._custom_language_input.show()
        else:
            self._custom_language_input.hide()
    
    def _on_translate_clicked(self) -> None:
        """Handle translation button click."""
        selected_value = self._translate_combo.currentData()
        
        # Determine target language
        if selected_value == "custom":
            target_language = self._custom_language_input.text().strip()
            if not target_language:
                self._status_label.setText("⚠️ Bitte Zielsprache eingeben")
                return
        elif selected_value == "":
            self._status_label.setText("⚠️ Bitte Zielsprache auswählen")
            return
        else:
            target_language = selected_value
        
        # Get the currently active text (corrected if available, otherwise original)
        text_to_translate = self._corrected_text if self._corrected_text else self._original_text
        
        self._status_label.setText(f"Übersetze nach {target_language}...")
        self._translate_btn.setEnabled(False)
        self.translation_requested.emit(text_to_translate, target_language)
    
    @QtCore.Slot(str, str)
    def set_translated_text(self, translated_text: str, target_language: str) -> None:
        """Display the translated text in a message box."""
        # Simple dialog to show translation
        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle(f"Übersetzung ({target_language})")
        msg.setText(translated_text)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #181818;
            }
            QLabel {
                color: #f0f0f0;
                font-size: 11pt;
                min-width: 400px;
            }
            QPushButton {
                background-color: #2a5a8a;
                color: #ffffff;
                padding: 6px 16px;
                border-radius: 6px;
            }
        """)
        
        # Add copy button
        copy_btn = msg.addButton("📋 Kopieren", QtWidgets.QMessageBox.ActionRole)
        msg.addButton("Schließen", QtWidgets.QMessageBox.AcceptRole)
        
        msg.exec()
        
        # If user clicked copy button
        if msg.clickedButton() == copy_btn:
            QtWidgets.QApplication.clipboard().setText(translated_text)
            self._status_label.setText(f"✓ Übersetzung ({target_language}) kopiert")
        else:
            self._status_label.setText(f"✓ Übersetzung abgeschlossen")
        
        self._translate_btn.setEnabled(True)