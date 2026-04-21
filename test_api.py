"""
test_api.py  —  End-to-end tests for the PDF Text Extractor API
Run:  python test_api.py
"""

import urllib.request
import urllib.error
import json
import io
import os

BASE_URL = "http://127.0.0.1:8000"
BOUNDARY = "----TestBoundary99"


# ── helpers ──────────────────────────────────────────────────────────────────

def post_file(filename: str, file_bytes: bytes, content_type: str = "application/pdf") -> dict:
    body = (
        f"--{BOUNDARY}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: {content_type}\r\n\r\n"
    ).encode() + file_bytes + f"\r\n--{BOUNDARY}--\r\n".encode()

    req = urllib.request.Request(
        f"{BASE_URL}/extract-pdf",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={BOUNDARY}"},
        method="POST",
    )
    try:
        r = urllib.request.urlopen(req)
        return {"http_status": r.status, "body": json.loads(r.read())}
    except urllib.error.HTTPError as e:
        return {"http_status": e.code, "body": json.loads(e.read())}


def print_result(label: str, result: dict):
    print(f"\n{'='*55}")
    print(f"  TEST : {label}")
    print(f"  HTTP : {result['http_status']}")
    print(f"  BODY :")
    print(json.dumps(result["body"], indent=4))
    print(f"{'='*55}")


# ── minimal valid PDF bytes ───────────────────────────────────────────────────

VALID_PDF = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>endobj
4 0 obj<</Length 80>>stream
BT /F1 12 Tf 72 720 Td (FastAPI PDF Extractor - AI Team Task 27 Feb 2026 - Text extraction working!) Tj ET
endstream
endobj
5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj
xref
0 6
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000274 00000 n
0000000406 00000 n
trailer<</Size 6/Root 1 0 R>>
startxref
477
%%EOF"""


# ── TEST 1: Health check ──────────────────────────────────────────────────────
print("\n" + "="*55)
print("  HEALTH CHECK  GET /")
r = urllib.request.urlopen(f"{BASE_URL}/")
print("  HTTP :", r.status)
print("  BODY :", json.dumps(json.loads(r.read()), indent=4))
print("="*55)


# ── TEST 2: Valid PDF upload ──────────────────────────────────────────────────
result = post_file("sample.pdf", VALID_PDF, "application/pdf")
print_result("Valid PDF  →  should return extracted_text", result)


# ── TEST 3: Wrong file type (image instead of PDF) ───────────────────────────
fake_png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 50   # fake PNG header
result = post_file("photo.png", fake_png, "image/png")
print_result("Wrong file type (PNG)  →  should return 400 error", result)


# ── TEST 4: Zero-byte file ────────────────────────────────────────────────────
result = post_file("empty.pdf", b"", "application/pdf")
print_result("Empty (0-byte) file  →  should return 400 error", result)


# ── TEST 5: PDF with no pages (empty PDF structure) ──────────────────────────
empty_pdf = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[]/Count 0>>endobj
xref
0 3
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
trailer<</Size 3/Root 1 0 R>>
startxref
110
%%EOF"""
result = post_file("blank.pdf", empty_pdf, "application/pdf")
print_result("PDF with 0 pages  →  should return is_empty=true", result)


print("\n✅  All test cases completed!")
