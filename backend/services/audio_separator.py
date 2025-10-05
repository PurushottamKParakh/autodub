import subprocess
import os
from pathlib import Path
import logging
import torch

logger = logging.getLogger(__name__)

class AudioSeparator:
    """Service for separating vocals from background music using Demucs"""
    
    def __init__(self, temp_dir='temp'):
        self.temp_dir = temp_dir
        Path(temp_dir).mkdir(parents=True, exist_ok=True)
        self.output_dir = os.path.join(temp_dir, 'separated')
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        # Check if MPS (Apple Silicon GPU) is available
        self.device = 'mps' if torch.backends.mps.is_available() else 'cpu'
        logger.info(f"[SEPARATOR] Initializing AudioSeparator with device: {self.device}")
    
    def separate_audio(self, audio_path, job_id):
        """
        Separate audio into vocals and background music
        Uses Apple M4 GPU acceleration automatically
        
        Args:
            audio_path: Path to original audio file
            job_id: Job identifier for file naming
            
        Returns:
            dict: Paths to separated audio files
        """
        try:
            logger.info(f"[SEPARATOR] Starting audio separation for {audio_path}")
            logger.info(f"[SEPARATOR] Using device: {self.device.upper()}")
            
            # Demucs command with device specification
            cmd = [
                'demucs',
                '--two-stems=vocals',
                '-n', 'htdemucs',
                '-d', self.device,
                '-o', self.output_dir,
                audio_path
            ]
            
            logger.info(f"[SEPARATOR] Running Demucs separation...")
            
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            
            logger.info(f"[SEPARATOR] ✅ Demucs separation completed")
            
            # Get separated files
            audio_filename = Path(audio_path).stem
            separated_dir = os.path.join(self.output_dir, 'htdemucs', audio_filename)
            
            vocals_path = os.path.join(separated_dir, 'vocals.wav')
            background_path = os.path.join(separated_dir, 'no_vocals.wav')
            
            if not os.path.exists(vocals_path):
                raise Exception(f"Vocals file not found: {vocals_path}")
            
            if not os.path.exists(background_path):
                raise Exception(f"Background file not found: {background_path}")
            
            logger.info(f"[SEPARATOR] ✅ Vocals extracted: {vocals_path}")
            logger.info(f"[SEPARATOR] ✅ Background extracted: {background_path}")
            
            return {
                'vocals': vocals_path,
                'background': background_path
            }
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            logger.error(f"[SEPARATOR] ❌ Demucs failed: {error_msg}")
            raise Exception(f"Audio separation failed: {error_msg}")
        except Exception as e:
            logger.error(f"[SEPARATOR] ❌ Error: {str(e)}")
            raise
    
    def mix_vocals_with_background(self, dubbed_vocals_path, background_path, output_path, 
                                   vocals_volume=1.0, background_volume=0.7):
        """
        Mix dubbed vocals with original background music
        
        Args:
            dubbed_vocals_path: Path to dubbed vocals audio
            background_path: Path to background music
            output_path: Path to save mixed audio
            vocals_volume: Volume multiplier for vocals (0.0-2.0)
            background_volume: Volume multiplier for background (0.0-2.0)
            
        Returns:
            str: Path to mixed audio file
        """
        try:
            logger.info(f"[SEPARATOR] Mixing dubbed vocals with background music")
            logger.info(f"[SEPARATOR] Vocals volume: {vocals_volume}, Background volume: {background_volume}")
            
            # Use ffmpeg to mix vocals and background
            cmd = [
                'ffmpeg',
                '-i', dubbed_vocals_path,
                '-i', background_path,
                '-filter_complex',
                f'[0:a]volume={vocals_volume}[vocals];'
                f'[1:a]volume={background_volume}[bg];'
                f'[vocals][bg]amix=inputs=2:duration=longest:dropout_transition=2',
                '-y',
                output_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            
            logger.info(f"[SEPARATOR] ✅ Mixed audio saved: {output_path}")
            return output_path
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            logger.error(f"[SEPARATOR] ❌ Audio mixing failed: {error_msg}")
            raise Exception(f"Audio mixing failed: {error_msg}")
