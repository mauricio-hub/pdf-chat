from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from pathlib import Path
import shutil
import json

from tools import process_pdf, add_chunks, list_documents, delete_document


router = APIRouter()

# Directory to store uploaded PDFs
UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Tags file for persistence
TAGS_FILE = UPLOAD_DIR / "tags.json"

# Available tags
AVAILABLE_TAGS = ["books", "work", "personal", "other"]


def load_tags() -> dict:
    """Load tags from file."""
    if TAGS_FILE.exists():
        return json.loads(TAGS_FILE.read_text())
    return {}


def save_tags(tags: dict):
    """Save tags to file."""
    TAGS_FILE.write_text(json.dumps(tags))


class UploadResponse(BaseModel):
    """Response after uploading a document."""
    document_id: str
    chunks_count: int
    tag: str
    message: str


class DocumentInfo(BaseModel):
    """Document with tag."""
    id: str
    tag: str


class DocumentList(BaseModel):
    """List of documents with tags."""
    documents: list[DocumentInfo]


class DeleteResponse(BaseModel):
    """Response after deleting a document."""
    success: bool
    message: str


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    tag: str = Form(default="other")
):
    """Upload a PDF document with a tag."""
    
    # Validate file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Validate tag
    if tag not in AVAILABLE_TAGS:
        tag = "other"
    
    # Save file
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Process PDF into chunks
        chunks = process_pdf(str(file_path))
        
        if not chunks:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")
        
        # Add chunks to vector store
        document_id = file.filename.replace(".pdf", "")
        chunks_count = add_chunks(chunks, document_id)
        
        # Save tag
        tags = load_tags()
        tags[document_id] = tag
        save_tags(tags)
        
        return UploadResponse(
            document_id=document_id,
            chunks_count=chunks_count,
            tag=tag,
            message=f"Successfully processed {file.filename}"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=DocumentList)
async def get_documents():
    """List all uploaded documents with their tags."""
    doc_ids = list_documents()
    tags = load_tags()
    
    documents = [
        DocumentInfo(id=doc_id, tag=tags.get(doc_id, "other"))
        for doc_id in doc_ids
    ]
    
    return DocumentList(documents=documents)


@router.get("/tags")
async def get_tags():
    """Get available tags."""
    return {"tags": AVAILABLE_TAGS}


class UpdateTagRequest(BaseModel):
    """Request to update document tag."""
    tag: str


@router.patch("/{document_id}/tag")
async def update_document_tag(document_id: str, request: UpdateTagRequest):
    """Update the tag of a document."""
    if request.tag not in AVAILABLE_TAGS:
        raise HTTPException(status_code=400, detail="Invalid tag")
    
    tags = load_tags()
    tags[document_id] = request.tag
    save_tags(tags)
    
    return {"success": True, "document_id": document_id, "tag": request.tag}


@router.delete("/{document_id}", response_model=DeleteResponse)
async def remove_document(document_id: str):
    """Delete a document from the vector store."""
    success = delete_document(document_id)
    
    # Remove tag
    tags = load_tags()
    if document_id in tags:
        del tags[document_id]
        save_tags(tags)
    
    # Also try to delete the file
    file_path = UPLOAD_DIR / f"{document_id}.pdf"
    if file_path.exists():
        file_path.unlink()
    
    return DeleteResponse(
        success=success,
        message=f"Document {document_id} deleted" if success else "Document not found"
    )
