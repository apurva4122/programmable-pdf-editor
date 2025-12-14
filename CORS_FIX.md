# Fixing CORS Error

## Error Message
```
Access to XMLHttpRequest at 'https://programmable-pdf-editor-production.up.railway.app/api/upload' 
from origin 'https://programmable-pdf-editor.vercel.app' 
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

## Problem
The backend's CORS configuration doesn't include your Vercel frontend URL.

## Solution: Update CORS_ORIGINS in Railway

### Step 1: Get Your Vercel URLs

You need to add these URLs to the backend CORS configuration:
- Production: `https://programmable-pdf-editor.vercel.app`
- Preview deployments: `https://programmable-pdf-editor-*.vercel.app` (wildcard)

### Step 2: Update Railway Environment Variable

1. **Go to Railway Dashboard**
   - Visit [railway.app/dashboard](https://railway.app/dashboard)
   - Select your **Backend** service

2. **Go to Variables Tab**
   - Click on **Variables** in the left sidebar

3. **Update CORS_ORIGINS**
   - Find the `CORS_ORIGINS` variable
   - If it doesn't exist, click **New Variable**
   - Set the value to:
     ```
     https://programmable-pdf-editor.vercel.app,https://programmable-pdf-editor-git-*.vercel.app,https://programmable-pdf-editor-*.vercel.app,http://localhost:3000
     ```
   - Or more simply (if wildcards don't work):
     ```
     https://programmable-pdf-editor.vercel.app,http://localhost:3000
     ```

4. **Save and Restart**
   - Click **Save** or the variable will auto-save
   - Railway will automatically restart the backend
   - Wait for the service to restart (check logs)

### Step 3: Verify CORS is Working

1. **Test in Browser**
   - Go to your Vercel frontend
   - Open browser DevTools (F12) → Console
   - Try uploading a PDF
   - Should no longer see CORS errors

2. **Check Backend Logs**
   - Railway Dashboard → Backend → Logs
   - Should see successful requests

## Alternative: Update CORS Code (If Needed)

If the environment variable approach doesn't work, you can update the backend code to allow all origins (for development):

```python
# In backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (not recommended for production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Note:** Only use `allow_origins=["*"]` for testing. For production, always specify exact origins.

## Quick Fix Command

If you have Railway CLI installed:

```bash
railway variables set CORS_ORIGINS="https://programmable-pdf-editor.vercel.app,http://localhost:3000"
```

## Common Issues

### Issue 1: Wildcards Not Working
- Railway might not support wildcards in CORS_ORIGINS
- Solution: List all specific URLs you need

### Issue 2: Preview Deployments
- Each Vercel preview gets a unique URL
- Solution: Add the main production URL, or use wildcards if supported

### Issue 3: Backend Not Restarting
- After updating CORS_ORIGINS, backend should auto-restart
- If not, manually restart: Railway Dashboard → Backend → Restart

## Verification

After updating CORS_ORIGINS:

1. **Check Backend is Running**
   - Railway Dashboard → Backend should show "Running"

2. **Test CORS Headers**
   - Open browser DevTools → Network tab
   - Make a request to backend
   - Check Response Headers for:
     - `Access-Control-Allow-Origin: https://programmable-pdf-editor.vercel.app`
     - `Access-Control-Allow-Methods: *`
     - `Access-Control-Allow-Headers: *`

3. **Test Upload**
   - Try uploading a PDF from Vercel frontend
   - Should work without CORS errors

