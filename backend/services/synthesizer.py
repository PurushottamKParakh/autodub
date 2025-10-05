from elevenlabs.client import ElevenLabs
import os
import logging
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

# Voice pools for multi-speaker support
# Each language has multiple voices (different genders/tones)
VOICE_POOLS = {
    'en': [
        '21m00Tcm4TlvDq8ikWAM',  # Rachel - Female
        'pNInz6obpgDQGcFmaJgB',  # Adam - Male
        'EXAVITQu4vr4xnSDxMaL',  # Bella - Female
        'VR6AewLTigWG4xSOukaG',  # Arnold - Male
    ],
    'es': [
        '21m00Tcm4TlvDq8ikWAM',  # Rachel - Multilingual Female
        'pNInz6obpgDQGcFmaJgB',  # Adam - Multilingual Male
        'EXAVITQu4vr4xnSDxMaL',  # Bella - Multilingual Female
        'VR6AewLTigWG4xSOukaG',  # Arnold - Multilingual Male
    ],
    'fr': [
        '21m00Tcm4TlvDq8ikWAM',  # Rachel - Multilingual
        'pNInz6obpgDQGcFmaJgB',  # Adam - Multilingual
        'EXAVITQu4vr4xnSDxMaL',  # Bella - Multilingual
        'VR6AewLTigWG4xSOukaG',  # Arnold - Multilingual
    ],
    'de': [
        '21m00Tcm4TlvDq8ikWAM',  # Rachel - Multilingual
        'pNInz6obpgDQGcFmaJgB',  # Adam - Multilingual
        'EXAVITQu4vr4xnSDxMaL',  # Bella - Multilingual
        'VR6AewLTigWG4xSOukaG',  # Arnold - Multilingual
    ],
    'it': [
        '21m00Tcm4TlvDq8ikWAM',  # Rachel - Multilingual
        'pNInz6obpgDQGcFmaJgB',  # Adam - Multilingual
        'EXAVITQu4vr4xnSDxMaL',  # Bella - Multilingual
        'VR6AewLTigWG4xSOukaG',  # Arnold - Multilingual
    ],
    'pt': [
        '21m00Tcm4TlvDq8ikWAM',  # Rachel - Multilingual
        'pNInz6obpgDQGcFmaJgB',  # Adam - Multilingual
        'EXAVITQu4vr4xnSDxMaL',  # Bella - Multilingual
        'VR6AewLTigWG4xSOukaG',  # Arnold - Multilingual
    ],
    'hi': [
        '21m00Tcm4TlvDq8ikWAM',  # Rachel - Multilingual Female
        'pNInz6obpgDQGcFmaJgB',  # Adam - Multilingual Male
        'EXAVITQu4vr4xnSDxMaL',  # Bella - Multilingual Female
        'VR6AewLTigWG4xSOukaG',  # Arnold - Multilingual Male
    ],
    'ja': [
        '21m00Tcm4TlvDq8ikWAM',  # Rachel - Multilingual
        'pNInz6obpgDQGcFmaJgB',  # Adam - Multilingual
        'EXAVITQu4vr4xnSDxMaL',  # Bella - Multilingual
        'VR6AewLTigWG4xSOukaG',  # Arnold - Multilingual
    ],
    'ko': [
        '21m00Tcm4TlvDq8ikWAM',  # Rachel - Multilingual
        'pNInz6obpgDQGcFmaJgB',  # Adam - Multilingual
        'EXAVITQu4vr4xnSDxMaL',  # Bella - Multilingual
        'VR6AewLTigWG4xSOukaG',  # Arnold - Multilingual
    ],
    'zh': [
        '21m00Tcm4TlvDq8ikWAM',  # Rachel - Multilingual
        'pNInz6obpgDQGcFmaJgB',  # Adam - Multilingual
        'EXAVITQu4vr4xnSDxMaL',  # Bella - Multilingual
        'VR6AewLTigWG4xSOukaG',  # Arnold - Multilingual
    ],
    'ar': [
        '21m00Tcm4TlvDq8ikWAM',  # Rachel - Multilingual
        'pNInz6obpgDQGcFmaJgB',  # Adam - Multilingual
        'EXAVITQu4vr4xnSDxMaL',  # Bella - Multilingual
        'VR6AewLTigWG4xSOukaG',  # Arnold - Multilingual
    ],
    'ru': [
        '21m00Tcm4TlvDq8ikWAM',  # Rachel - Multilingual
        'pNInz6obpgDQGcFmaJgB',  # Adam - Multilingual
        'EXAVITQu4vr4xnSDxMaL',  # Bella - Multilingual
        'VR6AewLTigWG4xSOukaG',  # Arnold - Multilingual
    ],
    'default': [
        '21m00Tcm4TlvDq8ikWAM',  # Rachel
        'pNInz6obpgDQGcFmaJgB',  # Adam
        'EXAVITQu4vr4xnSDxMaL',  # Bella
        'VR6AewLTigWG4xSOukaG',  # Arnold
    ]
}

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
        
        # Speaker to voice mapping (populated during synthesis)
        self.speaker_voice_map = {}
    
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
    
    def synthesize_segments(self, segments, voice_id='21m00Tcm4TlvDq8ikWAM', job_id='default', 
                           language_code='en', multi_speaker=True):
        """
        Synthesize multiple segments with optional multi-speaker support
        
        Args:
            segments: List of segments with translated text
            voice_id: Default voice to use (fallback for single speaker)
            job_id: Job identifier for file naming
            language_code: Target language code
            multi_speaker: Enable multi-speaker voice assignment
            
        Returns:
            list: Segments with audio_path added
        """
        synthesized_segments = []
        
        # Detect if we have multi-speaker content
        speakers = set(segment.get('speaker', 0) for segment in segments)
        has_multiple_speakers = len(speakers) > 1
        
        if has_multiple_speakers and multi_speaker:
            logger.info(f"[SYNTHESIZER] Multi-speaker mode: {len(speakers)} speakers detected")
            # Assign voices to speakers
            self._assign_voices_to_speakers(speakers, language_code)
        else:
            logger.info(f"[SYNTHESIZER] Single-speaker mode")
            # Use default voice for all
            self.speaker_voice_map = {0: voice_id}
        
        for i, segment in enumerate(segments):
            try:
                # Get voice for this segment's speaker
                speaker_id = segment.get('speaker', 0)
                segment_voice_id = self.speaker_voice_map.get(speaker_id, voice_id)
                
                output_path = os.path.join(
                    self.output_dir,
                    f"{job_id}_segment_{i:04d}.mp3"
                )
                
                logger.info(f"[SYNTHESIZER] Segment {i}: Speaker {speaker_id} → Voice {segment_voice_id[:8]}...")
                
                synthesized_segment = self.synthesize_segment(
                    segment,
                    segment_voice_id,
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
    
    def _assign_voices_to_speakers(self, speakers, language_code):
        """
        Assign different voices to different speakers
        
        Args:
            speakers: Set of speaker IDs
            language_code: Target language code
        """
        # Get voice pool for this language
        voice_pool = VOICE_POOLS.get(language_code.lower(), VOICE_POOLS['default'])
        
        # Assign voices to speakers (cycle through pool if more speakers than voices)
        sorted_speakers = sorted(speakers)
        for idx, speaker_id in enumerate(sorted_speakers):
            voice_idx = idx % len(voice_pool)
            self.speaker_voice_map[speaker_id] = voice_pool[voice_idx]
            logger.info(f"[SYNTHESIZER] Speaker {speaker_id} → Voice {voice_pool[voice_idx][:8]}...")
    
    def get_voice_for_language(self, language_code):
        """
        Get recommended default voice ID for a language
        
        Args:
            language_code: Language code (e.g., 'es', 'fr')
            
        Returns:
            str: Voice ID (first voice from pool)
        """
        voice_pool = VOICE_POOLS.get(language_code.lower(), VOICE_POOLS['default'])
        return voice_pool[0]  # Return first voice as default
    
    def synthesize_segments_with_cloned_voices(self, segments, cloned_voices, 
                                              language_code='en', model='eleven_multilingual_v2'):
        """
        Synthesize segments using cloned voices
        
        Args:
            segments: List of segments to synthesize
            cloned_voices: dict {speaker_id: voice_id} mapping
            language_code: Target language code
            model: ElevenLabs model to use
            
        Returns:
            list: Segments with audio_path added
        """
        try:
            logger.info(f"[SYNTHESIZER] Synthesizing with cloned voices")
            logger.info(f"[SYNTHESIZER] Cloned voices: {cloned_voices}")
            logger.info(f"[SYNTHESIZER] Segments to synthesize: {len(segments)}")
            
            synthesized_segments = []
            
            for i, segment in enumerate(segments):
                speaker = segment.get('speaker', 0)
                text = segment.get('translated_text') or segment.get('text', '')
                
                if not text:
                    logger.warning(f"[SYNTHESIZER] Segment {i} has no text, skipping")
                    synthesized_segments.append(segment)
                    continue
                
                # Get cloned voice for this speaker
                voice_id = cloned_voices.get(speaker)
                
                if not voice_id:
                    logger.warning(
                        f"[SYNTHESIZER] No cloned voice for speaker {speaker}, "
                        f"using default voice"
                    )
                    voice_id = self.default_voice_id
                
                logger.info(f"[SYNTHESIZER] Segment {i}: Speaker {speaker} → Voice {voice_id[:8]}...")
                logger.info(f"[SYNTHESIZER] Generating speech for text: {text[:50]}...")
                logger.info(f"[SYNTHESIZER] Using voice_id: {voice_id}, model: {model}")
                
                # Generate speech
                audio_data = self.client.text_to_speech.convert(
                    voice_id=voice_id,
                    text=text,
                    model_id=model,
                    output_format='mp3_44100_128'
                )
                
                # Save audio to file
                audio_path = os.path.join(
                    self.output_dir,
                    f'segment_{i}_{speaker}.mp3'
                )
                
                # Write audio data
                with open(audio_path, 'wb') as f:
                    for chunk in audio_data:
                        f.write(chunk)
                
                audio_size = os.path.getsize(audio_path)
                logger.info(f"[SYNTHESIZER] Successfully generated {audio_size} bytes of audio")
                
                # Add audio path to segment
                segment['audio_path'] = audio_path
                synthesized_segments.append(segment)
            
            logger.info(f"[SYNTHESIZER] ✅ Synthesized {len(synthesized_segments)} segments with cloned voices")
            return synthesized_segments
            
        except Exception as e:
            logger.error(f"[SYNTHESIZER] ❌ Synthesis failed: {str(e)}")
            raise
