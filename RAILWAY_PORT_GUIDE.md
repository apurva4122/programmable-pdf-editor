# Railway Port Configuration Guide

When Railway asks for a port when generating a domain, here's what to enter:

## Backend Service (FastAPI)

**Port to enter: `8000`**

- Railway automatically sets the `PORT` environment variable
- Our uvicorn command uses `--port $PORT` which reads from this variable
- When generating domain, you can enter `8000` or let Railway auto-detect
- Railway will route traffic to whatever port your app is listening on

## Frontend Service (Next.js)

**Port to enter: `3000`**

- Next.js typically runs on port 3000
- Railway sets `PORT` environment variable automatically
- When generating domain, enter `3000` or let Railway auto-detect

## Important Notes

1. **Railway Auto-Detection**: Railway usually detects the port automatically from your start command
2. **Environment Variable**: Railway sets `$PORT` automatically - your app should use this
3. **If Port Not Detected**: 
   - Check your service logs to see what port it's actually using
   - Enter that port number when generating the domain
   - Or check the service settings → Deploy → Start Command

## Quick Reference

| Service | Port | Environment Variable |
|---------|------|---------------------|
| Backend | 8000 | `$PORT` (Railway sets this) |
| Frontend | 3000 | `$PORT` (Railway sets this) |

## Troubleshooting

**If Railway can't detect the port:**
1. Check your start command uses `$PORT` variable
2. Look at service logs to see what port it's actually using
3. Enter that port number when generating domain

**If domain generation fails:**
1. Make sure your service has deployed successfully
2. Check that the service is running (green status)
3. Try waiting a few minutes for the service to fully start

