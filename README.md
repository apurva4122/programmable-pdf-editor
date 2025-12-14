# Programmable PDF Editor

A web application for programmatically editing PDFs using OCR to detect text sections and generate multiple variations with customizable text replacements.

## Features

- **OCR Text Detection**: Automatically scan PDFs and identify text sections
- **Programmatic Editing**: Assign rules to text sections (serial numbers, random numbers, prefixes/suffixes)
- **Batch Generation**: Generate multiple PDF copies with variations
- **Multiple Text Objects**: Edit multiple text sections simultaneously
- **Flexible Formatting**: Support for prefixes, suffixes, and custom number formats
- **Modern UI**: Built with shadcn/ui components for a beautiful, accessible interface

## Tech Stack

- **Frontend**: Next.js 14 (React) with shadcn/ui
- **Backend**: Python FastAPI
- **OCR**: Tesseract OCR
- **PDF Processing**: PyPDF2, PyMuPDF
- **UI Components**: Radix UI, Tailwind CSS

## Prerequisites

- Node.js 18+
- Python 3.11+
- Tesseract OCR
- Poppler utilities (for PDF processing)

### Installing System Dependencies

**Windows:**
```bash
# Install Tesseract OCR
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Install Poppler from: https://github.com/oschwartz10612/poppler-windows/releases
```

**macOS:**
```bash
brew install tesseract poppler
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr poppler-utils
```

## Setup

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The backend will run on `http://localhost:8000`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will run on `http://localhost:3000`

## Usage

1. **Upload PDF**: Click to upload a PDF file
2. **OCR Processing**: Wait for OCR to automatically detect text sections
3. **Select Sections**: Click on text sections you want to edit
4. **Configure Rules**: 
   - Choose replacement type (Serial, Random, or Custom)
   - Set start values, ranges, prefixes, suffixes
   - Preview the format
5. **Generate**: Specify number of copies and generate
6. **Download**: Download the ZIP file containing all generated PDFs

## Example Use Cases

- **Invoice Numbers**: Generate 10 invoices with sequential invoice numbers (INV-0001, INV-0002, etc.)
- **Random IDs**: Create multiple copies with random ID numbers
- **Custom Formatting**: Add prefixes like "DOC-" and suffixes like "-2024" to document numbers

## Deployment

### Recommended Setup

- **Frontend**: Deploy to [Vercel](https://vercel.com) (optimized for Next.js)
- **Backend**: Deploy to [Railway](https://railway.app) (supports Python with system dependencies)

### Frontend Deployment (Vercel)

**Quick Deploy:**
1. Go to [Vercel](https://vercel.com)
2. Import your GitHub repository
3. Set root directory to `frontend`
4. Add environment variable: `NEXT_PUBLIC_API_URL` → Your Railway backend URL
5. Deploy

See [VERCEL_DEPLOY.md](./VERCEL_DEPLOY.md) for complete Vercel setup guide.

### Backend Deployment (Railway)

**Quick Deploy:**
1. Go to [Railway](https://railway.app)
2. Create new project from GitHub repo
3. Add backend service (root: `backend`)
4. Set environment variables:
   - `CORS_ORIGINS`: Your Vercel frontend URL
5. Deploy

See [RAILWAY_DEPLOY.md](./RAILWAY_DEPLOY.md) for complete Railway setup guide.

### Alternative Deployments

See [DEPLOYMENT.md](./DEPLOYMENT.md) for other deployment options.

## Development

### Project Structure

```
.
├── backend/
│   ├── main.py              # FastAPI application
│   ├── services/            # Business logic
│   │   ├── ocr_service.py   # OCR processing
│   │   ├── pdf_service.py   # PDF manipulation
│   │   └── generator_service.py # PDF generation
│   └── requirements.txt
├── frontend/
│   ├── app/                 # Next.js app directory
│   │   ├── components/      # React components
│   │   └── page.tsx         # Main page
│   ├── components/ui/        # shadcn/ui components
│   └── lib/                 # Utilities
└── .github/workflows/       # CI/CD workflows
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License

