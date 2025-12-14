# Vercel Deployment Guide - Frontend

This guide will help you deploy the frontend to Vercel while keeping the backend on Railway.

## Prerequisites

- Vercel account (sign up at [vercel.com](https://vercel.com))
- GitHub repository connected
- Backend deployed on Railway (get the backend URL)

## Step 1: Deploy to Vercel

### Option 1: Via Vercel Dashboard (Recommended)

1. **Go to Vercel Dashboard**
   - Visit [vercel.com/dashboard](https://vercel.com/dashboard)
   - Sign in with GitHub

2. **Import Project**
   - Click "Add New" → "Project"
   - Import your GitHub repository: `apurva4122/programmable-pdf-editor`
   - Vercel will auto-detect it's a Next.js project

3. **Configure Project**
   - **Framework Preset**: Next.js (auto-detected)
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `.next` (auto-detected)
   - **Install Command**: `npm install` (auto-detected)

4. **Set Environment Variables**
   - Click "Environment Variables"
   - Add:
     ```
     NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
     ```
     - Replace with your actual Railway backend URL
   - Select "Production", "Preview", and "Development"

5. **Deploy**
   - Click "Deploy"
   - Wait for build to complete
   - Your app will be live at: `https://your-project.vercel.app`

### Option 2: Via Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Login**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   cd frontend
   vercel
   ```

4. **Set Environment Variables**
   ```bash
   vercel env add NEXT_PUBLIC_API_URL
   # Enter your backend URL when prompted
   ```

5. **Deploy to Production**
   ```bash
   vercel --prod
   ```

## Step 2: Update Backend CORS

After deploying frontend, update backend CORS to allow Vercel domain:

1. **Get Your Vercel URL**
   - From Vercel dashboard, copy your deployment URL
   - Example: `https://programmable-pdf-editor.vercel.app`

2. **Update Railway Backend**
   - Go to Railway Dashboard
   - Select your Backend service
   - Go to Variables tab
   - Update `CORS_ORIGINS`:
     ```
     https://your-project.vercel.app,https://your-project-git-main.vercel.app,http://localhost:3000
     ```
   - Include both production and preview URLs

## Step 3: Verify Deployment

1. **Test Frontend**
   - Visit your Vercel URL
   - Should see the PDF Editor interface

2. **Test Backend Connection**
   - Try uploading a PDF
   - Check browser console for any CORS errors
   - Check Railway logs for backend activity

## Environment Variables

### Required for Frontend

- `NEXT_PUBLIC_API_URL`: Your Railway backend URL
  - Example: `https://backend-production-xxxx.up.railway.app`

### Optional

- `NODE_ENV`: Automatically set by Vercel
- `VERCEL_URL`: Automatically set by Vercel (for preview deployments)

## Custom Domain (Optional)

1. Go to Vercel Dashboard → Your Project → Settings → Domains
2. Add your custom domain
3. Follow DNS configuration instructions

## Preview Deployments

Vercel automatically creates preview deployments for:
- Every push to a branch
- Every pull request

Each preview gets its own URL and can use different environment variables.

## Troubleshooting

### Build Failures

1. **Check Build Logs**
   - Go to Vercel Dashboard → Your Project → Deployments
   - Click on failed deployment → View Build Logs

2. **Common Issues**
   - Missing environment variables
   - TypeScript errors
   - Missing dependencies

### CORS Errors

1. **Verify Backend CORS**
   - Check Railway backend `CORS_ORIGINS` includes Vercel URL
   - Include both production and preview URLs

2. **Check Environment Variables**
   - Verify `NEXT_PUBLIC_API_URL` is set correctly
   - Must start with `https://` (not `http://`)

### API Connection Issues

1. **Test Backend Directly**
   - Visit backend URL in browser
   - Should see: `{"message": "Programmable PDF Editor API"}`

2. **Check Network Tab**
   - Open browser DevTools → Network
   - Look for failed API requests
   - Check error messages

## Advantages of Vercel for Frontend

- ✅ Optimized for Next.js
- ✅ Automatic deployments on git push
- ✅ Preview deployments for PRs
- ✅ Global CDN
- ✅ Automatic HTTPS
- ✅ Built-in analytics
- ✅ No configuration needed

## Migration from Railway Frontend

If you had the frontend on Railway:

1. **Keep Railway Service**
   - You can delete the Railway frontend service
   - Or keep it as a backup

2. **Update Environment Variables**
   - Remove Railway frontend environment variables
   - Add Vercel environment variables

3. **Update Documentation**
   - Update any links pointing to Railway frontend
   - Update CORS settings in backend

## Quick Reference

- **Frontend**: Vercel (https://your-project.vercel.app)
- **Backend**: Railway (https://backend-production-xxxx.up.railway.app)
- **Environment Variable**: `NEXT_PUBLIC_API_URL` → Backend URL

