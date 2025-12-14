# Fixing Railway 502 Bad Gateway Error

## Error Analysis

The error shows:
- **HTTP 502**: Bad Gateway
- **"connection refused"**: Backend not accepting connections
- **"Retried single replica"**: Railway tried multiple times but failed

This means the backend process is either:
1. Not starting
2. Crashing immediately
3. Not binding to the correct port
4. Not listening on 0.0.0.0

## Step 1: Check Railway Backend Logs

1. Go to Railway Dashboard
2. Select your **Backend** service
3. Click on **Logs** tab
4. Look for:
   - Startup errors
   - Python exceptions
   - Port binding errors
   - Import errors

## Step 2: Verify Start Command

Check that Railway is using the correct start command:

1. Railway Dashboard → Backend service → **Settings** → **Deploy**
2. **Start Command** should be: `python start_server.py`
3. If different, update it and redeploy

## Step 3: Check Environment Variables

Verify these are set in Railway:

1. Railway Dashboard → Backend service → **Variables**
2. Check:
   - `PORT` - Railway sets this automatically (don't set manually)
   - `CORS_ORIGINS` - Should include your Vercel frontend URL

## Step 4: Verify Backend Files

Make sure these files exist in your repository:

- `backend/start_server.py` ✓
- `backend/main.py` ✓
- `backend/requirements.txt` ✓
- `backend/nixpacks.toml` ✓

## Step 5: Test Start Script Locally

Test the start script works:

```bash
cd backend
python start_server.py
```

Should start without errors.

## Common Issues and Fixes

### Issue 1: Missing Dependencies

**Symptoms:** Import errors in logs

**Fix:**
- Check `requirements.txt` includes all dependencies
- Verify Railway installed them (check build logs)

### Issue 2: Port Binding Error

**Symptoms:** "Address already in use" or port errors

**Fix:**
- Don't set PORT manually in Railway
- Let Railway set it automatically
- The start_server.py script reads it correctly

### Issue 3: Python Path Issues

**Symptoms:** "Module not found" errors

**Fix:**
- Ensure `main.py` is in the backend root
- Check imports in main.py are correct

### Issue 4: Tesseract Not Found

**Symptoms:** OCR-related errors

**Fix:**
- Nixpacks should install Tesseract automatically
- Check nixpacks.toml includes: `"tesseract", "poppler_utils"`

## Quick Fix: Restart Backend

1. Railway Dashboard → Backend service
2. Click **Redeploy** or **Restart**
3. Watch the logs for startup messages

## Expected Log Output

When backend starts correctly, you should see:

```
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:XXXX (Press CTRL+C to quit)
```

## If Still Not Working

1. **Check Build Logs:**
   - Railway Dashboard → Backend → Deployments
   - Click on latest deployment
   - Check build phase for errors

2. **Check Runtime Logs:**
   - Railway Dashboard → Backend → Logs
   - Look for Python tracebacks
   - Look for startup errors

3. **Verify Service Status:**
   - Railway Dashboard → Backend service
   - Should show "Running" (green)
   - If "Crashed" or "Stopped", check logs

4. **Test Backend Directly:**
   - Copy backend URL from Railway
   - Visit in browser: `https://your-backend.railway.app/`
   - Should see: `{"message": "Programmable PDF Editor API"}`

## Manual Start Command Override

If needed, you can set the start command manually in Railway:

1. Railway Dashboard → Backend → Settings → Deploy
2. **Start Command**: `python start_server.py`
3. Save and redeploy

