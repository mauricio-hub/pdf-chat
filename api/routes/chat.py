from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from core.llm import get_llm
from tools import search


router = APIRouter()


class ChatRequest(BaseModel):
    """Request body for chat endpoint."""
    message: str
    document_id: str | None = None


class ChatResponse(BaseModel):
    """Response body for chat endpoint."""
    answer: str
    context: str
    document_id: str | None


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message using RAG."""
    # Search for relevant chunks
    results = search(request.message, n_results=3, document_id=request.document_id)
    
    if results:
        context_parts = [f"[Chunk {i+1}]\n{r['text']}" for i, r in enumerate(results)]
        context = "\n\n".join(context_parts)
        
        prompt = f"""Answer the question based on the provided context from the documents.
If the context doesn't contain relevant information, say so.

Context:
{context}

Question: {request.message}

Answer:"""
    else:
        context = ""
        prompt = f"""No documents have been uploaded yet, or no relevant information was found.
Please let the user know they need to upload a PDF first.

Question: {request.message}

Answer:"""

    llm = get_llm(streaming=False)
    response = llm.invoke(prompt)

    return ChatResponse(
        answer=response.content,
        context=context[:500] if context else "",
        document_id=request.document_id,
    )


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """Process a chat message and stream the response."""

    async def generate():
        # Search for relevant chunks (with optional document filter)
        results = search(request.message, n_results=3, document_id=request.document_id)
        
        if results:
            context_parts = [f"[Chunk {i+1}]\n{r['text']}" for i, r in enumerate(results)]
            context = "\n\n".join(context_parts)
            
            prompt = f"""Answer the question based on the provided context from the documents.
If the context doesn't contain relevant information, say so.

Context:
{context}

Question: {request.message}

Answer:"""
        else:
            prompt = f"""No documents have been uploaded yet, or no relevant information was found.
Please let the user know they need to upload a PDF first.

Question: {request.message}

Answer:"""

        # Stream the response
        llm = get_llm(streaming=True)
        async for chunk in llm.astream(prompt):
            if chunk.content:
                yield chunk.content

    return StreamingResponse(generate(), media_type="text/plain")
