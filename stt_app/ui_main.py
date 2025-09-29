from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional

from PySide6 import QtCore, QtGui, QtWidgets

from .config import AppSettings, load_settings, save_settings, set_api_key_secure, get_app_dir

logger = logging.getLogger(__name__)


@dataclass
class HistoryItem:
    timestamp: str
    text: str


class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, settings: AppSettings, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Einstellungen")
        self.setMinimumWidth(500)
        self._settings = settings
        
        # Dark mode dialog styling
        self.setStyleSheet("""
            QDialog {
                background-color: #181818;
            }
        """)

        self._api_key_edit = QtWidgets.QLineEdit()
        self._hotkey_edit = QtWidgets.QLineEdit(settings.toggle_hotkey)
        self._auto_copy_cb = QtWidgets.QCheckBox("Automatisch kopieren")
        self._auto_copy_cb.setChecked(settings.auto_copy)
        self._auto_paste_cb = QtWidgets.QCheckBox("Automatisch einfügen")
        self._auto_paste_cb.setChecked(settings.auto_paste)

        self._max_dur_spin = QtWidgets.QSpinBox()
        # Allow 0 = unlimited; keep an upper sanity cap
        self._max_dur_spin.setRange(0, 24 * 60 * 60)
        self._max_dur_spin.setValue(settings.max_duration_seconds)
        self._max_dur_spin.setSpecialValueText("Unbegrenzt")
        self._silence_thresh = QtWidgets.QDoubleSpinBox()
        self._silence_thresh.setRange(0.0, 1.0)
        self._silence_thresh.setSingleStep(0.01)
        self._silence_thresh.setValue(settings.silence_threshold_rms)

        # Device selection
        self._device_combo = QtWidgets.QComboBox()
        self._populate_devices()

        # Section headers - no emojis, dark mode
        api_header = QtWidgets.QLabel("API-Konfiguration")
        api_header.setStyleSheet("font-size: 12pt; font-weight: 600; color: #ffffff; padding-top: 8px;")
        
        audio_header = QtWidgets.QLabel("Audio-Einstellungen")
        audio_header.setStyleSheet("font-size: 12pt; font-weight: 600; color: #ffffff; padding-top: 12px;")
        
        hotkey_header = QtWidgets.QLabel("Tastenkombinationen")
        hotkey_header.setStyleSheet("font-size: 12pt; font-weight: 600; color: #ffffff; padding-top: 12px;")
        
        ux_header = QtWidgets.QLabel("Verhalten")
        ux_header.setStyleSheet("font-size: 12pt; font-weight: 600; color: #ffffff; padding-top: 12px;")
        
        form = QtWidgets.QFormLayout()
        form.setLabelAlignment(QtCore.Qt.AlignLeft)
        form.setVerticalSpacing(12)
        form.setHorizontalSpacing(12)
        
        form.addRow(api_header)
        form.addRow("Groq API Key:", self._api_key_edit)
        
        form.addRow(audio_header)
        form.addRow("Mikrofon:", self._device_combo)
        form.addRow("Max. Dauer (Sekunden):", self._max_dur_spin)
        form.addRow("Stille-Schwelle (RMS):", self._silence_thresh)
        
        form.addRow(hotkey_header)
        form.addRow("Hotkey (z.B. alt+t):", self._hotkey_edit)
        
        form.addRow(ux_header)
        form.addRow(self._auto_copy_cb)
        form.addRow(self._auto_paste_cb)

        btns = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        layout.addLayout(form)
        layout.addWidget(btns)

    def _populate_devices(self) -> None:
        try:
            import sounddevice as sd
            devices = sd.query_devices()
            # Input devices only
            input_devices = [
                (idx, d) for idx, d in enumerate(devices) if d.get("max_input_channels", 0) > 0
            ]
            self._device_combo.addItem("Standardgerät (System)", userData=None)
            for idx, d in input_devices:
                name = d.get("name", f"Gerät {idx}")
                sr = int(d.get("default_samplerate", 0))
                self._device_combo.addItem(f"{name} ({sr} Hz)", userData=idx)
        except Exception:
            self._device_combo.addItem("Standardgerät (System)", userData=None)

    def apply(self) -> None:
        api = self._api_key_edit.text().strip()
        if api:
            set_api_key_secure(api)
        s = self._settings
        s.toggle_hotkey = self._hotkey_edit.text().strip() or s.toggle_hotkey
        s.max_duration_seconds = int(self._max_dur_spin.value())
        s.silence_threshold_rms = float(self._silence_thresh.value())
        s.auto_copy = self._auto_copy_cb.isChecked()
        s.auto_paste = self._auto_paste_cb.isChecked()
        # Save selected device index
        s.input_device_index = self._device_combo.currentData()


