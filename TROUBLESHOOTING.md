# Troubleshooting Guide

## Error: "Failed to upload PDF. Please make sure the backend is running."

This error indicates the frontend cannot connect to the backend. Follow these steps:

### Step 1: Verify Backend is Running

1. **Check Railway Backend Status**
   - Go to [Railway Dashboard](https://railway.app/dashboard)
   - Select your Backend service
   - Verify it shows "Running" (green status)
   - Check the logs for any errors

2. **Test Backend Directly**
   - Copy your backend URL from Railway (Settings → Networking)
   - Open it in a browser: `https://your-backend-url.railway.app`
   - You should see: `{"message": "Programmable PDF Editor API"}`
   - If you get an error, the backend is not accessible

### Step 2: Check Environment Variables

**Frontend (Vercel):**
1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Verify `NEXT_PUBLIC_API_URL` is set correctly:
   - Should be: `https://your-backend-url.railway.app`
   - Must start with `https://` (not `http://`)
   - No trailing slash
3. If missing or incorrect:
   - Add/Update the variable
   - Redeploy the frontend

**Backend (Railway):**
1. Go to Railway Dashboard → Backend service → Variables
2. Verify `CORS_ORIGINS` includes your Vercel URL:
   ```
   https://your-project.vercel.app,https://your-project-git-main.vercel.app,http://localhost:3000
   ```
3. Include both production and preview URLs

### Step 3: Check CORS Configuration

1. **Open Browser DevTools**
   - Press F12 or Right-click → Inspect
   - Go to Console tab
   - Look for CORS errors like:
     ```
     Access to XMLHttpRequest at '...' from origin '...' has been blocked by CORS policy
     ```

2. **If CORS Error:**
   - Update backend `CORS_ORIGINS` to include your exact Vercel URL
   - Make sure it includes the protocol (`https://`)
   - Restart the backend service

### Step 4: Verify Network Connection

1. **Check Browser Network Tab**
   - Open DevTools → Network tab
   - Try uploading a PDF
   - Look for the API request to `/api/upload`
   - Check:
     - Status code (should be 200)
     - Request URL (should match your backend)
     - Error message if failed

2. **Common Status Codes:**
   - `404`: Backend URL incorrect or endpoint not found
   - `500`: Backend server error (check Railway logs)
   - `CORS error`: CORS configuration issue
   - `Network error`: Backend not accessible

### Step 5: Check Railway Backend Logs

1. **View Logs**
   - Railway Dashboard → Backend service → Logs
   - Look for:
     - Startup errors
     - Request errors
     - Python exceptions

2. **Common Backend Issues:**
   - Missing dependencies (check requirements.txt)
   - Port binding errors
   - Tesseract OCR not installed
   - File permission errors

### Step 6: Test API Endpoints

Test each endpoint directly:

1. **Root Endpoint:**
   ```
   GET https://your-backend-url.railway.app/
   ```
   Should return: `{"message": "Programmable PDF Editor API"}`

2. **Upload Endpoint (requires file):**
   ```
   POST https://your-backend-url.railway.app/api/upload
   ```
   Use Postman or curl to test

### Step 7: Verify Frontend API URL

1. **Check in Browser Console**
   - Open DevTools → Console
   - Type: `process.env.NEXT_PUBLIC_API_URL`
   - Should show your backend URL
   - If `undefined`, environment variable not set

2. **Check Network Requests**
   - DevTools → Network tab
   - Look at request URLs
   - Should start with your backend URL

### Quick Fixes

**If backend is not running:**
- Restart the Railway backend service
- Check Railway logs for errors
- Verify all dependencies are installed

**If CORS error:**
- Update `CORS_ORIGINS` in Railway backend
- Include exact Vercel URL with `https://`
- Restart backend

**If environment variable missing:**
- Add `NEXT_PUBLIC_API_URL` in Vercel
- Redeploy frontend
- Clear browser cache

**If wrong URL:**
- Verify backend URL in Railway
- Update `NEXT_PUBLIC_API_URL` in Vercel
- Redeploy frontend

### Testing Locally

To test if everything works locally:

1. **Start Backend:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

2. **Start Frontend:**
   ```bash
   cd frontend
   npm install
   NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
   ```

3. **Test Upload:**
   - Go to http://localhost:3000
   - Try uploading a PDF
   - Should work if backend is running

### Still Not Working?

1. **Check Railway Backend:**
   - Is it running?
   - Are there errors in logs?
   - Is the domain accessible?

2. **Check Vercel Frontend:**
   - Is it deployed?
   - Are environment variables set?
   - Check deployment logs

3. **Check Browser:**
   - Clear cache
   - Try incognito mode
   - Check console for errors

4. **Get Help:**
   - Share Railway backend logs
   - Share browser console errors
   - Share network request details

