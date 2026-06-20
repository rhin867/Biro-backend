"""OCR fallback for scanned PDFs using pdf2image + pytesseract (lightweight)."""
from typing import List, Dict


def extract_pages_ocr(pdf_bytes: bytes, dpi: int = 200) -> List[Dict]:
    from pdf2image import convert_from_bytes
    import pytesseract

    images = convert_from_bytes(pdf_bytes, dpi=dpi)
    pages = []
    for i, img in enumerate(images):
        text = pytesseract.image_to_string(img, lang="eng")
        pages.append({"page_number": i + 1, "text": text.strip()})
    return pages
