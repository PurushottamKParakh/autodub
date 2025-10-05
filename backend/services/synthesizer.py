from elevenlabs.client import ElevenLabs
import os
import logging
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

class SpeechSynthesizer:
    """Service for synthesizing speech using ElevenLabs"""
    
    def __init__(self, api_key=None, output_dir='temp'):
        self.api_key = api_key or os.getenv('ELEVENLABS_API_KEY')
        if not self.api_key:
            raise ValueError("ElevenLabs API key is required")
        
        # Initialize ElevenLabs client (SDK 1.0.0)
        self.client = ElevenLabs(api_key=self.api_key)
        self.output_dir = output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    def list_available_voices(self):
        """
        List all available voices from ElevenLabs
        
        Returns:
            list: Available voices
        """
        try:
            available_voices = self.client.voices.get_all()
            return available_voices
        except Exception as e:
            raise Exception(f"Failed to fetch voices: {str(e)}")
    
    def synthesize_text(self, text, voice_id='21m00Tcm4TlvDq8ikWAM', model='eleven_multilingual_v2'):
        """
        Synthesize speech from text
        
        Args:
            text: Text to synthesize
            voice_id: ElevenLabs voice ID (default: Rachel)
            model: Model to use (eleven_multilingual_v2 for multiple languages)
            
        Returns:
            bytes: Audio data
        """
        try:
            logger.info(f"[SYNTHESIZER] Generating speech for text: {text[:50]}...")
            logger.info(f"[SYNTHESIZER] Using voice_id: {voice_id}, model: {model}")
            
            # Use new SDK 1.0.0 API
            audio_generator = self.client.generate(
                text=text,
                voice=voice_id,
                model=model
            )
            
            # Convert generator to bytes
            audio = b''.join(audio_generator)
            
            logger.info(f"[SYNTHESIZER] Successfully generated {len(audio)} bytes of audio")
            return audio
            
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            logger.error(f"[SYNTHESIZER ERROR] Type: {error_type}")
            logger.error(f"[SYNTHESIZER ERROR] Message: {error_msg}")
            logger.error(f"[SYNTHESIZER ERROR] Full exception: {repr(e)}")
            
            # Check for specific error types
            if 'rate' in error_msg.lower() or 'limit' in error_msg.lower():
                logger.error("[SYNTHESIZER ERROR] RATE LIMIT DETECTED - ElevenLabs API quota exceeded")
            elif 'quota' in error_msg.lower():
                logger.error("[SYNTHESIZER ERROR] QUOTA EXCEEDED - ElevenLabs character limit reached")
            elif 'auth' in error_msg.lower() or 'key' in error_msg.lower():
                logger.error("[SYNTHESIZER ERROR] AUTHENTICATION ERROR - Invalid API key")
            
            raise Exception(f"Speech synthesis failed [{error_type}]: {error_msg}")
    
    def synthesize_segment(self, segment, voice_id='21m00Tcm4TlvDq8ikWAM', output_path=None):
        """
        Synthesize a single segment and save to file
        
        Args:
            segment: Segment dict with 'translated_text'
            voice_id: Voice to use
            output_path: Path to save audio file
            
        Returns:
            dict: Segment with audio_path added
        """
        try:
            text = segment.get('translated_text', segment.get('text', ''))
            
            if not text:
                raise ValueError("No text to synthesize")
            
            audio_data = self.synthesize_text(text, voice_id)
            
            # Save audio to file
            if output_path is None:
                output_path = os.path.join(
                    self.output_dir,
                    f"segment_{segment.get('start', 0):.2f}.mp3"
                )
            
            with open(output_path, 'wb') as f:
                f.write(audio_data)
            
            segment['audio_path'] = output_path
            return segment
            
        except Exception as e:
            raise Exception(f"Failed to synthesize segment: {str(e)}")
    
    def synthesize_segments(self, segments, voice_id='21m00Tcm4TlvDq8ikWAM', job_id='default'):
        """
        Synthesize multiple segments
        
        Args:
            segments: List of segments with translated text
            voice_id: Voice to use
            job_id: Job identifier for file naming
            
        Returns:
            list: Segments with audio_path added
        """
        synthesized_segments = []
        
        for i, segment in enumerate(segments):
            try:
                output_path = os.path.join(
                    self.output_dir,
                    f"{job_id}_segment_{i:04d}.mp3"
                )
                
                synthesized_segment = self.synthesize_segment(
                    segment,
                    voice_id,
                    output_path
                )
                
                synthesized_segments.append(synthesized_segment)
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"[SYNTHESIZER] Failed to synthesize segment {i}: {error_msg}")
                print(f"Warning: Failed to synthesize segment {i}: {error_msg}")
                # Add segment without audio
                synthesized_segments.append(segment)
        
        return synthesized_segments
    
    def get_voice_for_language(self, language_code):
        """
        Get recommended voice ID for a language
        
        Args:
            language_code: Language code (e.g., 'es', 'fr')
            
        Returns:
            str: Voice ID
        """
        # Default multilingual voices
        voice_map = {
            'es': '21m00Tcm4TlvDq8ikWAM',  # Rachel - works well for Spanish
            'fr': '21m00Tcm4TlvDq8ikWAM',  # Rachel - multilingual
            'de': '21m00Tcm4TlvDq8ikWAM',  # Rachel - multilingual
            'it': '21m00Tcm4TlvDq8ikWAM',  # Rachel - multilingual
            'pt': '21m00Tcm4TlvDq8ikWAM',  # Rachel - multilingual
            'default': '21m00Tcm4TlvDq8ikWAM'  # Rachel
        }
        
        return voice_map.get(language_code.lower(), voice_map['default'])
