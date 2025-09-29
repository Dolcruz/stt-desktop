from __future__ import annotations

from typing import Optional

from PySide6 import QtCore, QtGui, QtWidgets


class ResultPopup(QtWidgets.QDialog):
    """Popup that shows transcribed text with copy/paste actions.

    Supports auto-close with a countdown and a pin toggle to prevent closing.
    """

    def __init__(self, text: str, auto_close_seconds: int = 10, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Transkription")
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.setMinimumWidth(520)
        self.setMinimumHeight(280)
        
        # Dark mode styling
        self.setStyleSheet("""
            QDialog {
                background-color: #181818;
            }
        """)

        self._pinned = False
        self._remaining = auto_close_seconds

        # Title label - dark mode
        title_label = QtWidgets.QLabel("Transkription erfolgreich")
        title_label.setStyleSheet("""
            font-size: 16pt;
            font-weight: 700;
            color: #ffffff;
            padding: 8px 0px;
        """)
        
        self._text = QtWidgets.QPlainTextEdit()
        self._text.setPlainText(text)
        self._text.setMinimumHeight(140)
        self._text.setStyleSheet("""
            QPlainTextEdit {
                background-color: #242424;
                border: 1.5px solid #3d3d3d;
                border-radius: 12px;
                padding: 14px;
                font-size: 11pt;
                line-height: 1.5;
                color: #f0f0f0;
            }
        """)

        self._copy_btn = QtWidgets.QPushButton("Kopieren")
        self._paste_btn = QtWidgets.QPushButton("Einfügen")
        self._dismiss_btn = QtWidgets.QPushButton("Verwerfen")
        self._pin_btn = QtWidgets.QPushButton("Anheften")
        self._pin_btn.setCheckable(True)

        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addWidget(self._copy_btn)
        btn_row.addWidget(self._paste_btn)
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
        layout.setSpacing(12)
        layout.addWidget(title_label)
        layout.addWidget(self._text)
        layout.addLayout(btn_row)
        layout.addWidget(self._status_label)

        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._tick)
        if auto_close_seconds > 0:
            self._timer.start(1000)
            self._update_status()

        self._copy_btn.clicked.connect(self._copy)
        self._paste_btn.clicked.connect(self._paste)
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
        if self._pinned:
            self._status_label.setText("Angeheftet; automatisch Schließen ist pausiert.")
        else:
            self._status_label.setText(f"Schließt automatisch in {self._remaining}s")

    def _copy(self) -> None:
        text = self._text.toPlainText()
        QtWidgets.QApplication.clipboard().setText(text)
        self._status_label.setText("In Zwischenablage kopiert.")

    def _paste(self) -> None:
        # Ensure text is on clipboard, then send Ctrl+V
        text = self._text.toPlainText()
        QtWidgets.QApplication.clipboard().setText(text)
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
        return self._text.toPlainText()
