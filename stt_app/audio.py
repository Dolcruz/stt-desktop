import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional, List

import numpy as np
import sounddevice as sd
import soundfile as sf

from .config import get_app_dir, AppSettings


@dataclass
class RecorderCallbacks:
    """Callbacks for UI/UX updates during recording.

    All callbacks are optional. They are invoked from the recording thread.
    Callers should ensure any UI updates are marshalled to the UI thread.
    """

    on_level: Optional[Callable[[float], None]] = None  # 0..1 normalized RMS
    on_time: Optional[Callable[[float], None]] = None  # seconds elapsed
    on_stopped: Optional[Callable[[Path], None]] = None  # path to WAV file
    on_cancelled: Optional[Callable[[], None]] = None
    on_error: Optional[Callable[[str], None]] = None


class AudioRecorder:
    """High-level audio recorder with silence detection and WAV output.

    - Records mono PCM at settings.sample_rate_hz and 16-bit depth
    - Stops when toggled, cancelled, max duration, or after sustained silence
    """

    def __init__(self, settings: AppSettings, callbacks: Optional[RecorderCallbacks] = None) -> None:
        self.settings = settings
        self.callbacks = callbacks or RecorderCallbacks()

        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._cancel_event = threading.Event()
        self._lock = threading.Lock()

        self._buffer: List[np.ndarray] = []
        self._start_time: float = 0.0
        self._last_level: float = 0.0
        self._silence_accumulated: float = 0.0

    def is_recording(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self) -> bool:
        if self.is_recording():
            return False
        self._stop_event.clear()
        self._cancel_event.clear()
        self._buffer = []
        self._silence_accumulated = 0.0
        self._thread = threading.Thread(target=self._run, name="AudioRecorderThread", daemon=True)
        self._thread.start()
        return True

    def stop(self) -> None:
        self._stop_event.set()

    def cancel(self) -> None:
        self._cancel_event.set()
        self._stop_event.set()

    # Internal
    def _run(self) -> None:
        try:
            self._do_record()
        except Exception as exc:
            if self.callbacks.on_error:
                try:
                    self.callbacks.on_error(str(exc))
                except Exception:
                    pass

    def _do_record(self) -> None:
        self._start_time = time.time()
        samplerate = self.settings.sample_rate_hz
        channels = self.settings.channels

        # Use minimal latency-friendly blocksize
        blocksize = 0  # let sounddevice choose
        dtype = "float32"  # use float in callback; convert to int16 on write

        def callback(indata, frames, time_info, status):
            # status may carry warnings (e.g., buffer underruns/overruns)
            # indata shape: (frames, channels)
            mono = indata[:, 0] if channels == 1 else np.mean(indata, axis=1)

            # Compute RMS level (0..1 for float32)
            rms = float(np.sqrt(np.mean(np.square(mono))))
            self._last_level = rms
            if self.callbacks.on_level:
                try:
                    self.callbacks.on_level(min(1.0, rms))
                except Exception:
                    pass

            with self._lock:
                self._buffer.append(mono.copy())

        # Try to open default device first; fallback to explicit default index
        stream_kwargs = dict(
            channels=channels,
            samplerate=samplerate,
            dtype=dtype,
            blocksize=blocksize,
            callback=callback,
        )
        # Optional: user-selected device index in settings (if present)
        device_index = getattr(self.settings, "input_device_index", None)
        if device_index is not None:
            stream_kwargs["device"] = device_index

        with sd.InputStream(**stream_kwargs):
            # Polling loop for stop conditions and time updates
            while not self._stop_event.is_set():
                elapsed = time.time() - self._start_time
                if self.callbacks.on_time:
                    try:
                        self.callbacks.on_time(elapsed)
                    except Exception:
                        pass

                # Silence detection is optional; only apply when enabled
                if getattr(self.settings, "stop_on_silence", False):
                    # Accumulate time while below threshold; reset when above
                    if self._last_level < self.settings.silence_threshold_rms:
                        self._silence_accumulated += 0.1
                    else:
                        self._silence_accumulated = 0.0

                    # Stop on sustained silence once the minimum duration is reached
                    if self._silence_accumulated >= self.settings.silence_min_seconds:
                        break

                # Respect max duration only when configured (> 0)
                if getattr(self.settings, "max_duration_seconds", 0) > 0 and elapsed >= self.settings.max_duration_seconds:
                    break

                time.sleep(0.1)

        # Determine if cancelled
        if self._cancel_event.is_set():
            if self.callbacks.on_cancelled:
                try:
                    self.callbacks.on_cancelled()
                except Exception:
                    pass
            return

        # Write WAV file
        audio = self._concatenate()
        if audio.size == 0:
            if self.callbacks.on_cancelled:
                try:
                    self.callbacks.on_cancelled()
                except Exception:
                    pass
            return

        wav_path = self._write_wav(audio)
        if self.callbacks.on_stopped:
            try:
                self.callbacks.on_stopped(wav_path)
            except Exception:
                pass

    def _concatenate(self) -> np.ndarray:
        with self._lock:
            if not self._buffer:
                return np.array([], dtype=np.float32)
            return np.concatenate(self._buffer, axis=0)

    def _write_wav(self, audio_float: np.ndarray) -> Path:
        # Convert float32 [-1,1] to int16
        audio_clipped = np.clip(audio_float, -1.0, 1.0)
        audio_int16 = (audio_clipped * 32767.0).astype(np.int16)
        wav_dir = get_app_dir() / "temp"
        wav_dir.mkdir(parents=True, exist_ok=True)
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        wav_path = wav_dir / f"recording-{timestamp}.wav"
        sf.write(file=str(wav_path), data=audio_int16, samplerate=self.settings.sample_rate_hz, subtype="PCM_16")
        return wav_path
