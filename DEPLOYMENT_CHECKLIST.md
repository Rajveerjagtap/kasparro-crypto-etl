# ✅ Deployment Checklist - Render.com

## Pre-Deployment Verification

- [x] All 67 tests passing (`pytest tests/ -v`)
- [x] `render.yaml` configuration exists
- [x] `Dockerfile` ready for production
- [x] `entrypoint.sh` supports Render's DATABASE_URL format
- [x] Requirements.txt has all dependencies
- [ ] Code committed to GitHub

## Deployment Steps

### 1. Push to GitHub
```bash
git add -A
git commit -m "Deploy Kasparro to production - all tests passing"
git push origin main
```

### 2. Deploy on Render
1. Go to https://render.com
2. Sign up/Login with GitHub
3. Click **"New +"** → **"Blueprint"**
4. Select your repository: `assignment_kasparro_New`
5. Click **"Apply"**

### 3. Wait for Services (5-10 mins)
- ✅ `kasparro-db` (PostgreSQL)
- ✅ `kasparro-api` (Web Service)
- ✅ `kasparro-scheduler` (Background Worker)

### 4. Get Your Live URL
Format: `https://kasparro-api-XXXX.onrender.com`

Find it in: Render Dashboard → kasparro-api → URL

## Post-Deployment Testing

```bash
# Replace with your actual Render URL
export URL="https://kasparro-api-XXXX.onrender.com"

# Test 1: Health check
curl $URL/health
# Expected: {"status":"healthy","timestamp":"..."}

# Test 2: Get data
curl $URL/api/v1/data
# Expected: {"metadata":{...},"data":[],"total":0}

# Test 3: Trigger ETL
curl -X POST $URL/api/v1/etl/run
# Expected: {"job_id":...,"status":"RUNNING"}

# Test 4: Get stats
curl $URL/api/v1/stats
# Expected: {...etl_stats...}
```

## Final Steps

### 1. Update README.md
Replace placeholder URL with your actual live URL:

```markdown
## ☁️ Live Deployment

**Public API URL:** https://kasparro-api-XXXX.onrender.com

Test it:
```bash
curl https://kasparro-api-XXXX.onrender.com/health
```

### 2. Verify in Render Dashboard
- [ ] Database status: ✅ Available
- [ ] Web service status: ✅ Live
- [ ] Worker status: ✅ Running
- [ ] No errors in logs

### 3. Monitor Scheduler
Check Background Worker logs to see ETL jobs:
```
[2025-12-12 14:00:00] Starting ETL cycle...
[2025-12-12 14:00:05] ✓ CoinGecko: 100 records
[2025-12-12 14:00:10] ✓ CoinPaprika: 150 records
[2025-12-12 14:00:15] ETL cycle complete!
```

## Troubleshooting

### Build Fails
- Check Dockerfile syntax
- Verify requirements.txt has no conflicts
- Test locally: `./test-docker-build.sh`

### Database Connection Error
- Ensure DATABASE_URL is set in Render dashboard
- Check entrypoint.sh can parse the URL
- Verify migrations ran successfully

### Service Won't Start
- Check logs in Render dashboard
- Verify PORT environment variable is used
- Ensure healthCheckPath `/health` works

## Success Criteria
- [ ] `/health` returns 200 OK
- [ ] `/api/v1/data` returns valid JSON
- [ ] No errors in service logs
- [ ] Scheduler logs show periodic ETL runs
- [ ] README.md updated with live URL

**Deployment Complete! 🎉**

Submit your live URL to the reviewer:
```
https://kasparro-api-XXXX.onrender.com
```
