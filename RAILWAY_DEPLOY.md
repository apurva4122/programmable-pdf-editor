# Railway Deployment Guide

This guide will help you deploy both the frontend and backend to Railway.

## Prerequisites

- Railway account (sign up at [railway.app](https://railway.app))
- GitHub repository connected (already done!)

## Option 1: Deploy via Railway Dashboard

### Backend Deployment

1. **Create New Project**
   - Go to [Railway Dashboard](https://railway.app/dashboard)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository: `programmable-pdf-editor`

2. **Configure Backend Service**
   - Click "New Service"
   - Select "GitHub Repo"
   - Choose your repository
   - Set **Root Directory** to: `backend`
   - Railway will auto-detect Python

3. **Set Environment Variables**
   - Go to the service → Variables tab
   - Add:
     ```
     PORT=8000
     CORS_ORIGINS=https://your-frontend-domain.railway.app
     ```

4. **Configure Build Settings**
   - Railway will automatically:
     - Install system dependencies (Tesseract, Poppler)
     - Install Python dependencies
     - Run the FastAPI server

5. **Get Backend URL**
   - Go to Settings → Networking
   - Click "Generate Domain" or "Add Domain"
   - When asked for **Port**, enter: `8000` (or leave default if Railway auto-detects)
   - Railway will automatically use the PORT environment variable, but you may need to specify it here
   - Copy the URL (e.g., `https://backend-production-xxxx.up.railway.app`)

### Frontend Deployment

1. **Create New Service in Same Project**
   - In your Railway project, click "New Service"
   - Select "GitHub Repo"
   - Choose the same repository
   - Set **Root Directory** to: `frontend`

2. **Set Environment Variables**
   - Go to Variables tab
   - Add:
     ```
     NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
     NODE_ENV=production
     PORT=3000
     ```

3. **Configure Build Settings**
   - Railway will automatically:
     - Install Node.js dependencies
     - Build the Next.js app
     - Start the production server

4. **Get Frontend URL**
   - Go to Settings → Networking
   - Click "Generate Domain" or "Add Domain"
   - When asked for **Port**, enter: `3000` (or leave default if Railway auto-detects)
   - Your app will be live!

## Option 2: Deploy via Railway CLI

### Install Railway CLI

```bash
# Windows (PowerShell)
iwr https://railway.app/install.ps1 | iex

# macOS/Linux
curl -fsSL https://railway.app/install.sh | sh
```

### Login

```bash
railway login
```

### Deploy Backend

```bash
cd backend
railway init
railway link  # Link to existing project or create new
railway up
```

### Deploy Frontend

```bash
cd frontend
railway init
railway link  # Link to same project
railway variables set NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
railway up
```

## Environment Variables Reference

### Backend Variables
- `PORT`: Server port (Railway sets this automatically)
- `CORS_ORIGINS`: Comma-separated list of allowed origins
  - Example: `https://your-frontend.railway.app,http://localhost:3000`

### Frontend Variables
- `NEXT_PUBLIC_API_URL`: Backend API URL
  - Example: `https://backend-production-xxxx.up.railway.app`
- `NODE_ENV`: Set to `production`
- `PORT`: Server port (Railway sets this automatically)

## Post-Deployment Steps

1. **Update CORS Origins**
   - In backend service → Variables
   - Update `CORS_ORIGINS` with your frontend URL

2. **Test the Application**
   - Visit your frontend URL
   - Try uploading a PDF
   - Verify OCR and PDF generation work

3. **Monitor Logs**
   - Railway dashboard shows real-time logs
   - Check for any errors or warnings

## Troubleshooting

### Backend Issues

**Tesseract not found:**
- Railway's Nixpacks should auto-install it
- If not, check the `nixpacks.toml` file

**Port binding errors:**
- Ensure you're using `$PORT` environment variable
- Railway sets this automatically

**CORS errors:**
- Update `CORS_ORIGINS` with exact frontend URL
- Include protocol (https://)

### Frontend Issues

**API connection errors:**
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check backend is running and accessible
- Test backend URL in browser

**Build failures:**
- Check Node.js version (Railway uses latest LTS)
- Review build logs in Railway dashboard

## Custom Domain (Optional)

1. Go to service → Settings → Networking
2. Click "Custom Domain"
3. Add your domain
4. Follow DNS configuration instructions

## Cost Considerations

- Railway offers a free tier with $5 credit/month
- After free tier: Pay-as-you-go pricing
- Monitor usage in Railway dashboard

## Quick Deploy Commands

```bash
# Backend
cd backend && railway up

# Frontend  
cd frontend && railway up
```

## Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway

