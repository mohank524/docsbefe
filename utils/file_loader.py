import fitz  # PyMuPDF
from docx import Document

def load_pdf(file_bytes: bytes) -> str:
    text = []
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            text.append(page.get_text())
    return "\n".join(text)

def load_docx(file_bytes: bytes) -> str:
    doc = Document(file_bytes)
    return "\n".join(p.text for p in doc.paragraphs)

def extract_text(filename: str, file_bytes: bytes) -> str:
    if filename.lower().endswith(".pdf"):
        return load_pdf(file_bytes)
    if filename.lower().endswith(".docx"):
        return load_docx(file_bytes)
    raise ValueError("Unsupported file type")
