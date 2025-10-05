import os
import subprocess
from pathlib import Path
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class SpeakerExtractor:
    """Extract audio samples for each speaker from separated vocals"""
    
    def __init__(self, temp_dir='temp'):
        self.temp_dir = temp_dir
        Path(temp_dir).mkdir(parents=True, exist_ok=True)
        self.samples_dir = os.path.join(temp_dir, 'speaker_samples')
        Path(self.samples_dir).mkdir(parents=True, exist_ok=True)
    
    def extract_speaker_samples(self, vocals_path, segments, job_id, 
                               min_duration=10.0, max_duration=60.0):
        """
        Extract audio samples for each speaker from clean vocals
        
        Args:
            vocals_path: Path to separated vocals (clean audio)
            segments: List of transcription segments with speaker info
            job_id: Job identifier for file naming
            min_duration: Minimum audio duration per speaker (seconds)
            max_duration: Maximum audio duration per speaker (seconds)
            
        Returns:
            dict: {speaker_id: audio_sample_path}
        """
        try:
            logger.info(f"[SPEAKER_EXTRACTOR] Extracting speaker samples from {vocals_path}")
            
            # Group segments by speaker
            speaker_segments = defaultdict(list)
            for segment in segments:
                speaker = segment.get('speaker', 0)
                speaker_segments[speaker].append(segment)
            
            logger.info(f"[SPEAKER_EXTRACTOR] Found {len(speaker_segments)} unique speaker(s)")
            
            speaker_samples = {}
            
            for speaker_id, segs in speaker_segments.items():
                logger.info(f"[SPEAKER_EXTRACTOR] Processing speaker {speaker_id} ({len(segs)} segments)")
                
                # Sort segments by start time
                segs.sort(key=lambda x: x.get('start', 0))
                
                # Collect segments until we have enough audio
                selected_segments = []
                total_duration = 0.0
                
                for seg in segs:
                    start = seg.get('start', 0)
                    end = seg.get('end', 0)
                    duration = end - start
                    
                    # Skip very short segments (< 0.5 seconds)
                    if duration < 0.5:
                        continue
                    
                    selected_segments.append(seg)
                    total_duration += duration
                    
                    # Stop if we have enough audio
                    if total_duration >= max_duration:
                        break
                
                if total_duration < min_duration:
                    logger.warning(
                        f"[SPEAKER_EXTRACTOR] Speaker {speaker_id} has only {total_duration:.1f}s "
                        f"of audio (min: {min_duration}s). Using all available audio."
                    )
                
                if not selected_segments:
                    logger.warning(f"[SPEAKER_EXTRACTOR] No valid segments for speaker {speaker_id}")
                    continue
                
                # Extract and concatenate audio segments
                sample_path = self._extract_and_concatenate(
                    vocals_path,
                    selected_segments,
                    speaker_id,
                    job_id
                )
                
                speaker_samples[speaker_id] = sample_path
                logger.info(
                    f"[SPEAKER_EXTRACTOR] ✅ Speaker {speaker_id} sample: {sample_path} "
                    f"({total_duration:.1f}s)"
                )
            
            return speaker_samples
            
        except Exception as e:
            logger.error(f"[SPEAKER_EXTRACTOR] ❌ Error: {str(e)}")
            raise
    
    def _extract_and_concatenate(self, vocals_path, segments, speaker_id, job_id):
        """
        Extract and concatenate audio segments for a speaker
        
        Args:
            vocals_path: Path to vocals audio file
            segments: List of segments for this speaker
            speaker_id: Speaker identifier
            job_id: Job identifier
            
        Returns:
            str: Path to concatenated audio sample
        """
        try:
            # Create temporary files for each segment
            segment_files = []
            concat_list_path = os.path.join(
                self.temp_dir, 
                f'{job_id}_speaker_{speaker_id}_concat.txt'
            )
            
            with open(concat_list_path, 'w') as f:
                for i, seg in enumerate(segments):
                    start = seg.get('start', 0)
                    end = seg.get('end', 0)
                    duration = end - start
                    
                    # Extract segment using ffmpeg
                    segment_file = os.path.join(
                        self.temp_dir,
                        f'{job_id}_speaker_{speaker_id}_seg_{i}.wav'
                    )
                    
                    cmd = [
                        'ffmpeg',
                        '-i', vocals_path,
                        '-ss', str(start),
                        '-t', str(duration),
                        '-acodec', 'pcm_s16le',
                        '-ar', '44100',
                        '-ac', '1',  # Mono for voice cloning
                        '-y',
                        segment_file
                    ]
                    
                    subprocess.run(cmd, check=True, capture_output=True)
                    segment_files.append(segment_file)
                    
                    # Add to concat list
                    f.write(f"file '{os.path.abspath(segment_file)}'\n")
            
            # Concatenate all segments
            output_path = os.path.join(
                self.samples_dir,
                f'{job_id}_speaker_{speaker_id}_sample.wav'
            )
            
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_list_path,
                '-acodec', 'pcm_s16le',
                '-ar', '44100',
                '-ac', '1',
                '-y',
                output_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Cleanup temporary segment files
            for seg_file in segment_files:
                if os.path.exists(seg_file):
                    os.remove(seg_file)
            if os.path.exists(concat_list_path):
                os.remove(concat_list_path)
            
            return output_path
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            logger.error(f"[SPEAKER_EXTRACTOR] ❌ FFmpeg error: {error_msg}")
            raise Exception(f"Audio extraction failed: {error_msg}")
