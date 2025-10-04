# 🚀 Deployment Checklist

## Pre-Deployment

### Environment Setup
- [ ] Python 3.8+ installed
- [ ] ffmpeg installed and in PATH
- [ ] Virtual environment created
- [ ] All dependencies installed (`pip install -r requirements.txt`)

### Configuration
- [ ] `.env` file created from `.env.example`
- [ ] Deepgram API key added
- [ ] OpenAI API key added
- [ ] ElevenLabs API key verified
- [ ] Directory permissions set correctly

### Testing
- [ ] Run `python test_setup.py` - all checks pass
- [ ] Test with short video (1-2 min)
- [ ] Test different languages
- [ ] Verify audio-video sync
- [ ] Check file cleanup works

## Deployment Steps

### 1. Backend Deployment

```bash
cd backend
source venv/bin/activate
python app.py
```

**Verify:**
- [ ] Server starts without errors
- [ ] Health endpoint responds: `curl http://localhost:5000/health`
- [ ] No API key warnings in logs

### 2. Frontend Deployment

```bash
cd frontend
python -m http.server 8000
```

**Verify:**
- [ ] Frontend loads at http://localhost:8000
- [ ] No console errors
- [ ] Can connect to backend

### 3. Integration Test

- [ ] Submit test job with YouTube URL
- [ ] Monitor progress updates
- [ ] Verify video downloads successfully
- [ ] Check output quality

## Production Considerations

### Security
- [ ] API keys not committed to git
- [ ] `.env` in `.gitignore`
- [ ] CORS properly configured
- [ ] File size limits enforced
- [ ] Input validation in place

### Performance
- [ ] Disk space monitoring
- [ ] Cleanup old files regularly
- [ ] Monitor API usage/costs
- [ ] Check memory usage under load

### Monitoring
- [ ] Backend logs accessible
- [ ] Error tracking enabled
- [ ] Job status tracking works
- [ ] Failed jobs logged

### Backup
- [ ] Important outputs backed up
- [ ] Configuration backed up
- [ ] API keys securely stored

## Post-Deployment

### Smoke Tests
- [ ] Create dubbing job
- [ ] Check job status
- [ ] Download completed video
- [ ] List all jobs

### Documentation
- [ ] README.md updated
- [ ] API documentation current
- [ ] Setup instructions verified
- [ ] Troubleshooting guide complete

### Handoff
- [ ] Demo video recorded
- [ ] Known issues documented
- [ ] Future improvements listed
- [ ] Contact information provided

## Rollback Plan

If issues occur:

1. **Stop services**
   ```bash
   # Ctrl+C in both terminals
   ```

2. **Check logs**
   - Review terminal output
   - Check for API errors
   - Verify file permissions

3. **Restore configuration**
   ```bash
   cp .env.backup .env
   ```

4. **Restart services**
   ```bash
   python app.py
   ```

## Health Checks

### Backend Health
```bash
curl http://localhost:5000/health
# Expected: {"status": "healthy", "service": "autodub-api"}
```

### Create Test Job
```bash
curl -X POST http://localhost:5000/api/dub \
  -H "Content-Type: application/json" \
  -d '{"youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "target_language": "es"}'
```

### Check Job Status
```bash
curl http://localhost:5000/api/dub/{JOB_ID}
```

## Maintenance

### Daily
- [ ] Check disk space
- [ ] Monitor failed jobs
- [ ] Review error logs

### Weekly
- [ ] Clean up old temp files
- [ ] Clean up old output files
- [ ] Review API usage
- [ ] Check for updates

### Monthly
- [ ] Update dependencies
- [ ] Review security
- [ ] Optimize performance
- [ ] Update documentation

## Emergency Contacts

**API Support:**
- Deepgram: https://deepgram.com/support
- OpenAI: https://platform.openai.com/support
- ElevenLabs: support@deeptune.com

**Technical Issues:**
- Check GitHub issues
- Review documentation
- Contact hackathon organizers

## Success Criteria

✅ **Deployment Successful When:**
- Backend responds to health checks
- Frontend loads without errors
- Can create and process jobs
- Videos download successfully
- Audio-video sync is maintained
- No critical errors in logs

## Notes

- First deployment may take 5-10 minutes
- Test with SHORT videos first
- Monitor API costs during testing
- Keep `.env` secure and backed up
- Document any custom configurations

---

**Deployment Date**: _____________
**Deployed By**: _____________
**Version**: 1.0.0
**Status**: ⬜ Ready | ⬜ In Progress | ⬜ Complete
