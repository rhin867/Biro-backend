from typing import List, Dict

def extract_pages_ocr(pdf_bytes: bytes, dpi: int = 150) -> List[Dict]:
    from pdf2image import convert_from_bytes
    import pytesseract
    import fitz

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    total_pages = doc.page_count
    doc.close()

    pages = []
    for i in range(total_pages):
        images = convert_from_bytes(
            pdf_bytes,
            dpi=dpi,
            first_page=i + 1,
            last_page=i + 1
        )
        if images:
            text = pytesseract.image_to_string(
                images[0], lang="eng", config="--psm 6"
            )
            pages.append({"page_number": i + 1, "text": text})
            del images
    return pages
