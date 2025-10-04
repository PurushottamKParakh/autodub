import threading
from services.pipeline import DubbingPipeline

class JobManager:
    """
    Manages dubbing jobs and their execution
    Uses threading for async processing
    """
    
    def __init__(self):
        self.jobs = {}
        self.lock = threading.Lock()
    
    def create_job(self, job_id, youtube_url, target_language, source_language='en'):
        """
        Create a new dubbing job
        
        Args:
            job_id: Unique job identifier
            youtube_url: YouTube video URL
            target_language: Target language code
            source_language: Source language code
            
        Returns:
            dict: Job information
        """
        with self.lock:
            self.jobs[job_id] = {
                'job_id': job_id,
                'youtube_url': youtube_url,
                'target_language': target_language,
                'source_language': source_language,
                'status': 'queued',
                'progress': 0,
                'message': 'Job queued for processing',
                'output_file': None,
                'error': None
            }
        
        # Start processing in background thread
        thread = threading.Thread(
            target=self._process_job,
            args=(job_id, youtube_url, target_language, source_language)
        )
        thread.daemon = True
        thread.start()
        
        return self.jobs[job_id]
    
    def get_job(self, job_id):
        """
        Get job status
        
        Args:
            job_id: Job identifier
            
        Returns:
            dict: Job information or None
        """
        with self.lock:
            return self.jobs.get(job_id)
    
    def get_all_jobs(self):
        """
        Get all jobs
        
        Returns:
            list: List of all jobs
        """
        with self.lock:
            return list(self.jobs.values())
    
    def _process_job(self, job_id, youtube_url, target_language, source_language):
        """
        Process a dubbing job in background
        
        Args:
            job_id: Job identifier
            youtube_url: YouTube video URL
            target_language: Target language code
            source_language: Source language code
        """
        try:
            # Create pipeline
            pipeline = DubbingPipeline(
                job_id=job_id,
                youtube_url=youtube_url,
                target_language=target_language,
                source_language=source_language
            )
            
            # Update job status periodically
            def update_callback():
                with self.lock:
                    if job_id in self.jobs:
                        self.jobs[job_id]['status'] = pipeline.status
                        self.jobs[job_id]['progress'] = pipeline.progress
                        self.jobs[job_id]['message'] = pipeline.message
            
            # Monkey patch the update_progress method to update our job dict
            original_update = pipeline.update_progress
            
            def wrapped_update(progress, status, message):
                original_update(progress, status, message)
                update_callback()
            
            pipeline.update_progress = wrapped_update
            
            # Run pipeline
            result = pipeline.run()
            
            # Update job with result
            with self.lock:
                if job_id in self.jobs:
                    self.jobs[job_id].update({
                        'status': 'completed',
                        'progress': 100,
                        'message': 'Dubbing completed successfully',
                        'output_file': result['output_file']
                    })
            
            print(f"Job {job_id} completed successfully")
            
        except Exception as e:
            error_msg = str(e)
            print(f"Job {job_id} failed: {error_msg}")
            
            # Update job with error
            with self.lock:
                if job_id in self.jobs:
                    self.jobs[job_id].update({
                        'status': 'failed',
                        'message': f'Job failed: {error_msg}',
                        'error': error_msg
                    })
    
    def delete_job(self, job_id):
        """
        Delete a job
        
        Args:
            job_id: Job identifier
            
        Returns:
            bool: True if deleted, False if not found
        """
        with self.lock:
            if job_id in self.jobs:
                del self.jobs[job_id]
                return True
            return False

# Global job manager instance
job_manager = JobManager()
