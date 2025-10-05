import subprocess
import os
from pathlib import Path

class AudioProcessor:
    """Service for processing and aligning audio using ffmpeg"""
    
    def __init__(self, temp_dir='temp'):
        self.temp_dir = temp_dir
        Path(temp_dir).mkdir(parents=True, exist_ok=True)
    
    def extract_audio_from_video(self, video_path, output_path=None):
        """
        Extract audio from video file
        
        Args:
            video_path: Path to video file
            output_path: Path to save extracted audio
            
        Returns:
            str: Path to extracted audio
        """
        if output_path is None:
            output_path = os.path.join(
                self.temp_dir,
                f"{Path(video_path).stem}_audio.wav"
            )
        
        try:
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vn',  # No video
                '-acodec', 'pcm_s16le',  # PCM 16-bit
                '-ar', '44100',  # 44.1kHz sample rate
                '-ac', '2',  # Stereo
                '-y',  # Overwrite output
                output_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            return output_path
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to extract audio: {e.stderr.decode()}")
    
    def adjust_audio_speed(self, audio_path, speed_factor, output_path=None):
        """
        Adjust audio speed while preserving pitch
        
        Args:
            audio_path: Path to audio file
            speed_factor: Speed multiplier (e.g., 1.2 for 20% faster)
            output_path: Path to save adjusted audio
            
        Returns:
            str: Path to adjusted audio
        """
        if output_path is None:
            output_path = os.path.join(
                self.temp_dir,
                f"{Path(audio_path).stem}_adjusted.mp3"
            )
        
        try:
            # Use atempo filter (supports 0.5 to 2.0)
            if speed_factor < 0.5 or speed_factor > 2.0:
                # Chain multiple atempo filters for extreme speeds
                atempo_filters = []
                remaining_speed = speed_factor
                
                while remaining_speed > 2.0:
                    atempo_filters.append('atempo=2.0')
                    remaining_speed /= 2.0
                
                while remaining_speed < 0.5:
                    atempo_filters.append('atempo=0.5')
                    remaining_speed /= 0.5
                
                if remaining_speed != 1.0:
                    atempo_filters.append(f'atempo={remaining_speed}')
                
                filter_str = ','.join(atempo_filters)
            else:
                filter_str = f'atempo={speed_factor}'
            
            cmd = [
                'ffmpeg',
                '-i', audio_path,
                '-filter:a', filter_str,
                '-y',
                output_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            return output_path
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to adjust audio speed: {e.stderr.decode()}")
    
    def concatenate_audio_segments(self, segments, output_path, silence_duration=0.1):
        """
        Concatenate audio segments with proper timing
        
        Args:
            segments: List of segments with audio_path, start, end
            output_path: Path to save concatenated audio
            silence_duration: Duration of silence between segments
            
        Returns:
            str: Path to concatenated audio
        """
        try:
            # Create a concat file list
            concat_file = os.path.join(self.temp_dir, 'concat_list.txt')
            
            with open(concat_file, 'w') as f:
                for i, segment in enumerate(segments):
                    if 'audio_path' not in segment or not os.path.exists(segment['audio_path']):
                        continue
                    
                    # Add silence before segment if needed
                    if i > 0:
                        gap = segment['start'] - segments[i-1]['end']
                        if gap > 0:
                            silence_file = self._create_silence(gap)
                            # Only add silence file if it was created (not None)
                            if silence_file:
                                # Use absolute path for silence file
                                silence_abs_path = os.path.abspath(silence_file)
                                f.write(f"file '{silence_abs_path}'\n")
                    
                    # Use absolute path for segment audio
                    segment_abs_path = os.path.abspath(segment['audio_path'])
                    f.write(f"file '{segment_abs_path}'\n")
            
            # Concatenate using ffmpeg
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_file,
                '-c', 'copy',
                '-y',
                output_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            return output_path
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to concatenate audio: {e.stderr.decode()}")
    
    def _create_silence(self, duration):
        """
        Create a silent audio file
        
        Args:
            duration: Duration in seconds
            
        Returns:
            str: Path to silence file
        """
        # Skip creating silence for very small durations (< 0.01 seconds)
        # This prevents ffmpeg errors with extremely small values
        if duration < 0.01:
            return None
        
        silence_path = os.path.join(self.temp_dir, f'silence_{duration:.2f}.mp3')
        
        if os.path.exists(silence_path):
            return silence_path
        
        cmd = [
            'ffmpeg',
            '-f', 'lavfi',
            '-i', f'anullsrc=r=44100:cl=stereo',
            '-t', str(duration),
            '-y',
            silence_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return silence_path
    
    def merge_audio_with_video(self, video_path, audio_path, output_path):
        """
        Replace video's audio track with new audio
        
        Args:
            video_path: Path to original video
            audio_path: Path to new audio track
            output_path: Path to save output video
            
        Returns:
            str: Path to output video
        """
        try:
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-i', audio_path,
                '-c:v', 'copy',  # Copy video stream
                '-map', '0:v:0',  # Use video from first input
                '-map', '1:a:0',  # Use audio from second input
                '-shortest',  # Finish when shortest stream ends
                '-y',
                output_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            return output_path
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to merge audio with video: {e.stderr.decode()}")
    
    def get_audio_duration(self, audio_path):
        """
        Get duration of audio file in seconds
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            float: Duration in seconds
        """
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                audio_path
            ]
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            duration = float(result.stdout.strip())
            return duration
            
        except (subprocess.CalledProcessError, ValueError) as e:
            raise Exception(f"Failed to get audio duration: {str(e)}")
