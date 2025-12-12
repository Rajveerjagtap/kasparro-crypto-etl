# 🚀 Kasparro Deployment Guide - Render.com

This guide will help you deploy the Kasparro application to Render.com to get a live, verifiable public URL.

## Prerequisites

✅ All tests passing (67/67 passing)  
✅ `render.yaml` configuration file exists  
✅ `Dockerfile` ready for deployment  
✅ GitHub repository ready

## Step-by-Step Deployment Instructions

### 1. Prepare Your GitHub Repository

```bash
# Make sure all changes are committed
git status

# If there are uncommitted changes:
git add -A
git commit -m "Ready for production deployment"

# Push to GitHub
git push origin main
```

### 2. Sign Up for Render.com

1. Go to [https://render.com](https://render.com)
2. Click **"Get Started"** or **"Sign Up"**
3. Sign up with your GitHub account (recommended)
4. Authorize Render to access your repositories

### 3. Deploy Using Blueprint

1. **From Render Dashboard:**
   - Click **"New +"** button (top right)
   - Select **"Blueprint"**

2. **Connect Repository:**
   - Select your GitHub account
   - Find and select the `assignment_kasparro_New` repository
   - Click **"Connect"**

3. **Review Infrastructure:**
   Render will automatically detect `render.yaml` and show:
   - ✅ **PostgreSQL Database** (`kasparro-db`) - Free tier
   - ✅ **Web Service** (`kasparro-api`) - Public API endpoint
   - ✅ **Background Worker** (`kasparro-scheduler`) - ETL scheduler

4. **Approve and Deploy:**
   - Review the services
   - Click **"Apply"** or **"Create Resources"**
   - Wait for deployment (5-10 minutes)

### 4. Monitor Deployment

**In the Render Dashboard:**

1. **Database (`kasparro-db`):**
   - Status should show ✅ "Available"
   - Note: Free tier has 90-day expiration

2. **Web Service (`kasparro-api`):**
   - Watch build logs for errors
   - Status will show "Building" → "Deploying" → "Live"
   - Once live, you'll see a public URL like:
     ```
     https://kasparro-api-XXXX.onrender.com
     ```

3. **Background Worker (`kasparro-scheduler`):**
   - Watch logs to see ETL jobs running
   - Should start executing every hour

### 5. Verify Deployment

Once all services show ✅ "Live", test your endpoints:

```bash
# Get your actual Render URL (format: https://kasparro-api-XXXX.onrender.com)
export RENDER_URL="https://kasparro-api-XXXX.onrender.com"

# Test 1: Health check
curl $RENDER_URL/health

# Expected response:
# {"status":"healthy","timestamp":"2025-12-12T..."}

# Test 2: Get crypto data
curl $RENDER_URL/api/v1/data

# Expected response:
# {"metadata":{...},"data":[...],"total":0}

# Test 3: Trigger ETL manually
curl -X POST $RENDER_URL/api/v1/etl/run \
  -H "Content-Type: application/json"

# Test 4: Check ETL jobs
curl $RENDER_URL/api/v1/etl/jobs

# Test 5: Get stats
curl $RENDER_URL/api/v1/stats
```

### 6. Update README.md

Once you have your live URL, update the README:

```markdown
## ☁️ Live Deployment

**Public API URL:** https://kasparro-api-XXXX.onrender.com

### Quick Test:
```bash
curl https://kasparro-api-XXXX.onrender.com/health
curl https://kasparro-api-XXXX.onrender.com/api/v1/data
```
```

### 7. Final Verification Checklist

- [ ] Database shows "Available" status
- [ ] Web service shows "Live" status  
- [ ] Background worker is running (check logs)
- [ ] `/health` endpoint returns 200 OK
- [ ] `/api/v1/data` endpoint returns valid JSON
- [ ] ETL scheduler logs show periodic runs
- [ ] README.md updated with actual live URL

---

## Troubleshooting

### Build Fails

**Error: "Failed to build"**
```bash
# Check Dockerfile locally first:
docker build -t kasparro-test .
docker run -e DATABASE_URL="postgresql://test" kasparro-test
```

**Error: "Port binding failed"**
- Render sets `$PORT` automatically
- Verify Dockerfile CMD uses: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Database Connection Issues

**Error: "password authentication failed"**
- Verify `DATABASE_URL` environment variable is set in Render dashboard
- Check that it references the correct database name (`kasparro-db`)

**Error: "relation does not exist"**
- Tables aren't created automatically
- You may need to run migrations manually first

### Scheduler Not Running

**ETL jobs not executing:**
1. Check Background Worker logs in Render dashboard
2. Verify `SCHEDULE_INTERVAL` environment variable is set
3. Check that `app/scheduler.py` is importable

### Free Tier Limitations

**Cold starts:**
- Free tier services spin down after 15 minutes of inactivity
- First request after idle may take 30-60 seconds

**Database expiration:**
- Free PostgreSQL expires after 90 days
- Migrate to paid tier or export data before expiration

---

## Alternative: Railway.app Deployment

If Render doesn't work, try Railway:

1. Go to [https://railway.app](https://railway.app)
2. **New Project** → **Deploy from GitHub repo**
3. Select `assignment_kasparro_New`
4. Add **PostgreSQL** plugin
5. Set environment variables:
   ```
   DATABASE_URL=${DATABASE_URL}  # Auto-populated
   ENVIRONMENT=production
   LOG_LEVEL=INFO
   ```
6. Deploy!

Railway URL format: `https://kasparro-production.up.railway.app`

---

## Support

If you encounter issues during deployment:

1. Check Render logs (Dashboard → Service → Logs)
2. Verify environment variables are set correctly
3. Test locally with Docker first
4. Check GitHub Actions CI for build errors

**Local Docker Test:**
```bash
# Test production Docker build locally
docker-compose up --build

# Verify services work
curl http://localhost:8000/health
```

---

## Next Steps After Deployment

1. ✅ Update README.md with live URL
2. ✅ Test all API endpoints
3. ✅ Verify ETL scheduler runs automatically
4. ✅ Monitor logs for errors
5. ✅ Submit live URL to reviewer

**Congratulations! Your application is now live in production! 🎉**
