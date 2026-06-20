"""Extract + clean per-page text from a digital PDF using PyMuPDF."""
import re
from typing import List, Dict
import fitz

_NOISE = re.compile(
    r"(?:"
    r"Click\s+here\s+premium_educationn?"
    r"|Join\s+@premium_educationn?"
    r"|@premium_educationn?"
    r"|Premium[_\s]Education"
    r"|(?:Mathematics|Physics|Chemistry)\s+(?:Single\s+Correct|Numerical)\s*\(Maximum\s+Marks\s*:\s*\d+\)"
    r"|This\s+section\s+contains\s+(?:TWENTY|FIVE|TEN)\s*\(\d+\)\s+questions\."
    r"|Each\s+question\s+has\s+FOUR\s+options.*?correct\s+answer\."
    r"|For\s+each\s+question,\s+choose\s+the\s+option.*?correct\s+answer\."
    r"|ONLY\s+ONE\s+of\s+these\s+four\s+options\s+is\s+the\s+correct\s+answer\."
    r"|Answer\s+must\s+be\s+typed\s+into\s+the\s+input\s+box\."
    r"|Answer\s+to\s+each\s+question\s+will\s+be\s+evaluated.*?cases\."
    r"|Full\s+Marks\s*:.*?chosen"
    r"|Zero\s+Marks\s*:.*?unanswered\)"
    r"|Negative\s+Marks\s*:.*?cases\."
    r"|Question\s+Type\s*:.*?Negative\s+Marks\s*:\s*-?\d+"
    r"|Marks\s+for\s+correct\s+answer\s*:\s*\d+"
    r")",
    re.I | re.S,
)

_SUBJECT_MARKER = re.compile(
    r"^(Mathematics\s+(?:Single\s+Correct|Numerical)"
    r"|Physics\s+(?:Single\s+Correct|Numerical)"
    r"|Chemistry\s+(?:Single\s+Correct|Numerical))$",
    re.I | re.M,
)

_MULTI_BLANK = re.compile(r"\n{3,}")
_BULLET_ONLY = re.compile(r"^\s*[•·▪]\s*$", re.M)


def _inject_markers(raw: str) -> str:
    def replacer(m):
        h = m.group(1).lower()
        if "mathematics" in h:
            return "\n[SUBJECT:Mathematics]\n"
        elif "physics" in h:
            return "\n[SUBJECT:Physics]\n"
        elif "chemistry" in h:
            return "\n[SUBJECT:Chemistry]\n"
        return "\n"
    return _SUBJECT_MARKER.sub(replacer, raw)


def _clean(raw: str) -> str:
    text = _inject_markers(raw)
    text = _NOISE.sub("\n", text)
    text = _BULLET_ONLY.sub("", text)
    text = _MULTI_BLANK.sub("\n\n", text)
    return text.strip()


def extract_pages_text(pdf_bytes: bytes) -> List[Dict]:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    try:
        pages = []
        for i in range(doc.page_count):
            raw = doc[i].get_text("text") or ""
            pages.append({"page_number": i + 1, "text": _clean(raw)})
        return pages
    finally:
        doc.close()
