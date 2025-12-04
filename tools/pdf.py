from pypdf import PdfReader
from pathlib import Path


def extract_text(file_path: str) -> str:
    """Extract all text from a PDF file."""
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text.strip()


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        if chunk.strip():
            chunks.append(chunk.strip())
        
        start = end - overlap
    
    return chunks


def process_pdf(file_path: str, chunk_size: int = 1000) -> list[str]:
    """Extract text from PDF and split into chunks."""
    text = extract_text(file_path)
    chunks = chunk_text(text, chunk_size)
    return chunks

