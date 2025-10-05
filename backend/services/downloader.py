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
    
    def download_video(self, youtube_url, job_id, start_time=None, end_time=None):
        """
        Download video from YouTube
        
        Args:
            youtube_url: YouTube video URL
            job_id: Unique job identifier
            start_time: Optional start time in seconds
            end_time: Optional end time in seconds
            
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
            
            # Add time-based trimming if specified
            if start_time is not None or end_time is not None:
                # Try download_ranges approach first (more efficient)
                try:
                    from yt_dlp.utils import download_range_func
                    
                    start = start_time if start_time is not None else 0
                    end = end_time  # Can be None for "until the end"
                    
                    # Use download_ranges to only download the specified segment
                    ydl_opts['download_ranges'] = download_range_func(None, [(start, end)])
                    ydl_opts['force_keyframes_at_cuts'] = True
                    
                    logger.info(f"[DOWNLOADER] Using download_ranges: start={start_time}s, end={end_time}s")
                    
                except ImportError:
                    # Fallback to postprocessor approach if download_ranges not available
                    logger.info(f"[DOWNLOADER] download_ranges not available, using postprocessor fallback")
                    self._add_postprocessor_trimming(ydl_opts, start_time, end_time)
                except Exception as e:
                    # If download_ranges fails for any reason, fall back to postprocessor
                    logger.warning(f"[DOWNLOADER] download_ranges failed: {e}, using postprocessor fallback")
                    self._add_postprocessor_trimming(ydl_opts, start_time, end_time)
            
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
                
                # Calculate actual duration based on trimming
                duration = info.get('duration', 0)
                if start_time is not None or end_time is not None:
                    actual_start = start_time if start_time is not None else 0
                    actual_end = end_time if end_time is not None else duration
                    duration = actual_end - actual_start
                
                return {
                    'video_path': video_path,
                    'title': info.get('title', 'video'),
                    'duration': duration
                }
                
        except Exception as e:
            logger.error(f"[DOWNLOADER] ❌ Error: {str(e)}")
            raise Exception(f"Failed to download video: {str(e)}")
        finally:
            # Restore environment variables
            for var, value in env_backup.items():
                os.environ[var] = value
    
    def _add_postprocessor_trimming(self, ydl_opts, start_time, end_time):
        """
        Add ffmpeg postprocessor arguments for trimming
        
        Args:
            ydl_opts: yt-dlp options dictionary
            start_time: Start time in seconds (can be None)
            end_time: End time in seconds (can be None)
        """
        postprocessor_args = ['-c', 'copy']  # Copy codec for fast processing
        
        if start_time is not None:
            postprocessor_args.extend(['-ss', str(start_time)])
        
        if end_time is not None:
            if start_time is not None:
                duration = end_time - start_time
                postprocessor_args.extend(['-t', str(duration)])
            else:
                postprocessor_args.extend(['-to', str(end_time)])
        
        ydl_opts['postprocessor_args'] = {'ffmpeg': postprocessor_args}
        logger.info(f"[DOWNLOADER] Using postprocessor trimming: start={start_time}s, end={end_time}s")

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
