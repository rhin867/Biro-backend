import base64
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..services.pdf_detector import is_text_pdf
from ..services.text_pipeline import extract_pages_text
from ..services.parser import parse_questions, parse_answer_key_only
from ..services.diagram_cropper import attach_diagram_crops, crop_region

router = APIRouter()


class PdfBody(BaseModel):
    pdfBase64: str
    mimeType: Optional[str] = "application/pdf"


class CropBody(BaseModel):
    pdfBase64: str
    pageNumber: int
    x: float
    y: float
    width: float
    height: float
    scale: float = 2.0


def _get_pages(pdf_bytes: bytes):
    if is_text_pdf(pdf_bytes):
        return extract_pages_text(pdf_bytes), "text"
    from ..services.ocr_pipeline import extract_pages_ocr
    return extract_pages_ocr(pdf_bytes), "ocr"


@router.post("/extract")
async def extract(body: PdfBody):
    try:
        pdf_bytes = base64.b64decode(body.pdfBase64)
        pages, mode = _get_pages(pdf_bytes)
        result = parse_questions(pages)
        result["questions"] = attach_diagram_crops(pdf_bytes, result["questions"])
        result["extractionMode"] = mode
        return result
    except Exception as e:
        raise HTTPException(500, f"Extraction failed: {e}")


@router.post("/extract-answer-key")
async def extract_answer_key(body: PdfBody):
    try:
        pdf_bytes = base64.b64decode(body.pdfBase64)
        pages, _ = _get_pages(pdf_bytes)
        return {"answerKey": parse_answer_key_only(pages)}
    except Exception as e:
        raise HTTPException(500, f"Answer key extraction failed: {e}")


@router.post("/crop-region")
async def api_crop_region(body: CropBody):
    pdf_bytes = base64.b64decode(body.pdfBase64)
    try:
        url = crop_region(pdf_bytes, body.pageNumber, body.x, body.y, body.width, body.height, body.scale)
        return {"imageBase64": url}
    except Exception as e:
        raise HTTPException(400, str(e))
