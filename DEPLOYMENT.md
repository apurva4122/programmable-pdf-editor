# Deployment Guide

This guide covers deploying the Programmable PDF Editor application.

## Prerequisites

- Node.js 18+ (for frontend)
- Python 3.11+ (for backend)
- Tesseract OCR installed
- Poppler utilities (for PDF processing)

## Frontend Deployment (Vercel)

### Option 1: Vercel CLI

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Navigate to frontend directory:
```bash
cd frontend
```

3. Deploy:
```bash
vercel
```

### Option 2: Vercel Dashboard

1. Import your GitHub repository to Vercel
2. Set root directory to `frontend`
3. Configure environment variables if needed
4. Deploy

### Environment Variables

Create a `.env.local` file in the frontend directory:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production, update this to your backend API URL.

## Backend Deployment

### Option 1: Railway

1. Create a new project on Railway
2. Connect your GitHub repository
3. Set root directory to `backend`
4. Add environment variables:
   - `PORT=8000`
5. Railway will auto-detect Python and install dependencies

### Option 2: Heroku

1. Create a `Procfile` in backend directory:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

2. Create `runtime.txt`:
```
python-3.11.0
```

3. Deploy:
```bash
heroku create your-app-name
git push heroku main
```

### Option 3: DigitalOcean App Platform

1. Create a new app
2. Connect GitHub repository
3. Set root directory to `backend`
4. Configure build command: `pip install -r requirements.txt`
5. Configure run command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### System Dependencies

The backend requires:
- Tesseract OCR
- Poppler utilities

For Docker deployment, use this Dockerfile:

```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Docker Compose (Full Stack)

Create a `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend/uploads:/app/uploads
      - ./backend/outputs:/app/outputs
    environment:
      - CORS_ORIGINS=http://localhost:3000

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend
```

## GitHub Actions

The repository includes GitHub Actions workflows for:
- CI/CD on push/PR
- Automatic deployment to Vercel (if configured)

To enable Vercel deployment:
1. Add `VERCEL_TOKEN` to GitHub Secrets
2. Push to main/master branch

## Environment Variables

### Backend
- `CORS_ORIGINS`: Allowed CORS origins (default: http://localhost:3000)
- `PORT`: Server port (default: 8000)

### Frontend
- `NEXT_PUBLIC_API_URL`: Backend API URL

## Troubleshooting

1. **OCR not working**: Ensure Tesseract OCR is installed
2. **PDF processing fails**: Check Poppler utilities installation
3. **CORS errors**: Update `CORS_ORIGINS` in backend
4. **Build failures**: Check Node.js and Python versions

