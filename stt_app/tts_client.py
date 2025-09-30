"""
ElevenLabs Text-to-Speech Client
Handles audio generation from translated text
"""

import logging
from typing import Optional, Iterator
from elevenlabs.client import ElevenLabs
from elevenlabs import play, stream
import keyring

logger = logging.getLogger(__name__)

# Service name for keyring storage
KEYRING_SERVICE = "STTDesktop"
ELEVENLABS_KEY_NAME = "elevenlabs_api_key"


class TTSClient:
    """Client for ElevenLabs Text-to-Speech API."""
    
    def __init__(self) -> None:
        self._client: Optional[ElevenLabs] = None
        self._api_key: Optional[str] = None
    
    def set_api_key(self, api_key: str) -> None:
        """Set and validate ElevenLabs API key."""
        if api_key and api_key.strip():
            self._api_key = api_key.strip()
            self._client = ElevenLabs(api_key=self._api_key)
            # Store in keyring for persistence
            try:
                keyring.set_password(KEYRING_SERVICE, ELEVENLABS_KEY_NAME, self._api_key)
                logger.info("ElevenLabs API key stored in keyring")
            except Exception as e:
                logger.warning(f"Could not store ElevenLabs key in keyring: {e}")
        else:
            self._client = None
            self._api_key = None
    
    def load_api_key(self) -> bool:
        """Load API key from keyring or environment."""
        try:
            # Try keyring first
            key = keyring.get_password(KEYRING_SERVICE, ELEVENLABS_KEY_NAME)
            if key:
                self._api_key = key
                self._client = ElevenLabs(api_key=key)
                logger.info("ElevenLabs API key loaded from keyring")
                return True
            
            # Try environment variable
            import os
            key = os.getenv("ELEVENLABS_API_KEY")
            if key:
                self._api_key = key
                self._client = ElevenLabs(api_key=key)
                logger.info("ElevenLabs API key loaded from environment")
                return True
            
            logger.warning("No ElevenLabs API key found")
            return False
        except Exception as e:
            logger.error(f"Error loading ElevenLabs API key: {e}")
            return False
    
    def get_api_key(self) -> str:
        """Get current API key (for display in settings)."""
        return self._api_key or ""
    
    def is_configured(self) -> bool:
        """Check if client is configured with API key."""
        return self._client is not None
    
    def text_to_speech(
        self, 
        text: str, 
        voice_id: str = "JBFqnCBsd6RMkjVDRZzb",  # Default: George (multilingual)
        model_id: str = "eleven_multilingual_v2",
        output_format: str = "mp3_44100_128"
    ) -> Iterator[bytes]:
        """
        Convert text to speech and return audio stream.
        
        Args:
            text: Text to convert to speech
            voice_id: ElevenLabs voice ID (default: George)
            model_id: Model to use (default: eleven_multilingual_v2)
            output_format: Audio format (default: mp3_44100_128)
        
        Returns:
            Iterator of audio bytes
            
        Raises:
            ValueError: If client is not configured
            Exception: If TTS conversion fails
        """
        if not self._client:
            raise ValueError("ElevenLabs client not configured. Please set API key.")
        
        try:
            logger.info(f"Generating speech for text: {text[:50]}...")
            audio = self._client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id=model_id,
                output_format=output_format,
            )
            return audio
        except Exception as e:
            logger.error(f"TTS conversion failed: {e}")
            raise
    
    def play_audio(self, audio: Iterator[bytes]) -> None:
        """Play audio stream."""
        try:
            play(audio)
        except Exception as e:
            logger.error(f"Audio playback failed: {e}")
            raise


# Voice options for different languages
VOICE_OPTIONS = {
    "Deutsch": "pNInz6obpgDQGcFmaJgB",  # Adam (multilingual)
    "Englisch": "JBFqnCBsd6RMkjVDRZzb",  # George (multilingual)
    "Spanisch": "EXAVITQu4vr4xnSDxMaL",  # Bella (multilingual)
    "Französisch": "ThT5KcBeYPX3keUQqHPh",  # Dorothy (multilingual)
    "Italienisch": "ErXwobaYiN019PkySvjV",  # Antoni (multilingual)
    "Arabisch": "MF3mGyEYCl7XYWbV9V6O",  # Elli (multilingual)
}
