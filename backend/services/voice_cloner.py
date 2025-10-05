import os
import logging
from elevenlabs.client import ElevenLabs

logger = logging.getLogger(__name__)

class VoiceCloner:
    """Clone voices using ElevenLabs Professional Voice Cloning"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('ELEVENLABS_API_KEY')
        if not self.api_key:
            raise ValueError("ElevenLabs API key is required")
        
        self.client = ElevenLabs(api_key=self.api_key)
        logger.info(f"[VOICE_CLONER] Initialized with API key: {self.api_key[:10]}...")
    
    def clone_voice(self, audio_path, voice_name, description=""):
        """
        Clone a voice using ElevenLabs Professional Voice Cloning
        
        Args:
            audio_path: Path to speaker audio sample (WAV file)
            voice_name: Name for the cloned voice
            description: Optional description of the voice
            
        Returns:
            str: voice_id of the cloned voice
        """
        try:
            logger.info(f"[VOICE_CLONER] Cloning voice: {voice_name}")
            logger.info(f"[VOICE_CLONER] Audio sample: {audio_path}")
            
            # Verify audio file exists
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            # Get file size for logging
            file_size = os.path.getsize(audio_path) / (1024 * 1024)  # MB
            logger.info(f"[VOICE_CLONER] Audio file size: {file_size:.2f} MB")
            
            # Open audio file
            with open(audio_path, 'rb') as audio_file:
                # Clone voice using ElevenLabs API
                voice = self.client.voices.add(
                    name=voice_name,
                    description=description or f"Cloned voice for {voice_name}",
                    files=[audio_file]
                )
            
            voice_id = voice.voice_id
            logger.info(f"[VOICE_CLONER] ✅ Voice cloned successfully")
            logger.info(f"[VOICE_CLONER] Voice ID: {voice_id}")
            logger.info(f"[VOICE_CLONER] Voice Name: {voice_name}")
            
            return voice_id
            
        except Exception as e:
            logger.error(f"[VOICE_CLONER] ❌ Voice cloning failed: {str(e)}")
            raise Exception(f"Voice cloning failed: {str(e)}")
    
    def list_voices(self):
        """
        List all available voices (including cloned ones)
        
        Returns:
            list: List of voice objects
        """
        try:
            voices = self.client.voices.get_all()
            logger.info(f"[VOICE_CLONER] Found {len(voices.voices)} voices")
            return voices.voices
        except Exception as e:
            logger.error(f"[VOICE_CLONER] ❌ Failed to list voices: {str(e)}")
            return []
    
    def delete_voice(self, voice_id):
        """
        Delete a cloned voice
        
        Args:
            voice_id: ID of the voice to delete
        """
        try:
            self.client.voices.delete(voice_id)
            logger.info(f"[VOICE_CLONER] ✅ Deleted voice: {voice_id}")
        except Exception as e:
            logger.error(f"[VOICE_CLONER] ❌ Failed to delete voice: {str(e)}")
    
    def get_voice_info(self, voice_id):
        """
        Get information about a specific voice
        
        Args:
            voice_id: ID of the voice
            
        Returns:
            dict: Voice information
        """
        try:
            voice = self.client.voices.get(voice_id)
            return {
                'voice_id': voice.voice_id,
                'name': voice.name,
                'category': voice.category,
                'description': voice.description
            }
        except Exception as e:
            logger.error(f"[VOICE_CLONER] ❌ Failed to get voice info: {str(e)}")
            return None
