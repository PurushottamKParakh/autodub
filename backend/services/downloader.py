import yt_dlp
import os
from pathlib import Path

class VideoDownloader:
    """Service for downloading YouTube videos using yt-dlp"""
    
    def __init__(self, output_dir='temp'):
        self.output_dir = output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    def download_video(self, youtube_url, job_id):
        """
        Download video from YouTube
        
        Args:
            youtube_url: YouTube video URL
            job_id: Unique job identifier
            
        Returns:
            dict: Paths to downloaded video and audio files
        """
        output_template = os.path.join(self.output_dir, f'{job_id}_%(title)s.%(ext)s')
        
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': output_template,
            'quiet': False,
            'no_warnings': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=True)
                video_path = ydl.prepare_filename(info)
                
                return {
                    'video_path': video_path,
                    'title': info.get('title', 'video'),
                    'duration': info.get('duration', 0)
                }
        except Exception as e:
            raise Exception(f"Failed to download video: {str(e)}")
    
    def download_audio_only(self, youtube_url, job_id):
        """
        Download only audio from YouTube video
        
        Args:
            youtube_url: YouTube video URL
            job_id: Unique job identifier
            
        Returns:
            str: Path to downloaded audio file
        """
        output_template = os.path.join(self.output_dir, f'{job_id}_audio.%(ext)s')
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_template,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
            }],
            'quiet': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=True)
                # The audio file will have .wav extension after post-processing
                audio_path = os.path.join(self.output_dir, f'{job_id}_audio.wav')
                
                return {
                    'audio_path': audio_path,
                    'title': info.get('title', 'audio'),
                    'duration': info.get('duration', 0)
                }
        except Exception as e:
            raise Exception(f"Failed to download audio: {str(e)}")
