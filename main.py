from __future__ import annotations

import logging
import threading
import time
from pathlib import Path

from PySide6 import QtCore, QtWidgets, QtGui

from stt_app.config import load_settings, save_settings, get_api_key_secure
from stt_app.logger import configure_logging
from stt_app.audio import AudioRecorder, RecorderCallbacks
from stt_app.groq_client import GroqTranscriber
from stt_app.hotkeys import HotkeyManager
from stt_app.ui_main import MainWindow
from stt_app.ui_overlay import RecordingOverlay
from stt_app.ui_result_popup import ResultPopup
from stt_app.theme import apply_dark_theme


class Controller(QtCore.QObject):
    """Glue layer connecting hotkeys, recorder, transcriber, and UI."""

    def __init__(self, app: QtWidgets.QApplication) -> None:
        super().__init__()
        self.app = app
        self.settings = load_settings()

        self.window = MainWindow(self.settings)
        self.overlay = RecordingOverlay()
        
        # Apply saved visualization settings
        self.overlay._particle_sphere.set_particle_count(self.settings.particle_count)
        self.overlay._particle_sphere.set_glow_intensity(self.settings.glow_intensity)
        self.overlay._particle_sphere.set_color_hue(self.settings.particle_color_hue)
        
        self.hotkeys = HotkeyManager()
        self.transcriber = GroqTranscriber(self.settings)

        self.recorder = AudioRecorder(
            settings=self.settings,
            callbacks=RecorderCallbacks(
                on_level=self._on_level,
                on_time=self._on_time,
                on_stopped=self._on_stopped,
                on_cancelled=self._on_cancelled,
                on_error=self._on_record_error,
            ),
        )

        # Hook UI signals first
        self.window.start_stop_requested.connect(self.toggle_recording)
        self.window.cancel_requested.connect(self.cancel_recording)
        self.overlay.cancel_requested.connect(self.cancel_recording)
        
        # Hook visual settings button
        self.window._visual_settings_btn.clicked.disconnect()  # Remove default connection
        self.window._visual_settings_btn.clicked.connect(self.open_visual_settings)

        # Show window immediately so the app is visible, regardless of hotkey registration
        self.window.show()
        self.window.raise_()
        self.window.activateWindow()
        QtCore.QTimer.singleShot(300, self.window.show_tray_tip)
        self.window.set_status("Bereit")

        # Register global hotkeys in a background thread to avoid any UI freeze
        threading.Thread(target=self._register_hotkeys_bg, name="HotkeyRegister", daemon=True).start()

    def _register_hotkeys_bg(self) -> None:
        def do_register():
            # Ensure hotkey handlers run on the UI thread even if the hotkey
            # library invokes them from a background thread.
            def invoke_toggle() -> None:
                QtCore.QMetaObject.invokeMethod(self, "toggle_recording", QtCore.Qt.QueuedConnection)

            def invoke_cancel() -> None:
                QtCore.QMetaObject.invokeMethod(self, "cancel_recording", QtCore.Qt.QueuedConnection)

            ok = self.hotkeys.register(
                toggle_hotkey=self.settings.toggle_hotkey,
                cancel_key=self.settings.cancel_key,
                on_toggle=invoke_toggle,
                on_cancel=invoke_cancel,
            )
            if not ok:
                # Inform user that global hotkeys are not available
                # but local shortcuts still work when window is focused
                QtCore.QMetaObject.invokeMethod(
                    self.window,
                    "set_status",
                    QtCore.Qt.QueuedConnection,
                    QtCore.Q_ARG(str, "Bereit • Tastenkürzel funktionieren wenn Fenster im Fokus ist"),
                )
            else:
                # Global hotkeys are active
                QtCore.QMetaObject.invokeMethod(
                    self.window,
                    "set_status",
                    QtCore.Qt.QueuedConnection,
                    QtCore.Q_ARG(str, "Bereit • Globale Hotkeys aktiv"),
                )
        # Delay a bit so UI can settle
        time.sleep(0.4)
        do_register()

    # Event handlers from recorder (called on recorder thread)
    def _on_level(self, level: float) -> None:
        QtCore.QMetaObject.invokeMethod(
            self.overlay, "update_level", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(float, level)
        )

    def _on_time(self, seconds: float) -> None:
        QtCore.QMetaObject.invokeMethod(
            self.overlay, "update_time", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(float, seconds)
        )

    def _on_stopped(self, wav_path: Path) -> None:
        # Switch to processing state on UI
        QtCore.QMetaObject.invokeMethod(
            self, "_start_transcription", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, str(wav_path))
        )

    def _on_cancelled(self) -> None:
        QtCore.QMetaObject.invokeMethod(self, "_cancelled_ui", QtCore.Qt.QueuedConnection)

    @QtCore.Slot()
    def _cancelled_ui(self) -> None:
        self.overlay.hide()
        self.window.set_status("Abgebrochen")

    def _on_record_error(self, message: str) -> None:
        QtCore.QMetaObject.invokeMethod(
            self, "_record_error_ui", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, message)
        )

    @QtCore.Slot(str)
    def _record_error_ui(self, message: str) -> None:
        self.overlay.hide()
        self.window.set_status(f"Audiofehler: {message}")

    @QtCore.Slot(str)
    def _start_transcription(self, wav_path_str: str) -> None:
        self.overlay.hide()
        self.window.set_status("Transkribiere…")

        def worker() -> None:
            text = ""
            try:
                result = self.transcriber.transcribe_wav(Path(wav_path_str))
                text = result.text or ""
            except Exception as exc:
                text = f"Fehler bei der Transkription: {exc}"
            finally:
                # Clean up temp file
                try:
                    Path(wav_path_str).unlink(missing_ok=True)
                except Exception:
                    pass
            QtCore.QMetaObject.invokeMethod(
                self, "_show_result", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, text)
            )

        threading.Thread(target=worker, name="TranscriptionThread", daemon=True).start()

    @QtCore.Slot(str)
    def _show_result(self, text: str) -> None:
        self.window.set_status("Fertig")
        popup = ResultPopup(text=text, auto_close_seconds=self.settings.auto_close_popup_seconds, parent=self.window)
        if self.settings.auto_copy:
            QtWidgets.QApplication.clipboard().setText(text)
        if self.settings.auto_paste:
            # Paste after brief delay to allow popup to render (avoid pasting into popup)
            QtCore.QTimer.singleShot(200, lambda: self.hotkeys.send_paste())
        popup.exec()
        # Append to history
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.window.append_history(timestamp, popup.get_text(), self.settings.history_limit)

    # Public controls
    @QtCore.Slot()
    def toggle_recording(self) -> None:
        if self.recorder.is_recording():
            self.window.set_status("Stoppe Aufnahme…")
            self.recorder.stop()
            return
        # Start
        started = self.recorder.start()
        if started:
            self.overlay.show_top_right()
            self.window.set_status("Aufnahme läuft… (Alt+T zum Stoppen)")

    @QtCore.Slot()
    def cancel_recording(self) -> None:
        if self.recorder.is_recording():
            self.window.set_status("Abbreche…")
            self.recorder.cancel()
    
    @QtCore.Slot()
    def open_visual_settings(self) -> None:
        """Open visual settings dialog with REAL microphone preview."""
        from stt_app.ui_visual_settings import VisualSettingsDialog
        
        # Show overlay for live preview
        self.overlay.show_top_right()
        
        # Start REAL audio monitoring for preview (like actual recording but don't save)
        # Use the recorder's audio monitoring without actually recording
        import sounddevice as sd
        import numpy as np
        
        self._preview_stream = None
        
        def audio_callback(indata, frames, time_info, status):
            """Process real microphone input for preview."""
            if status:
                return
            # Calculate RMS level from audio data (same as real recording)
            audio_data = indata[:, 0] if len(indata.shape) > 1 else indata
            rms = float(np.sqrt(np.mean(audio_data**2)))
            # Normalize to 0-1 range (same normalization as recorder)
            normalized_level = min(1.0, rms * 50)  # Scale factor like in audio.py
            # Update overlay with REAL audio level
            QtCore.QMetaObject.invokeMethod(
                self.overlay._particle_sphere, 
                "set_level", 
                QtCore.Qt.QueuedConnection, 
                QtCore.Q_ARG(float, normalized_level)
            )
        
        try:
            # Start audio stream with same settings as recorder
            self._preview_stream = sd.InputStream(
                samplerate=self.settings.sample_rate_hz,
                channels=self.settings.channels,
                callback=audio_callback,
                blocksize=int(self.settings.sample_rate_hz * 0.1),  # 100ms blocks
                device=self.settings.input_device_index
            )
            self._preview_stream.start()
        except Exception as e:
            # Fallback if audio fails
            import logging
            logging.getLogger(__name__).warning("Could not start audio preview: %s", e)
        
        # Create and show settings dialog with current settings
        dialog = VisualSettingsDialog(
            particle_count=self.settings.particle_count,
            glow_intensity=self.settings.glow_intensity,
            color_hue=self.settings.particle_color_hue,
            parent=self.window
        )
        
        # Connect live update signals
        dialog.particle_count_changed.connect(self.overlay._particle_sphere.set_particle_count)
        dialog.glow_intensity_changed.connect(self.overlay._particle_sphere.set_glow_intensity)
        dialog.color_hue_changed.connect(self.overlay._particle_sphere.set_color_hue)
        
        # Execute dialog
        result = dialog.exec()
        
        # Stop REAL audio preview
        if self._preview_stream:
            try:
                self._preview_stream.stop()
                self._preview_stream.close()
            except Exception:
                pass
            self._preview_stream = None
        
        self.overlay.hide()
        
        # Save settings if user clicked OK
        if result == QtWidgets.QDialog.Accepted:
            count, glow, hue = dialog.get_values()
            self.settings.particle_count = count
            self.settings.glow_intensity = glow
            self.settings.particle_color_hue = hue
            save_settings(self.settings)
            self.window.set_status("Visualisierungs-Einstellungen gespeichert")
        else:
            # Reset to saved settings if cancelled
            self.overlay._particle_sphere.set_particle_count(self.settings.particle_count)
            self.overlay._particle_sphere.set_glow_intensity(self.settings.glow_intensity)
            self.overlay._particle_sphere.set_color_hue(self.settings.particle_color_hue)
            self.window.set_status("Einstellungen verworfen")


def main() -> None:
    log_path = configure_logging()
    logging.getLogger(__name__).info("Starting app; logs at %s", log_path)

    # High DPI support - removed deprecated attributes
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts, True)

    app = QtWidgets.QApplication([])
    apply_dark_theme(app)
    controller = Controller(app)
    app.exec()


if __name__ == "__main__":
    main()
