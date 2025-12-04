from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import router

app = FastAPI(
    title="PDF Chat Agent",
    description="Chat with your PDF documents using RAG",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")


@app.get("/health")
async def health_check():
    """Basic health check."""
    return {"status": "healthy"}


@app.get("/health/detailed")
async def health_check_detailed():
    """Detailed health check with dependency validation."""
    from core.config import settings
    from tools.vectorstore import get_collection
    
    checks = {
        "api": "healthy",
        "openai_key": "configured" if settings.OPENAI_API_KEY else "missing",
    }
    
    # Check ChromaDB
    try:
        collection = get_collection()
        checks["chromadb"] = "connected"
    except Exception:
        checks["chromadb"] = "error"
    
    # Overall status
    all_ok = all(v in ["healthy", "configured", "connected"] for v in checks.values())
    
    return {
        "status": "healthy" if all_ok else "degraded",
        "checks": checks,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