class MainWindow(QtWidgets.QMainWindow):
    start_stop_requested = QtCore.Signal()
    cancel_requested = QtCore.Signal()

    def __init__(self, settings: Optional[AppSettings] = None) -> None:
        super().__init__()
        self.settings = settings or load_settings()
        self.setWindowTitle("Speech-to-Text Desktop")
        self.resize(820, 620)
        
        # Add keyboard shortcuts that work when window has focus
        # These provide a fallback if global hotkeys don't work
        self._shortcut_toggle = QtGui.QShortcut(QtGui.QKeySequence("Alt+T"), self)
        self._shortcut_toggle.activated.connect(self.start_stop_requested.emit)
        
        self._shortcut_cancel = QtGui.QShortcut(QtGui.QKeySequence("Esc"), self)
        self._shortcut_cancel.activated.connect(self.cancel_requested.emit)

        # Header - Modern design
        header = QtWidgets.QFrame()
        header.setObjectName("headerBar")
        hl = QtWidgets.QHBoxLayout(header)
        hl.setContentsMargins(24, 16, 24, 16)
        hl.setSpacing(16)
        
        title = QtWidgets.QLabel("Speech-to-Text")
        title.setStyleSheet("""
            font-size: 18pt;
            font-weight: 700;
            color: #ffffff;
        """)
        
        pill = QtWidgets.QLabel("Bereit")
        pill.setProperty("type", "pill")
        
        hl.addWidget(title)
        hl.addStretch(1)
        hl.addWidget(pill)
        self._status_pill = pill

        # Controls - Dark mode design
        self._status_label = QtWidgets.QLabel("Bereit")
        self._status_label.setStyleSheet("""
            font-size: 13pt; 
            font-weight: 600; 
            color: #f0f0f0;
            padding: 8px 0px;
        """)
        
        # Info label for shortcuts - no emoji
        info_label = QtWidgets.QLabel("Tipp: Alt+T zum Starten/Stoppen, ESC zum Abbrechen")
        info_label.setStyleSheet("""
            font-size: 9pt;
            color: #a0a0a0;
            background-color: #242424;
            border-radius: 8px;
            padding: 10px 14px;
        """)
        
        self._history = QtWidgets.QListWidget()
        # Connect double-click to show full text
        self._history.itemDoubleClicked.connect(self._show_history_detail)
        self._btn_row = QtWidgets.QHBoxLayout()
        self._start_btn = QtWidgets.QPushButton("Aufnahme starten")
        self._start_btn.setProperty("type", "primary")
        self._start_btn.setMinimumHeight(48)
        self._start_btn.setStyleSheet("""
            QPushButton[type="primary"] {
                font-size: 11pt;
                font-weight: 600;
            }
        """)
        
        self._cancel_btn = QtWidgets.QPushButton("Abbrechen")
        self._cancel_btn.setProperty("type", "danger")
        self._cancel_btn.setMinimumHeight(48)
        
        # Settings button with gear icon
        self._visual_settings_btn = QtWidgets.QPushButton("⚙ Visualisierung")
        self._visual_settings_btn.setMinimumHeight(48)
        
        self._btn_row.addWidget(self._start_btn, 3)
        self._btn_row.addWidget(self._cancel_btn, 1)
        self._btn_row.addWidget(self._visual_settings_btn, 2)

        central = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(header)

        content = QtWidgets.QWidget()
        content_l = QtWidgets.QVBoxLayout(content)
        content_l.setContentsMargins(24, 20, 24, 24)
        content_l.setSpacing(16)
        content_l.addWidget(self._status_label)
        content_l.addWidget(info_label)
        content_l.addLayout(self._btn_row)
        
        history_label = QtWidgets.QLabel("Verlauf")
        history_label.setStyleSheet("""
            font-size: 12pt;
            font-weight: 600;
            color: #ffffff;
            padding-top: 8px;
        """)
        content_l.addWidget(history_label)
        content_l.addWidget(self._history)

        layout.addWidget(content)
        self.setCentralWidget(central)

        # Tray icon
        self._tray = QtWidgets.QSystemTrayIcon(self)
        self._tray.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))
        menu = QtWidgets.QMenu()
        act_record = menu.addAction("Aufnahme Start/Stop (Alt+T)")
        act_cancel = menu.addAction("Abbrechen (ESC)")
        menu.addSeparator()
        act_settings = menu.addAction("Einstellungen…")
        act_quit = menu.addAction("Beenden")
        self._tray.setContextMenu(menu)
        self._tray.show()

        # Wire
        self._start_btn.clicked.connect(self.start_stop_requested.emit)
        self._cancel_btn.clicked.connect(self.cancel_requested.emit)
        self._visual_settings_btn.clicked.connect(self._open_visual_settings)
        act_record.triggered.connect(self.start_stop_requested.emit)
        act_cancel.triggered.connect(self.cancel_requested.emit)
        act_settings.triggered.connect(self._open_settings)
        act_quit.triggered.connect(QtWidgets.QApplication.instance().quit)

        self._history_path = get_app_dir() / "history.json"
        self._history_data = []  # Store full history data
        self._load_history()

    # History persistence (simple JSON array)
    def _load_history(self) -> None:
        if self._history_path.exists():
            try:
                items = json.loads(self._history_path.read_text(encoding="utf-8"))
                self._history_data = list(reversed(items))  # Store full data
                for item in self._history_data:
                    # Show preview in list (first 80 chars)
                    preview = item['text'][:80]
                    if len(item['text']) > 80:
                        preview += "..."
                    self._history.addItem(f"{item['timestamp']}: {preview}")
            except Exception:
                pass

    def append_history(self, timestamp: str, text: str, limit: int) -> None:
        # Create history item
        item = {"timestamp": timestamp, "text": text}
        
        # Prepend to in-memory data
        self._history_data.insert(0, item)
        
        # Prepend visually with preview
        preview = text[:80]
        if len(text) > 80:
            preview += "..."
        self._history.insertItem(0, f"{timestamp}: {preview}")
        
        # Save to disk (keep last N)
        try:
            items: List[dict] = []
            if self._history_path.exists():
                items = json.loads(self._history_path.read_text(encoding="utf-8"))
            items.append(item)
            items = items[-limit:]
            self._history_path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            logger.exception("Failed to persist history")

    def set_status(self, text: str) -> None:
        self._status_label.setText(text)
        self._status_pill.setText(text)
        self._tray.setToolTip(text)

    def _open_settings(self) -> None:
        dlg = SettingsDialog(self.settings, self)
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            dlg.apply()
            save_settings(self.settings)
            self.set_status("Einstellungen gespeichert")

    def show_tray_tip(self) -> None:
        try:
            self._tray.showMessage(
                "Speech-to-Text läuft",
                "Alt+T: Start/Stop  •  ESC: Abbrechen",
                QtWidgets.QSystemTrayIcon.Information,
                4000,
            )
        except Exception:
            pass
    
    def _show_history_detail(self, item: QtWidgets.QListWidgetItem) -> None:
        """Show full text of history item in a dialog."""
        # Get index of clicked item
        index = self._history.row(item)
        
        if 0 <= index < len(self._history_data):
            history_item = self._history_data[index]
            
            # Create dialog to show full text
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("Transkription Details")
            dialog.setMinimumWidth(600)
            dialog.setMinimumHeight(400)
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #181818;
                }
            """)
            
            # Timestamp label
            timestamp_label = QtWidgets.QLabel(history_item['timestamp'])
            timestamp_label.setStyleSheet("""
                font-size: 11pt;
                font-weight: 600;
                color: #a0a0a0;
                padding: 8px 0px;
            """)
            
            # Text area (read-only)
            text_edit = QtWidgets.QPlainTextEdit()
            text_edit.setPlainText(history_item['text'])
            text_edit.setReadOnly(True)
            text_edit.setStyleSheet("""
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
            
            # Buttons
            copy_btn = QtWidgets.QPushButton("Kopieren")
            copy_btn.setProperty("type", "primary")
            copy_btn.clicked.connect(lambda: self._copy_to_clipboard(history_item['text']))
            
            close_btn = QtWidgets.QPushButton("Schließen")
            close_btn.clicked.connect(dialog.accept)
            
            btn_layout = QtWidgets.QHBoxLayout()
            btn_layout.addWidget(copy_btn)
            btn_layout.addStretch()
            btn_layout.addWidget(close_btn)
            
            # Main layout
            layout = QtWidgets.QVBoxLayout(dialog)
            layout.setContentsMargins(24, 20, 24, 20)
            layout.setSpacing(12)
            layout.addWidget(timestamp_label)
            layout.addWidget(text_edit)
            layout.addLayout(btn_layout)
            
            dialog.exec()
    
    def _copy_to_clipboard(self, text: str) -> None:
        """Copy text to clipboard."""
        QtWidgets.QApplication.clipboard().setText(text)
        self.set_status("Text in Zwischenablage kopiert")
    
    def _open_visual_settings(self) -> None:
        """Open visual settings dialog for particle customization."""
        # Import here to avoid circular dependency
        from .ui_visual_settings import VisualSettingsDialog
        
        # Get overlay from parent (controller)
        # We'll pass this via a signal or through controller
        # For now, emit a signal
        if hasattr(self, 'visual_settings_requested'):
            self.visual_settings_requested.emit()
        else:
            # Fallback: just show a message
            self.set_status("Visuelle Einstellungen: Starte Aufnahme für Live Preview")
