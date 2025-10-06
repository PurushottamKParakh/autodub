import os
import time
import logging
from pathlib import Path
from .downloader import VideoDownloader
from .transcriber import Transcriber
from .translator import Translator
from .synthesizer import SpeechSynthesizer
from .audio_processor import AudioProcessor
from .audio_separator import AudioSeparator
from .speaker_extractor import SpeakerExtractor
from .voice_cloner import VoiceCloner

# Configure logging
logger = logging.getLogger(__name__)

class DubbingPipeline:
    """
    Orchestrates the complete dubbing pipeline:
    Download → Transcribe → Translate → Synthesize → Align → Merge
    """
    
    def __init__(self, job_id, youtube_url, target_language, source_language='en', start_time=None, end_time=None, use_voice_cloning=False):
        self.job_id = job_id
        self.youtube_url = youtube_url
        self.target_language = target_language
        self.source_language = source_language
        self.use_voice_cloning = use_voice_cloning
        self.start_time = start_time
        self.end_time = end_time
        
        # Initialize services
        self.downloader = VideoDownloader(output_dir='temp')
        self.transcriber = Transcriber()
        self.translator = Translator()
        self.synthesizer = SpeechSynthesizer(output_dir='temp')
        self.audio_separator = AudioSeparator(temp_dir='temp')
        self.speaker_extractor = SpeakerExtractor(temp_dir='temp')
        self.voice_cloner = VoiceCloner()
        self.cloned_voices = {}
        self.audio_processor = AudioProcessor(temp_dir='temp')
        
        # Paths
        self.video_path = None
        self.audio_path = None
        self.transcription = None
        self.translated_segments = None
        self.synthesized_segments = None
        self.background_audio_path = None
        self.vocals_path = None
        self.dubbed_audio_path = None
        self.output_video_path = None
        
        # Progress tracking
        self.progress = 0
        self.status = 'queued'
        self.message = 'Job queued'
        
        # Performance tracking
        self.stage_timings = {}
        self.total_start_time = None
    
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
        # Start total timer
        self.total_start_time = time.time()
        
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
            
            stage_start = time.time()
            
            self.update_progress(10, 'processing', 'Downloading video from YouTube...')
            video_info = self.downloader.download_video(
                self.youtube_url, 
                self.job_id,
                start_time=self.start_time,
                end_time=self.end_time
            )
            self.video_path = video_info['video_path']
            
            self.stage_timings['download'] = time.time() - stage_start
            logger.info(f"✅ STAGE 1 COMPLETE: Video downloaded successfully")
            logger.info(f"   Video Path: {self.video_path}")
            logger.info(f"   Video Title: {video_info.get('title', 'Unknown')}")
            logger.info(f"   ⏱️  Duration: {self.stage_timings['download']:.2f}s")
            
            logger.info(f"\n{'='*80}")
            logger.info(f"[STAGE 2/6] EXTRACTING AUDIO")
            logger.info(f"{'='*80}")
            
            stage_start = time.time()
            self.update_progress(20, 'processing', 'Extracting audio from video...')
            self.audio_path = self.audio_processor.extract_audio_from_video(
                self.video_path,
                os.path.join('temp', f'{self.job_id}_original_audio.wav')
            )
            
            self.stage_timings['audio_extraction'] = time.time() - stage_start
            logger.info(f"✅ STAGE 2 COMPLETE: Audio extracted successfully")
            logger.info(f"   Audio Path: {self.audio_path}")
            logger.info(f"   ⏱️  Duration: {self.stage_timings['audio_extraction']:.2f}s")

            # Step 2.5: Separate vocals from background
            logger.info(f"\n{'='*80}")
            logger.info(f"[STAGE 2.5/7] SEPARATING VOCALS FROM BACKGROUND")
            logger.info(f"{'='*80}")

            stage_start = time.time()
            self.update_progress(22, 'processing', 'Separating vocals from background music...')

            separated_audio = self.audio_separator.separate_audio(
                self.audio_path,
                self.job_id
            )

            self.vocals_path = separated_audio['vocals']
            self.background_audio_path = separated_audio['background']

            self.stage_timings['audio_separation'] = time.time() - stage_start
            logger.info(f"✅ STAGE 2.5 COMPLETE: Audio separation successful")
            logger.info(f"   Vocals: {self.vocals_path}")
            logger.info(f"   Background: {self.background_audio_path}")
            logger.info(f"   ⏱️  Duration: {self.stage_timings['audio_separation']:.2f}s")
            
            # Step 2: Transcribe audio
            logger.info(f"\n{'='*80}")
            logger.info(f"[STAGE 3/6] TRANSCRIBING AUDIO")
            logger.info(f"{'='*80}")
            logger.info(f"Language: {self.source_language}")
            
            stage_start = time.time()
            self.update_progress(30, 'processing', 'Transcribing audio...')
            self.transcription = self.transcriber.transcribe_audio(
                self.vocals_path,  # Use vocals instead of full audio
                language=self.source_language
            )
            
            if not self.transcription or not self.transcription.get('segments'):
                raise Exception("Transcription failed or returned no segments")
            
            self.stage_timings['transcription'] = time.time() - stage_start
            logger.info(f"✅ STAGE 3 COMPLETE: Transcription successful")
            logger.info(f"   Segments: {len(self.transcription['segments'])}")
            logger.info(f"   Speakers: {self.transcription.get('speaker_count', 1)}")
            logger.info(f"   Full Text Preview: {self.transcription.get('full_text', '')[:100]}...")
            logger.info(f"   ⏱️  Duration: {self.stage_timings['transcription']:.2f}s")

            # Voice Cloning Stages (if enabled)
            if self.use_voice_cloning:
                # Stage 3.5: Extract speaker audio samples
                logger.info(f"\n{'='*80}")
                logger.info(f"[STAGE 3.5/8] EXTRACTING SPEAKER AUDIO SAMPLES")
                logger.info(f"{'='*80}")
                
                stage_start = time.time()
                self.update_progress(35, 'processing', 'Extracting speaker audio samples...')
                
                speaker_samples = self.speaker_extractor.extract_speaker_samples(
                    self.vocals_path,
                    self.transcription['segments'],
                    self.job_id,
                    min_duration=10.0,
                    max_duration=60.0
                )
                
                self.stage_timings['speaker_extraction'] = time.time() - stage_start
                logger.info(f"✅ STAGE 3.5 COMPLETE: Extracted samples for {len(speaker_samples)} speaker(s)")
                for speaker_id, path in speaker_samples.items():
                    logger.info(f"   Speaker {speaker_id}: {path}")
                logger.info(f"   ⏱️  Duration: {self.stage_timings['speaker_extraction']:.2f}s")
                
                # Stage 3.6: Clone voices
                logger.info(f"\n{'='*80}")
                logger.info(f"[STAGE 3.6/8] CLONING VOICES")
                logger.info(f"{'='*80}")
                
                stage_start = time.time()
                self.update_progress(38, 'processing', 'Cloning voices...')
                
                for speaker_id, audio_path in speaker_samples.items():
                    voice_name = f"{self.job_id}_speaker_{speaker_id}"
                    
                    logger.info(f"[PIPELINE] Cloning voice for speaker {speaker_id}")
                    
                    try:
                        voice_id = self.voice_cloner.clone_voice(
                            audio_path,
                            voice_name,
                            description=f"Cloned voice from job {self.job_id}"
                        )
                        
                        self.cloned_voices[speaker_id] = voice_id
                        logger.info(f"[PIPELINE] Speaker {speaker_id} → Voice ID: {voice_id}")
                    except Exception as e:
                        logger.error(f"[PIPELINE] Failed to clone voice for speaker {speaker_id}: {str(e)}")
                        logger.warning(f"[PIPELINE] Will use stock voice for speaker {speaker_id}")
                
                self.stage_timings['voice_cloning'] = time.time() - stage_start
                logger.info(f"✅ STAGE 3.6 COMPLETE: Cloned {len(self.cloned_voices)} voice(s)")
                logger.info(f"   ⏱️  Duration: {self.stage_timings['voice_cloning']:.2f}s")
            
            
            # Step 3: Translate segments
            logger.info(f"\n{'='*80}")
            logger.info(f"[STAGE 4/6] TRANSLATING TEXT")
            logger.info(f"{'='*80}")
            logger.info(f"From: {self.source_language} → To: {self.target_language}")
            logger.info(f"Segments to translate: {len(self.transcription['segments'])}")
            
            stage_start = time.time()
            self.update_progress(45, 'processing', 'Translating text...')
            self.translated_segments = self.translator.batch_translate_segments(
                self.transcription['segments'],
                self.target_language,
                self.source_language
            )
            
            self.stage_timings['translation'] = time.time() - stage_start
            logger.info(f"✅ STAGE 4 COMPLETE: Translation successful")
            logger.info(f"   Translated Segments: {len(self.translated_segments)}")
            if self.translated_segments:
                logger.info(f"   Sample Translation: '{self.translated_segments[0].get('original_text', '')[:50]}' → '{self.translated_segments[0].get('translated_text', '')[:50]}'")
            logger.info(f"   ⏱️  Duration: {self.stage_timings['translation']:.2f}s")
            
            # Step 4: Synthesize speech
            logger.info(f"\n{'='*80}")
            logger.info(f"[STAGE 5/8] SYNTHESIZING SPEECH")
            logger.info(f"{'='*80}")
            
            stage_start = time.time()
            self.update_progress(60, 'processing', 'Synthesizing speech...')
            
            if self.use_voice_cloning and self.cloned_voices:
                logger.info(f"[PIPELINE] Using cloned voices for synthesis")
                logger.info(f"[PIPELINE] Cloned voices: {self.cloned_voices}")
                self.synthesized_segments = self.synthesizer.synthesize_segments_with_cloned_voices(
                    self.translated_segments,
                    self.cloned_voices,
                    language_code=self.target_language
                )
            else:
                voice_id = self.synthesizer.get_voice_for_language(self.target_language)
                speaker_count = self.transcription.get('speaker_count', 1)
                logger.info(f"[PIPELINE] Using stock voices for synthesis")
                logger.info(f"Default Voice ID: {voice_id}")
                logger.info(f"Segments to synthesize: {len(self.translated_segments)}")
                logger.info(f"Multi-speaker mode: {'Enabled' if speaker_count > 1 else 'Disabled'}")
                self.synthesized_segments = self.synthesizer.synthesize_segments(
                    self.translated_segments,
                    voice_id=voice_id,
                    job_id=self.job_id,
                    language_code=self.target_language,
                    multi_speaker=True
                )
            
            self.stage_timings['synthesis'] = time.time() - stage_start
            logger.info(f"✅ STAGE 5 COMPLETE: Speech synthesis successful")
            logger.info(f"   Synthesized Segments: {len(self.synthesized_segments)}")
            segments_with_audio = sum(1 for s in self.synthesized_segments if 'audio_path' in s)
            logger.info(f"   Segments with audio: {segments_with_audio}/{len(self.synthesized_segments)}")
            logger.info(f"   ⏱️  Duration: {self.stage_timings['synthesis']:.2f}s")
            
            # Step 5: Align and concatenate audio
            logger.info(f"\n{'='*80}")
            logger.info(f"[STAGE 6/6] ALIGNING & MERGING AUDIO")
            logger.info(f"{'='*80}")
            
            stage_start = time.time()
            self.update_progress(75, 'processing', 'Aligning audio segments...')
            self.dubbed_audio_path = self._align_and_merge_audio()
            
            self.stage_timings['alignment'] = time.time() - stage_start
            logger.info(f"✅ Audio alignment complete")
            logger.info(f"   Dubbed Audio Path: {self.dubbed_audio_path}")
            logger.info(f"   ⏱️  Duration: {self.stage_timings['alignment']:.2f}s")

            # Step 6.5: Mix dubbed vocals with original background
            logger.info(f"\n{'='*80}")
            logger.info(f"[STAGE 6.5/7] MIXING DUBBED VOCALS WITH BACKGROUND MUSIC")
            logger.info(f"{'='*80}")

            stage_start = time.time()
            self.update_progress(85, 'processing', 'Mixing dubbed vocals with background music...')

            final_dubbed_audio = os.path.join('temp', f'{self.job_id}_final_dubbed_audio.mp3')
            self.audio_separator.mix_vocals_with_background(
                self.dubbed_audio_path,
                self.background_audio_path,
                final_dubbed_audio,
                vocals_volume=1.0,
                background_volume=0.7
            )

            # Use final mixed audio for video merging
            self.dubbed_audio_path = final_dubbed_audio

            self.stage_timings['mixing'] = time.time() - stage_start
            logger.info(f"✅ STAGE 6.5 COMPLETE: Audio mixing successful")
            logger.info(f"   Final Audio: {self.dubbed_audio_path}")
            logger.info(f"   ⏱️  Duration: {self.stage_timings['mixing']:.2f}s")
            
            # Step 6: Merge dubbed audio with video
            logger.info(f"\n📹 Merging dubbed audio with original video...")
            stage_start = time.time()
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
            
            self.stage_timings['video_merge'] = time.time() - stage_start
            logger.info(f"✅ STAGE 6 COMPLETE: Video merging successful")
            logger.info(f"   Output Video: {self.output_video_path}")
            logger.info(f"   ⏱️  Duration: {self.stage_timings['video_merge']:.2f}s")
            
            # Step 7: Complete - Calculate and log total time
            total_time = time.time() - self.total_start_time
            
            logger.info(f"\n{'='*80}")
            logger.info(f"🎉 DUBBING PIPELINE COMPLETE!")
            logger.info(f"{'='*80}")
            logger.info(f"Job ID: {self.job_id}")
            logger.info(f"Output File: {self.output_video_path}")
            logger.info(f"Total Segments: {len(self.synthesized_segments)}")
            logger.info(f"")
            logger.info(f"⏱️  PERFORMANCE SUMMARY:")
            logger.info(f"{'─'*80}")
            logger.info(f"   Download:           {self.stage_timings.get('download', 0):>8.2f}s")
            logger.info(f"   Audio Extraction:   {self.stage_timings.get('audio_extraction', 0):>8.2f}s")
            logger.info(f"   Audio Separation:   {self.stage_timings.get('audio_separation', 0):>8.2f}s")
            logger.info(f"   Transcription:      {self.stage_timings.get('transcription', 0):>8.2f}s")
            if 'speaker_extraction' in self.stage_timings:
                logger.info(f"   Speaker Extraction: {self.stage_timings.get('speaker_extraction', 0):>8.2f}s")
            if 'voice_cloning' in self.stage_timings:
                logger.info(f"   Voice Cloning:      {self.stage_timings.get('voice_cloning', 0):>8.2f}s")
            logger.info(f"   Translation:        {self.stage_timings.get('translation', 0):>8.2f}s")
            logger.info(f"   Synthesis:          {self.stage_timings.get('synthesis', 0):>8.2f}s")
            logger.info(f"   Alignment:          {self.stage_timings.get('alignment', 0):>8.2f}s")
            logger.info(f"   Mixing:             {self.stage_timings.get('mixing', 0):>8.2f}s")
            logger.info(f"   Video Merge:        {self.stage_timings.get('video_merge', 0):>8.2f}s")
            logger.info(f"{'─'*80}")
            logger.info(f"   🏁 TOTAL TIME:      {total_time:>8.2f}s ({total_time/60:.2f} minutes)")
            logger.info(f"{'='*80}\n")
            
            self.update_progress(100, 'completed', 'Dubbing completed successfully!')
            
            return {
                'status': 'completed',
                'output_file': self.output_video_path,
                'job_id': self.job_id,
                'segments_count': len(self.synthesized_segments),
                'total_time': total_time,
                'stage_timings': self.stage_timings
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
                
                # Log timing information
                logger.info(f"[ALIGNMENT] Segment {segment['start']:.2f}s-{segment['end']:.2f}s:")
                logger.info(f"[ALIGNMENT]   Original duration: {original_duration:.2f}s")
                logger.info(f"[ALIGNMENT]   Synthesized duration: {synth_duration:.2f}s")
                logger.info(f"[ALIGNMENT]   Speed factor: {speed_factor:.2f}x")
                
                # If speed adjustment is needed (tolerance: 1% for precise timing)
                if abs(speed_factor - 1.0) > 0.01:
                    logger.info(f"[ALIGNMENT] Adjusting segment speed to {speed_factor:.2f}x")
                    
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
                        logger.info(f"[ALIGNMENT] ✅ Speed adjusted successfully")
                    except Exception as e:
                        logger.warning(f"[ALIGNMENT] ⚠️ Could not adjust speed: {e}")
                else:
                    logger.info(f"[ALIGNMENT] ✅ No adjustment needed (within 1% tolerance)")
            
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
            self.vocals_path,
            self.background_audio_path,
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
