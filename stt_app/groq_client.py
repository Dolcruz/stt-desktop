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

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type(Exception),
    )
    def correct_grammar(self, text: str) -> str:
        """Correct grammar of the provided text using Groq's LLM.
        
        Uses the kimi-k2-instruct model to correct grammar while preserving meaning.
        Returns the corrected text only, without any additional commentary.
        """
        client = self._ensure_client()
        
        # Craft a precise prompt that ensures ONLY corrected text is returned
        system_prompt = (
            "Du bist ein präziser Grammatik-Korrektor. "
            "Korrigiere NUR die Grammatik, Rechtschreibung und Zeichensetzung des Textes. "
            "Gib AUSSCHLIESSLICH den korrigierten Text zurück, ohne Kommentare, Erklärungen oder zusätzliche Formatierung. "
            "Verändere den Inhalt oder die Bedeutung NICHT."
        )
        
        user_message = f"Korrigiere diesen Text: {text}"
        
        # Collect the streamed response
        corrected_text = ""
        try:
            completion = client.chat.completions.create(
                model="moonshotai/kimi-k2-instruct-0905",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,  # Lower temperature for more consistent corrections
                max_completion_tokens=4096,
                top_p=1,
                stream=True,
                stop=None
            )
            
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    corrected_text += chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"Grammar correction failed: {e}")
            # Return original text on error
            return text
            
        # Return the corrected text, stripped of any leading/trailing whitespace
        result = corrected_text.strip()
        logger.info(f"Grammar correction: '{text}' → '{result}'")
        return result if result else text

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type(Exception),
    )
    def translate_text(self, text: str, target_language: str) -> str:
        """Translate the provided text to the target language using Groq's LLM.
        
        Uses the kimi-k2-instruct model to translate text accurately.
        Returns ONLY the translated text without any additional commentary.
        
        Args:
            text: The text to translate
            target_language: Target language (e.g., "Englisch", "Spanisch", "Arabisch", etc.)
        
        Returns:
            The translated text
        """
        client = self._ensure_client()
        
        # Craft a precise prompt that ensures ONLY translated text is returned
        system_prompt = (
            "Du bist ein präziser Übersetzer. "
            f"Übersetze den folgenden Text AUSSCHLIESSLICH in {target_language}. "
            "Gib NUR die Übersetzung zurück, ohne Kommentare, Erklärungen oder zusätzliche Formatierung. "
            "Behalte die Bedeutung und den Ton des Originaltextes bei."
        )
        
        user_message = f"Übersetze diesen Text in {target_language}: {text}"
        
        # Collect the streamed response
        translated_text = ""
        try:
            completion = client.chat.completions.create(
                model="moonshotai/kimi-k2-instruct-0905",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,  # Lower temperature for more consistent translations
                max_completion_tokens=4096,
                top_p=1,
                stream=True,
                stop=None
            )
            
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    translated_text += chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            # Return original text on error
            return text
            
        # Return the translated text, stripped of any leading/trailing whitespace
        result = translated_text.strip()
        logger.info(f"Translation to {target_language}: '{text}' → '{result}'")
        return result if result else text
