import os
import time
import logging
from pathlib import Path
from .downloader import VideoDownloader
from .transcriber import Transcriber
from .translator import Translator
from .synthesizer import SpeechSynthesizer
from .audio_processor import AudioProcessor

# Configure logging
logger = logging.getLogger(__name__)

class DubbingPipeline:
    """
    Orchestrates the complete dubbing pipeline:
    Download → Transcribe → Translate → Synthesize → Align → Merge
    """
    
    def __init__(self, job_id, youtube_url, target_language, source_language='en', start_time=None, end_time=None):
        self.job_id = job_id
        self.youtube_url = youtube_url
        self.target_language = target_language
        self.source_language = source_language
        self.start_time = start_time
        self.end_time = end_time
        
        # Initialize services
        self.downloader = VideoDownloader(output_dir='temp')
        self.transcriber = Transcriber()
        self.translator = Translator()
        self.synthesizer = SpeechSynthesizer(output_dir='temp')
        self.audio_processor = AudioProcessor(temp_dir='temp')
        
        # Paths
        self.video_path = None
        self.audio_path = None
        self.transcription = None
        self.translated_segments = None
        self.synthesized_segments = None
        self.dubbed_audio_path = None
        self.output_video_path = None
        
        # Progress tracking
        self.progress = 0
        self.status = 'queued'
        self.message = 'Job queued'
    
    def update_progress(self, progress, status, message):
        """Update job progress"""
        self.progress = progress
        self.status = status
        self.message = message
        print(f"[{self.job_id}] {progress}% - {status}: {message}")
    
    def run(self):
        """
        Execute the complete dubbing pipeline
        
        Returns:
            dict: Job result with output video path
        """
        try:
            # Step 1: Download video and extract audio
            logger.info(f"\n{'='*80}")
            logger.info(f"[STAGE 1/6] DOWNLOADING VIDEO")
            logger.info(f"{'='*80}")
            logger.info(f"Job ID: {self.job_id}")
            logger.info(f"YouTube URL: {self.youtube_url}")
            logger.info(f"Target Language: {self.target_language}")
            logger.info(f"Source Language: {self.source_language}")
            logger.info(f"Start Time: {self.start_time}")
            logger.info(f"End Time: {self.end_time}")
            
            self.update_progress(10, 'processing', 'Downloading video from YouTube...')
            video_info = self.downloader.download_video(
                self.youtube_url, 
                self.job_id,
                start_time=self.start_time,
                end_time=self.end_time
            )
            self.video_path = video_info['video_path']
            
            logger.info(f"✅ STAGE 1 COMPLETE: Video downloaded successfully")
            logger.info(f"   Video Path: {self.video_path}")
            logger.info(f"   Video Title: {video_info.get('title', 'Unknown')}")
            
            logger.info(f"\n{'='*80}")
            logger.info(f"[STAGE 2/6] EXTRACTING AUDIO")
            logger.info(f"{'='*80}")
            
            self.update_progress(20, 'processing', 'Extracting audio from video...')
            self.audio_path = self.audio_processor.extract_audio_from_video(
                self.video_path,
                os.path.join('temp', f'{self.job_id}_original_audio.wav')
            )
            
            logger.info(f"✅ STAGE 2 COMPLETE: Audio extracted successfully")
            logger.info(f"   Audio Path: {self.audio_path}")
            
            # Step 2: Transcribe audio
            logger.info(f"\n{'='*80}")
            logger.info(f"[STAGE 3/6] TRANSCRIBING AUDIO")
            logger.info(f"{'='*80}")
            logger.info(f"Language: {self.source_language}")
            
            self.update_progress(30, 'processing', 'Transcribing audio...')
            self.transcription = self.transcriber.transcribe_audio(
                self.audio_path,
                language=self.source_language
            )
            
            if not self.transcription or not self.transcription.get('segments'):
                raise Exception("Transcription failed or returned no segments")
            
            logger.info(f"✅ STAGE 3 COMPLETE: Transcription successful")
            logger.info(f"   Segments: {len(self.transcription['segments'])}")
            logger.info(f"   Speakers: {self.transcription.get('speaker_count', 1)}")
            logger.info(f"   Full Text Preview: {self.transcription.get('full_text', '')[:100]}...")
            
            # Step 3: Translate segments
            logger.info(f"\n{'='*80}")
            logger.info(f"[STAGE 4/6] TRANSLATING TEXT")
            logger.info(f"{'='*80}")
            logger.info(f"From: {self.source_language} → To: {self.target_language}")
            logger.info(f"Segments to translate: {len(self.transcription['segments'])}")
            
            self.update_progress(45, 'processing', 'Translating text...')
            self.translated_segments = self.translator.batch_translate_segments(
                self.transcription['segments'],
                self.target_language,
                self.source_language
            )
            
            logger.info(f"✅ STAGE 4 COMPLETE: Translation successful")
            logger.info(f"   Translated Segments: {len(self.translated_segments)}")
            if self.translated_segments:
                logger.info(f"   Sample Translation: '{self.translated_segments[0].get('original_text', '')[:50]}' → '{self.translated_segments[0].get('translated_text', '')[:50]}'")
            
            # Step 4: Synthesize speech
            logger.info(f"\n{'='*80}")
            logger.info(f"[STAGE 5/6] SYNTHESIZING SPEECH")
            logger.info(f"{'='*80}")
            voice_id = self.synthesizer.get_voice_for_language(self.target_language)
            speaker_count = self.transcription.get('speaker_count', 1)
            logger.info(f"Default Voice ID: {voice_id}")
            logger.info(f"Segments to synthesize: {len(self.translated_segments)}")
            logger.info(f"Multi-speaker mode: {'Enabled' if speaker_count > 1 else 'Disabled'}")
            
            self.update_progress(60, 'processing', 'Synthesizing speech...')
            self.synthesized_segments = self.synthesizer.synthesize_segments(
                self.translated_segments,
                voice_id=voice_id,
                job_id=self.job_id,
                language_code=self.target_language,
                multi_speaker=True  # Always enabled, will auto-detect speakers
            )
            
            logger.info(f"✅ STAGE 5 COMPLETE: Speech synthesis successful")
            logger.info(f"   Synthesized Segments: {len(self.synthesized_segments)}")
            segments_with_audio = sum(1 for s in self.synthesized_segments if 'audio_path' in s)
            logger.info(f"   Segments with audio: {segments_with_audio}/{len(self.synthesized_segments)}")
            
            # Step 5: Align and concatenate audio
            logger.info(f"\n{'='*80}")
            logger.info(f"[STAGE 6/6] ALIGNING & MERGING AUDIO")
            logger.info(f"{'='*80}")
            
            self.update_progress(75, 'processing', 'Aligning audio segments...')
            self.dubbed_audio_path = self._align_and_merge_audio()
            
            logger.info(f"✅ Audio alignment complete")
            logger.info(f"   Dubbed Audio Path: {self.dubbed_audio_path}")
            
            # Step 6: Merge dubbed audio with video
            logger.info(f"\n📹 Merging dubbed audio with original video...")
            self.update_progress(90, 'processing', 'Merging audio with video...')
            self.output_video_path = os.path.join(
                'outputs',
                f'{self.job_id}_dubbed.mp4'
            )
            
            Path('outputs').mkdir(parents=True, exist_ok=True)
            
            self.audio_processor.merge_audio_with_video(
                self.video_path,
                self.dubbed_audio_path,
                self.output_video_path
            )
            
            logger.info(f"✅ STAGE 6 COMPLETE: Video merging successful")
            logger.info(f"   Output Video: {self.output_video_path}")
            
            # Step 7: Complete
            logger.info(f"\n{'='*80}")
            logger.info(f"🎉 DUBBING PIPELINE COMPLETE!")
            logger.info(f"{'='*80}")
            logger.info(f"Job ID: {self.job_id}")
            logger.info(f"Output File: {self.output_video_path}")
            logger.info(f"Total Segments: {len(self.synthesized_segments)}")
            logger.info(f"{'='*80}\n")
            
            self.update_progress(100, 'completed', 'Dubbing completed successfully!')
            
            return {
                'status': 'completed',
                'output_file': self.output_video_path,
                'job_id': self.job_id,
                'segments_count': len(self.synthesized_segments)
            }
            
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            logger.error(f"[PIPELINE ERROR] Job {self.job_id} failed")
            logger.error(f"[PIPELINE ERROR] Type: {error_type}")
            logger.error(f"[PIPELINE ERROR] Message: {error_msg}")
            logger.error(f"[PIPELINE ERROR] Full exception: {repr(e)}")
            
            self.update_progress(self.progress, 'failed', f'Error: {error_msg}')
            raise
    
    def _align_and_merge_audio(self):
        """
        Align synthesized audio segments to match original timing
        
        Returns:
            str: Path to final dubbed audio file
        """
        aligned_segments = []
        
        for segment in self.synthesized_segments:
            if 'audio_path' not in segment or not os.path.exists(segment['audio_path']):
                print(f"Warning: Skipping segment without audio: {segment.get('translated_text', '')[:50]}")
                continue
            
            # Get duration of synthesized audio
            synth_duration = self.audio_processor.get_audio_duration(segment['audio_path'])
            
            # Get original segment duration
            original_duration = segment['end'] - segment['start']
            
            # Calculate speed adjustment needed
            if original_duration > 0:
                speed_factor = synth_duration / original_duration
                
                # If speed adjustment is needed (tolerance: 10%)
                if abs(speed_factor - 1.0) > 0.1:
                    print(f"Adjusting segment speed: {speed_factor:.2f}x")
                    
                    # Adjust speed to fit original duration
                    adjusted_path = os.path.join(
                        'temp',
                        f"{self.job_id}_adjusted_{segment['start']:.2f}.mp3"
                    )
                    
                    try:
                        self.audio_processor.adjust_audio_speed(
                            segment['audio_path'],
                            1.0 / speed_factor,  # Inverse to compress/expand
                            adjusted_path
                        )
                        segment['audio_path'] = adjusted_path
                    except Exception as e:
                        print(f"Warning: Could not adjust speed: {e}")
            
            aligned_segments.append(segment)
        
        # Concatenate all segments
        output_path = os.path.join('temp', f'{self.job_id}_dubbed_audio.mp3')
        
        self.audio_processor.concatenate_audio_segments(
            aligned_segments,
            output_path
        )
        
        return output_path
    
    def cleanup(self):
        """Clean up temporary files"""
        temp_files = [
            self.video_path,
            self.audio_path,
            self.dubbed_audio_path
        ]
        
        # Add all segment audio files
        if self.synthesized_segments:
            for segment in self.synthesized_segments:
                if 'audio_path' in segment:
                    temp_files.append(segment['audio_path'])
        
        for file_path in temp_files:
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"Cleaned up: {file_path}")
                except Exception as e:
                    print(f"Warning: Could not delete {file_path}: {e}")
