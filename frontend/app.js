// Configuration
const API_BASE_URL = 'http://localhost:5000';

// DOM Elements
const dubForm = document.getElementById('dubForm');
const submitBtn = document.getElementById('submitBtn');
const progressSection = document.getElementById('progressSection');
const resultSection = document.getElementById('resultSection');
const jobsSection = document.getElementById('jobsSection');

const jobIdSpan = document.getElementById('jobId');
const statusSpan = document.getElementById('status');
const progressSpan = document.getElementById('progress');
const messageP = document.getElementById('message');
const progressFill = document.getElementById('progressFill');

const resultVideo = document.getElementById('resultVideo');
const downloadBtn = document.getElementById('downloadBtn');
const newDubBtn = document.getElementById('newDubBtn');

const jobsList = document.getElementById('jobsList');

// State
let currentJobId = null;
let pollingInterval = null;

// Event Listeners
dubForm.addEventListener('submit', handleSubmit);
newDubBtn.addEventListener('click', resetForm);
downloadBtn.addEventListener('click', handleDownload);

// Initialize
loadJobs();

async function handleSubmit(e) {
    e.preventDefault();
    
    const youtubeUrl = document.getElementById('youtubeUrl').value;
    const targetLanguage = document.getElementById('targetLanguage').value;
    const startTime = document.getElementById('startTime').value;
    const endTime = document.getElementById('endTime').value;
    
    try {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Creating Job...';
        
        // Build request body
        const requestBody = {
            youtube_url: youtubeUrl,
            target_language: targetLanguage
        };
        
        // Add optional time parameters if provided
        if (startTime !== '' && startTime !== null) {
            requestBody.start_time = parseInt(startTime);
        }
        if (endTime !== '' && endTime !== null) {
            requestBody.end_time = parseInt(endTime);
        }
        
        console.log('Sending request body:', requestBody);
        
        const response = await fetch(`${API_BASE_URL}/api/dub`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to create dubbing job');
        }
        
        const data = await response.json();
        currentJobId = data.job_id;
        
        // Show progress section
        progressSection.classList.remove('hidden');
        resultSection.classList.add('hidden');
        
        // Start polling for status
        startPolling();
        
        // Scroll to progress section
        progressSection.scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        alert(`Error: ${error.message}`);
        submitBtn.disabled = false;
        submitBtn.textContent = 'Start Dubbing';
    }
}

function startPolling() {
    if (pollingInterval) {
        clearInterval(pollingInterval);
    }
    
    // Poll every 2 seconds
    pollingInterval = setInterval(checkJobStatus, 2000);
    
    // Check immediately
    checkJobStatus();
}

async function checkJobStatus() {
    if (!currentJobId) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/dub/${currentJobId}`);
        
        if (!response.ok) {
            throw new Error('Failed to fetch job status');
        }
        
        const data = await response.json();
        
        // Update UI
        jobIdSpan.textContent = data.job_id;
        statusSpan.textContent = data.status;
        progressSpan.textContent = data.progress || 0;
        messageP.textContent = data.message || '';
        progressFill.style.width = `${data.progress || 0}%`;
        
        // Update status styling
        statusSpan.className = `job-status ${data.status}`;
        
        // Check if completed
        if (data.status === 'completed') {
            clearInterval(pollingInterval);
            showResult(data);
        } else if (data.status === 'failed') {
            clearInterval(pollingInterval);
            alert(`Job failed: ${data.message}`);
            resetForm();
        }
        
        // Reload jobs list
        loadJobs();
        
    } catch (error) {
        console.error('Error checking job status:', error);
    }
}

function showResult(data) {
    progressSection.classList.add('hidden');
    resultSection.classList.remove('hidden');
    
    // Set video source
    if (data.video_url) {
        resultVideo.src = `${API_BASE_URL}${data.video_url}`;
    }
    
    // Scroll to result
    resultSection.scrollIntoView({ behavior: 'smooth' });
    
    // Reset form
    submitBtn.disabled = false;
    submitBtn.textContent = 'Start Dubbing';
}

function handleDownload() {
    if (currentJobId) {
        window.open(`${API_BASE_URL}/api/download/${currentJobId}`, '_blank');
    }
}

function resetForm() {
    dubForm.reset();
    progressSection.classList.add('hidden');
    resultSection.classList.add('hidden');
    currentJobId = null;
    
    if (pollingInterval) {
        clearInterval(pollingInterval);
    }
    
    submitBtn.disabled = false;
    submitBtn.textContent = 'Start Dubbing';
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

async function loadJobs() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/jobs`);
        
        if (!response.ok) {
            throw new Error('Failed to fetch jobs');
        }
        
        const data = await response.json();
        const jobs = data.jobs || [];
        
        if (jobs.length === 0) {
            jobsList.innerHTML = '<p class="text-muted">No jobs yet. Start by creating a new dub!</p>';
            return;
        }
        
        // Sort by most recent first
        jobs.sort((a, b) => {
            // Assuming job_id contains timestamp or is chronological
            return b.job_id.localeCompare(a.job_id);
        });
        
        // Display jobs
        jobsList.innerHTML = jobs.map(job => `
            <div class="job-item" onclick="loadJob('${job.job_id}')">
                <p><strong>Job ID:</strong> ${job.job_id.substring(0, 8)}...</p>
                <p><strong>Status:</strong> <span class="job-status ${job.status}">${job.status}</span></p>
                <p><strong>Language:</strong> ${job.target_language}</p>
                <p><strong>URL:</strong> ${truncateUrl(job.youtube_url)}</p>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading jobs:', error);
    }
}

function loadJob(jobId) {
    currentJobId = jobId;
    progressSection.classList.remove('hidden');
    resultSection.classList.add('hidden');
    startPolling();
    progressSection.scrollIntoView({ behavior: 'smooth' });
}

function truncateUrl(url) {
    if (url.length > 50) {
        return url.substring(0, 47) + '...';
    }
    return url;
}

// Check API health on load
async function checkApiHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (!response.ok) {
            console.warn('API health check failed');
        }
    } catch (error) {
        console.error('Cannot connect to API:', error);
        alert('Warning: Cannot connect to the backend API. Please make sure the server is running on port 5000.');
    }
}

checkApiHealth();
