from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from groq import Groq

from .config import get_api_key_secure, AppSettings

logger = logging.getLogger(__name__)

# SECURITY NOTE: No fallback API key included for security reasons.
# Users must configure their own Groq API key via the UI settings or environment variable GROQ_API_KEY.
FALLBACK_API_KEY = None


@dataclass
class TranscriptionResult:
    text: str
    raw: dict


class GroqTranscriber:
    """Wrapper around Groq SDK for Whisper transcription.

    Uses retries on transient failures and returns the transcribed text.
    Lazily initializes the underlying client to avoid UI-thread stalls.
    """

    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings
        self._client: Optional[Groq] = None

    def _ensure_client(self) -> Groq:
        if self._client is not None:
            return self._client
        api_key = get_api_key_secure()
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not configured. Please set your API key via:\n"
                "1. UI Settings (Main Window → Groq API Key field)\n"
                "2. Environment variable: GROQ_API_KEY=your_key_here\n"
                "Get your API key from: https://console.groq.com/keys"
            )
        logger.info("Using GROQ_API_KEY from keyring/env.")
        self._client = Groq(api_key=api_key)
        return self._client

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type(Exception),
    )
    def transcribe_wav(self, wav_path: Path) -> TranscriptionResult:
        client = self._ensure_client()
        model = self.settings.model
        response_format = self.settings.response_format
        language = self.settings.language

        with open(wav_path, "rb") as fp:
            transcription = client.audio.transcriptions.create(
                file=(str(wav_path.name), fp.read()),
                model=model,
                response_format=response_format,
                # language parameter: only include if provided
                **({"language": language} if language else {}),
            )
        # The SDK returns an object; ensure we can access text
        text = getattr(transcription, "text", "")
        # Convert to plain dict for optional history; robustly handle attr access
        try:
            raw = json.loads(transcription.json())  # type: ignore[attr-defined]
        except Exception:
            # best-effort
            raw = {"text": text}
        return TranscriptionResult(text=text, raw=raw)
