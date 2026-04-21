"""
FastAPI PDF Text Extraction API
AI Team Task - 27/feb/26

Endpoint: POST /extract-pdf
- Accepts only PDF files
- Validates file format
- Extracts first 200 characters of text
- Returns structured JSON response
- Handles empty or null PDFs gracefully
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import PyPDF2
import io
import traceback
from datetime import datetime

app = FastAPI(
    title="PDF Text Extractor API",
    description="A FastAPI backend that accepts a PDF file, extracts the starting 200 characters, and returns a structured JSON response.",
    version="1.0.0",
)


# ─────────────────────────────────────────────
# Helper: validate that the upload is a PDF
# ─────────────────────────────────────────────
def validate_pdf(file: UploadFile) -> None:
    """
    Raises HTTPException(400) if the uploaded file is not a PDF.
    Checks both the MIME content-type and the file extension.
    """
    allowed_content_type = "application/pdf"
    if file.content_type != allowed_content_type:
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "message": f"Invalid file type '{file.content_type}'. Only PDF files are accepted.",
                "accepted_format": "application/pdf",
            },
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "message": f"Invalid file extension. File must have a '.pdf' extension.",
                "received_filename": file.filename,
            },
        )


# ─────────────────────────────────────────────
# Helper: extract first 200 characters from PDF
# ─────────────────────────────────────────────
def extract_text_from_pdf(file_bytes: bytes) -> dict:
    """
    Reads PDF bytes and extracts the first 200 characters of text.
    Returns a dict with extraction details.
    """
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail={
                "status": "error",
                "message": "Failed to parse the PDF file. The file may be corrupted.",
                "error": str(e),
            },
        )

    # Handle encrypted / password-protected PDFs
    if reader.is_encrypted:
        try:
            # Many PDFs use an empty password for owner-level restrictions
            if not reader.decrypt(""):
                raise HTTPException(
                    status_code=400,
                    detail={
                        "status": "error",
                        "message": "The PDF is password-protected and cannot be read without a password.",
                    },
                )
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "message": "The PDF is encrypted and could not be decrypted.",
                },
            )

    total_pages = len(reader.pages)

    # Handle PDF with zero pages
    if total_pages == 0:
        return {
            "extracted_text": None,
            "characters_extracted": 0,
            "total_pages": 0,
            "is_empty": True,
            "note": "The PDF file contains no pages.",
        }

    # Accumulate text across pages until we have 200 chars
    full_text = ""
    for page in reader.pages:
        page_text = page.extract_text() or ""
        full_text += page_text
        if len(full_text) >= 200:
            break

    full_text = full_text.strip()

    # Handle PDF with pages but no extractable text
    if not full_text:
        return {
            "extracted_text": None,
            "characters_extracted": 0,
            "total_pages": total_pages,
            "is_empty": True,
            "note": "The PDF contains pages but no extractable text (may be image-based/scanned).",
        }

    preview = full_text[:200]

    return {
        "extracted_text": preview,
        "characters_extracted": len(preview),
        "total_pages": total_pages,
        "is_empty": False,
        "note": None,
    }


# ─────────────────────────────────────────────
# Root endpoint
# ─────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "running",
        "message": "PDF Text Extractor API is live. POST a PDF to /extract-pdf",
        "docs": "/docs",
    }


# ─────────────────────────────────────────────
# Main endpoint: POST /extract-pdf
# ─────────────────────────────────────────────
@app.post("/extract-pdf", tags=["PDF"])
async def extract_pdf(file: UploadFile = File(..., description="Upload a PDF file")):
    """
    **Accepts** a PDF file upload and returns a JSON response containing:
    - `status`: success / error
    - `filename`: original file name
    - `file_size_bytes`: size of the uploaded file
    - `extracted_text`: first 200 characters of text in the PDF
    - `characters_extracted`: exact count of extracted characters
    - `total_pages`: number of pages in the PDF
    - `is_empty`: true if the PDF has no readable text
    - `timestamp`: UTC timestamp of the request
    """

    try:
        # ── Step 1: Validate file format ──────────────────────────
        validate_pdf(file)

        # ── Step 2: Read file bytes ────────────────────────────────
        file_bytes = await file.read()

        # Guard against a completely null / zero-byte upload
        if not file_bytes:
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "message": "The uploaded file is empty (0 bytes).",
                    "filename": file.filename,
                },
            )

        file_size = len(file_bytes)

        # ── Step 3: Extract text ───────────────────────────────────
        extraction = extract_text_from_pdf(file_bytes)

        # ── Step 4: Build and return structured JSON response ──────
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "filename": file.filename,
                "file_size_bytes": file_size,
                "extracted_text": extraction["extracted_text"],
                "characters_extracted": extraction["characters_extracted"],
                "total_pages": extraction["total_pages"],
                "is_empty": extraction["is_empty"],
                "note": extraction["note"],
                "timestamp": datetime.utcnow().isoformat() + "Z",
            },
        )

    except HTTPException:
        # Re-raise known HTTP exceptions so FastAPI handles them normally
        raise

    except Exception as e:
        # Catch-all for unexpected errors — log the traceback and return JSON 500
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "An unexpected error occurred while processing the PDF.",
                "detail": str(e),
            },
        )
