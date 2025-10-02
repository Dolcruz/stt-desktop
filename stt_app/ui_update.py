"""
Update Dialog UI
Shows available updates and handles download/installation
"""

import logging
from typing import Optional
from PySide6 import QtWidgets, QtCore, QtGui

logger = logging.getLogger(__name__)


class UpdateDialog(QtWidgets.QDialog):
    """Dialog to notify user of available updates and handle installation."""
    
    # Signals
    download_requested = QtCore.Signal(str)  # download_url
    
    def __init__(
        self, 
        current_version: str,
        new_version: str,
        download_url: str,
        release_notes: str,
        parent: Optional[QtWidgets.QWidget] = None
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Update verfügbar")
        self.setWindowFlag(QtCore.Qt.Window)
        self.setMinimumWidth(550)
        self.setMinimumHeight(400)
        
        self._download_url = download_url
        self._downloading = False
        
        # Dark mode styling
        self.setStyleSheet("""
            QDialog { background-color: #181818; }
        """)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        
        # Title with icon
        title_layout = QtWidgets.QHBoxLayout()
        title_icon = QtWidgets.QLabel("🔄")
        title_icon.setStyleSheet("font-size: 32pt;")
        
        title_text = QtWidgets.QLabel("Update verfügbar!")
        title_text.setStyleSheet("""
            font-size: 18pt; font-weight: 700; color: #4287f5;
        """)
        
        title_layout.addWidget(title_icon)
        title_layout.addWidget(title_text)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Version info
        version_info = QtWidgets.QLabel(
            f"📦 Neue Version: <b>{new_version}</b><br>"
            f"📁 Aktuelle Version: {current_version}"
        )
        version_info.setStyleSheet("""
            font-size: 11pt; color: #f0f0f0; padding: 12px;
            background-color: #242424; border-radius: 8px;
        """)
        layout.addWidget(version_info)
        
        # Release notes
        notes_label = QtWidgets.QLabel("📝 Was ist neu:")
        notes_label.setStyleSheet("font-size: 11pt; font-weight: 600; color: #f0f0f0; padding: 8px 0px;")
        layout.addWidget(notes_label)
        
        self._notes_text = QtWidgets.QPlainTextEdit()
        self._notes_text.setPlainText(release_notes)
        self._notes_text.setReadOnly(True)
        self._notes_text.setStyleSheet("""
            QPlainTextEdit {
                background-color: #242424; border: 2px solid #4a4a4a; border-radius: 8px;
                padding: 12px; font-size: 10pt; color: #d0d0d0;
            }
        """)
        layout.addWidget(self._notes_text, stretch=1)
        
        # Progress bar (hidden initially)
        self._progress_bar = QtWidgets.QProgressBar()
        self._progress_bar.setMinimum(0)
        self._progress_bar.setMaximum(100)
        self._progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #2a2a2a; border: none; border-radius: 5px; height: 24px;
                text-align: center; color: #ffffff; font-weight: 600;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4287f5, stop:1 #6ab4ff);
                border-radius: 5px;
            }
        """)
        self._progress_bar.hide()
        layout.addWidget(self._progress_bar)
        
        # Status label
        self._status_label = QtWidgets.QLabel("")
        self._status_label.setAlignment(QtCore.Qt.AlignCenter)
        self._status_label.setStyleSheet("color: #a0a0a0; font-size: 9pt; padding: 6px 0px;")
        layout.addWidget(self._status_label)
        
        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(12)
        
        self._update_btn = QtWidgets.QPushButton("✓ Jetzt updaten")
        self._update_btn.setStyleSheet("""
            QPushButton {
                background-color: #4287f5; color: #ffffff; font-weight: 600;
                padding: 12px 24px; border-radius: 8px; font-size: 11pt;
            }
            QPushButton:hover { background-color: #3a7ae0; }
            QPushButton:disabled { background-color: #3a3a3a; color: #808080; }
        """)
        self._update_btn.clicked.connect(self._on_update_clicked)
        
        self._later_btn = QtWidgets.QPushButton("Später")
        self._later_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a; color: #f0f0f0; font-weight: 600;
                padding: 12px 24px; border-radius: 8px; font-size: 11pt;
            }
            QPushButton:hover { background-color: #4a4a4a; }
        """)
        self._later_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self._later_btn)
        btn_layout.addWidget(self._update_btn)
        layout.addLayout(btn_layout)
    
    def _on_update_clicked(self) -> None:
        """Handle update button click."""
        if not self._downloading:
            self._downloading = True
            self._update_btn.setEnabled(False)
            self._later_btn.setEnabled(False)
            self._progress_bar.show()
            self._status_label.setText("Download wird vorbereitet...")
            self.download_requested.emit(self._download_url)
    
    @QtCore.Slot(int, int)
    def update_progress(self, downloaded: int, total: int) -> None:
        """Update download progress bar."""
        if total > 0:
            progress = int((downloaded / total) * 100)
            self._progress_bar.setValue(progress)
            
            # Format sizes
            mb_downloaded = downloaded / (1024 * 1024)
            mb_total = total / (1024 * 1024)
            self._status_label.setText(f"Download läuft... {mb_downloaded:.1f} MB / {mb_total:.1f} MB")
    
    @QtCore.Slot()
    def download_complete(self) -> None:
        """Handle download completion."""
        self._progress_bar.setValue(100)
        self._status_label.setText("✓ Download abgeschlossen! Update wird installiert...")
    
    @QtCore.Slot(str)
    def download_error(self, error_msg: str) -> None:
        """Handle download error."""
        self._progress_bar.hide()
        self._status_label.setText(f"❌ Fehler: {error_msg}")
        self._update_btn.setEnabled(True)
        self._later_btn.setEnabled(True)
        self._downloading = False

