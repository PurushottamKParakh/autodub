import yt_dlp
import os
from pathlib import Path
import logging


# Configure logging
logger = logging.getLogger(__name__)

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
        import os
        
        # Clear proxy environment variables
        env_backup = {}
        proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy']
        for var in proxy_vars:
            if var in os.environ:
                env_backup[var] = os.environ[var]
                del os.environ[var]
        
        try:
            output_template = os.path.join(self.output_dir, f'{job_id}_%(title)s.%(ext)s')
            
            ydl_opts = {
                # Simpler format that's less likely to be blocked
                'format': 'best[ext=mp4]/best',
                'outtmpl': output_template,
                'quiet': False,
                'no_warnings': False,
                
                # Disable proxy
                'proxy': None,
                
                # YouTube specific - important for avoiding blocks
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android', 'web'],
                        'player_skip': ['webpage', 'configs'],
                    }
                },
                
                # Updated headers to better mimic browser
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Cache-Control': 'max-age=0',
                },
                
                # Retry and error handling
                'retries': 10,
                'fragment_retries': 10,
                'extractor_retries': 5,
                'nocheckcertificate': True,
                'ignoreerrors': False,
                
                # Additional options to avoid blocks
                'age_limit': None,
                'sleep_interval': 1,
                'max_sleep_interval': 3,
            }
            
            logger.info(f"[DOWNLOADER] Downloading from: {youtube_url}")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=True)
                
                if info is None:
                    raise Exception("Failed to extract video information")
                
                video_path = ydl.prepare_filename(info)
                
                # Check if file exists with various extensions
                if not os.path.exists(video_path):
                    base_path = os.path.splitext(video_path)[0]
                    # Try common extensions
                    for ext in ['.mp4', '.webm', '.mkv', '.m4a']:
                        test_path = base_path + ext
                        if os.path.exists(test_path):
                            video_path = test_path
                            break
                
                if not os.path.exists(video_path):
                    raise FileNotFoundError(f"Downloaded file not found: {video_path}")
                
                logger.info(f"[DOWNLOADER] ✅ Downloaded: {video_path}")
                
                return {
                    'video_path': video_path,
                    'title': info.get('title', 'video'),
                    'duration': info.get('duration', 0)
                }
                
        except Exception as e:
            logger.error(f"[DOWNLOADER] ❌ Error: {str(e)}")
            raise Exception(f"Failed to download video: {str(e)}")
        finally:
            # Restore environment variables
            for var, value in env_backup.items():
                os.environ[var] = value

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
            'noproxy': '*',  # Disable proxy for all hosts
            'proxy': '',     # Explicitly set no proxy
            'socket_timeout': 30,
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
