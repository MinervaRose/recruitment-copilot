from __future__ import annotations

from pathlib import Path
from typing import Optional


def read_uploaded_file(uploaded_file) -> str:
    """Read Streamlit uploaded TXT/PDF/DOCX files. PDF/DOCX support depends on optional libs."""
    if uploaded_file is None:
        return ""

    name = uploaded_file.name.lower()
    data = uploaded_file.getvalue()

    if name.endswith(".txt"):
        return data.decode("utf-8", errors="ignore")

    if name.endswith(".pdf"):
        try:
            from pypdf import PdfReader
            import io
            reader = PdfReader(io.BytesIO(data))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as exc:
            return f"[PDF extraction failed: {exc}]"

    if name.endswith(".docx"):
        try:
            import docx
            import io
            doc = docx.Document(io.BytesIO(data))
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception as exc:
            return f"[DOCX extraction failed: {exc}]"

    return data.decode("utf-8", errors="ignore")


def load_sample(filename: str) -> str:
    path = Path(__file__).resolve().parent.parent / "sample_data" / filename
    return path.read_text(encoding="utf-8")
