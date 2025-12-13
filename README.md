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

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions.

### Quick Deploy

**Frontend (Vercel):**
```bash
cd frontend
vercel
```

**Backend (Railway/Heroku):**
- Connect GitHub repository
- Set root directory to `backend`
- Deploy

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

