from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import uuid
import json
from pathlib import Path

from services.ocr_service import OCRService
from services.pdf_service import PDFService
from services.generator_service import GeneratorService

app = FastAPI(title="Programmable PDF Editor API")

# CORS middleware - read from environment variable
cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000")
# Handle both comma-separated and space-separated origins
cors_origins = [origin.strip() for origin in cors_origins_str.replace(",", " ").split() if origin.strip()]

# Log CORS origins for debugging
print(f"CORS Origins configured: {cors_origins}")
print(f"CORS_ORIGINS env var: {os.getenv('CORS_ORIGINS', 'NOT SET')}")

# If CORS_ORIGINS is not set or empty, allow all origins (for debugging)
if not cors_origins or cors_origins == ["http://localhost:3000"]:
    print("WARNING: Using permissive CORS (allowing all origins)")
    cors_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if "*" not in cors_origins else ["*"],
    allow_credentials=True if "*" not in cors_origins else False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Initialize services
ocr_service = OCRService()
pdf_service = PDFService()
generator_service = GeneratorService()


class TextSection(BaseModel):
    text: str
    x: float
    y: float
    width: float
    height: float
    page: int


class ReplacementRule(BaseModel):
    section_id: str
    original_text: str  # The text to replace
    type: str  # "serial", "random", "custom"
    start_value: Optional[int] = None
    random_min: Optional[int] = None
    random_max: Optional[int] = None
    prefix: Optional[str] = ""
    suffix: Optional[str] = ""
    format: Optional[str] = None  # e.g., "%04d" for zero-padded numbers


class GenerationRequest(BaseModel):
    pdf_id: str
    rules: List[ReplacementRule]
    num_copies: int


@app.get("/")
async def root():
    return {
        "message": "Programmable PDF Editor API",
        "cors_origins": os.getenv("CORS_ORIGINS", "NOT SET")
    }


@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF file and return its ID"""
    try:
        file_id = str(uuid.uuid4())
        file_path = UPLOAD_DIR / f"{file_id}.pdf"
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        return {"pdf_id": file_id, "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ocr/{pdf_id}")
async def process_ocr(pdf_id: str):
    """Process PDF with OCR to detect text sections"""
    try:
        file_path = UPLOAD_DIR / f"{pdf_id}.pdf"
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="PDF not found")
        
        print(f"Processing OCR for PDF: {pdf_id}")
        sections = await ocr_service.process_pdf(file_path)
        print(f"OCR completed. Found {len(sections)} sections")
        return {"sections": sections}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"OCR Error: {str(e)}")
        print(f"Traceback: {error_trace}")
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")


@app.post("/api/generate")
async def generate_pdfs(request: GenerationRequest):
    """Generate multiple PDF copies with specified replacements"""
    try:
        file_path = UPLOAD_DIR / f"{request.pdf_id}.pdf"
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="PDF not found")
        
        # Generate PDFs
        output_files = await generator_service.generate_pdfs(
            file_path,
            request.rules,
            request.num_copies
        )
        
        # Create zip file with all generated PDFs
        zip_path = await generator_service.create_zip(output_files, request.pdf_id)
        
        return FileResponse(
            zip_path,
            media_type="application/zip",
            filename=f"generated_pdfs_{request.pdf_id}.zip"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/download/{pdf_id}/{copy_number}")
async def download_pdf(pdf_id: str, copy_number: int):
    """Download a specific generated PDF copy"""
    try:
        file_path = OUTPUT_DIR / f"{pdf_id}_copy_{copy_number}.pdf"
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="PDF copy not found")
        
        return FileResponse(
            file_path,
            media_type="application/pdf",
            filename=f"copy_{copy_number}.pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

