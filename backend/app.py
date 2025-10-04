from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from dotenv import load_dotenv
import uuid
from pathlib import Path
from job_manager import job_manager

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['OUTPUT_FOLDER'] = os.getenv('OUTPUT_FOLDER', 'outputs')
app.config['TEMP_FOLDER'] = os.getenv('TEMP_FOLDER', 'temp')
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Ensure directories exist
for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER'], app.config['TEMP_FOLDER']]:
    Path(folder).mkdir(parents=True, exist_ok=True)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'autodub-api'
    }), 200

@app.route('/api/dub', methods=['POST'])
def create_dub_job():
    """
    Create a new dubbing job
    Expected JSON body:
    {
        "youtube_url": "https://www.youtube.com/watch?v=...",
        "target_language": "es",
        "source_language": "en"  (optional)
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'youtube_url' not in data:
            return jsonify({'error': 'youtube_url is required'}), 400
        
        youtube_url = data['youtube_url']
        target_language = data.get('target_language', 'es')
        source_language = data.get('source_language', 'en')
        
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Create job using job manager (starts async processing)
        job = job_manager.create_job(
            job_id=job_id,
            youtube_url=youtube_url,
            target_language=target_language,
            source_language=source_language
        )
        
        return jsonify({
            'job_id': job_id,
            'status': 'queued',
            'message': 'Dubbing job created successfully'
        }), 202
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dub/<job_id>', methods=['GET'])
def get_dub_status(job_id):
    """
    Get the status of a dubbing job
    """
    job = job_manager.get_job(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    response = {
        'job_id': job_id,
        'status': job['status'],
        'progress': job.get('progress', 0),
        'message': job.get('message', '')
    }
    
    # If completed, include video URL
    if job['status'] == 'completed' and 'output_file' in job:
        response['video_url'] = f'/api/download/{job_id}'
    
    return jsonify(response), 200

@app.route('/api/download/<job_id>', methods=['GET'])
def download_video(job_id):
    """
    Download the dubbed video
    """
    job = job_manager.get_job(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    if job['status'] != 'completed':
        return jsonify({'error': 'Job not completed yet'}), 400
    
    if 'output_file' not in job:
        return jsonify({'error': 'Output file not found'}), 404
    
    output_path = job['output_file']
    
    if not os.path.exists(output_path):
        return jsonify({'error': 'Output file does not exist'}), 404
    
    return send_file(
        output_path,
        mimetype='video/mp4',
        as_attachment=True,
        download_name=f'dubbed_video_{job_id}.mp4'
    )

@app.route('/api/jobs', methods=['GET'])
def list_jobs():
    """
    List all jobs
    """
    jobs = job_manager.get_all_jobs()
    return jsonify({
        'jobs': jobs
    }), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True') == 'True'
    app.run(host='0.0.0.0', port=port, debug=debug)
