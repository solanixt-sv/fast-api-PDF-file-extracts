# 📄 FastAPI PDF Text Extractor API

> **AI Team Task — 27 Feb 2026**

A lightweight FastAPI backend that accepts a PDF upload, validates it, extracts the first **200 characters** of text, and returns a clean **structured JSON response**.

---

## 🚀 Features

| Feature | Detail |
|---|---|
| Single endpoint | `POST /extract-pdf` |
| File validation | MIME type + extension check |
| Text extraction | First 200 characters |
| Empty PDF handling | Returns `is_empty: true` with a descriptive note |
| Null / 0-byte upload | Returns `400` with clear error message |
| Auto docs | Available at `/docs` (Swagger UI) |

---

## 📦 Setup

```bash
# 1. Create a virtual environment
python -m venv venv
venv\Scripts\activate      # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the server
uvicorn main:app --reload --port 8000
```

---

## 📡 Endpoint

### `POST /extract-pdf`

**Request**
- Content-Type: `multipart/form-data`
- Field name: `file`
- Accepted format: `.pdf` only

**Successful Response (200)**
```json
{
  "status": "success",
  "filename": "sample.pdf",
  "file_size_bytes": 43210,
  "extracted_text": "This is the first 200 characters extracted from the PDF...",
  "characters_extracted": 58,
  "total_pages": 3,
  "is_empty": false,
  "note": null,
  "timestamp": "2026-02-27T10:00:00.000000Z"
}
```

**Empty PDF Response (200)**
```json
{
  "status": "success",
  "filename": "blank.pdf",
  "file_size_bytes": 1024,
  "extracted_text": null,
  "characters_extracted": 0,
  "total_pages": 1,
  "is_empty": true,
  "note": "The PDF contains pages but no extractable text (may be image-based/scanned).",
  "timestamp": "2026-02-27T10:01:00.000000Z"
}
```

**Error Response (400)**
```json
{
  "status": "error",
  "message": "Invalid file type 'image/png'. Only PDF files are accepted.",
  "accepted_format": "application/pdf"
}
```

---

## 🧪 Test with curl

```bash
# Upload a PDF
curl -X POST "http://127.0.0.1:8000/extract-pdf" \
     -F "file=@your_file.pdf"

# Upload a wrong file type (triggers validation error)
curl -X POST "http://127.0.0.1:8000/extract-pdf" \
     -F "file=@image.png"
```

---

## 📁 Project Structure

```
fastapi pdf/
├── main.py           ← FastAPI app & all logic
├── requirements.txt  ← Python dependencies
└── README.md         ← This file
```
