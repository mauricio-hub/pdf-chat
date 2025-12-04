import chromadb
from chromadb.config import Settings
from pathlib import Path

# Initialize ChromaDB client (persistent, local storage)
_client = None
_collection = None


def get_client():
    """Get or create ChromaDB client."""
    global _client
    if _client is None:
        db_path = Path(__file__).parent.parent / "chroma_db"
        _client = chromadb.PersistentClient(path=str(db_path))
    return _client


def get_collection():
    """Get or create the documents collection."""
    global _collection
    if _collection is None:
        client = get_client()
        _collection = client.get_or_create_collection(
            name="documents",
            metadata={"description": "PDF document chunks"}
        )
    return _collection


def add_chunks(chunks: list[str], document_id: str) -> int:
    """Add text chunks to the vector store."""
    collection = get_collection()
    
    ids = [f"{document_id}_{i}" for i in range(len(chunks))]
    metadatas = [{"document_id": document_id, "chunk_index": i} for i in range(len(chunks))]
    
    collection.add(
        documents=chunks,
        ids=ids,
        metadatas=metadatas
    )
    
    return len(chunks)


def search(query: str, n_results: int = 3, document_id: str | None = None) -> list[dict]:
    """Search for relevant chunks, optionally filtering by document."""
    collection = get_collection()
    
    # Debug: list all document IDs in collection
    all_docs = list_documents()
    print(f"[DEBUG] Available documents in DB: {all_docs}")
    print(f"[DEBUG] Looking for document_id: '{document_id}'")
    
    # Build query parameters
    query_params = {
        "query_texts": [query],
        "n_results": n_results,
    }
    
    # Add filter if document_id is specified
    if document_id:
        query_params["where"] = {"document_id": document_id}
    
    results = collection.query(**query_params)
    print(f"[DEBUG] Query returned {len(results.get('documents', [[]])[0])} results")
    
    # Format results
    chunks = []
    if results["documents"] and results["documents"][0]:
        for i, doc in enumerate(results["documents"][0]):
            chunks.append({
                "text": doc,
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {}
            })
    
    return chunks


def list_documents() -> list[str]:
    """List all unique document IDs in the store."""
    collection = get_collection()
    
    all_items = collection.get()
    document_ids = set()
    
    if all_items["metadatas"]:
        for metadata in all_items["metadatas"]:
            if metadata and "document_id" in metadata:
                document_ids.add(metadata["document_id"])
    
    return list(document_ids)


def delete_document(document_id: str) -> bool:
    """Delete all chunks for a document."""
    collection = get_collection()
    
    # Get all IDs for this document
    all_items = collection.get()
    ids_to_delete = []
    
    if all_items["ids"] and all_items["metadatas"]:
        for i, metadata in enumerate(all_items["metadatas"]):
            if metadata and metadata.get("document_id") == document_id:
                ids_to_delete.append(all_items["ids"][i])
    
    if ids_to_delete:
        collection.delete(ids=ids_to_delete)
        return True
    
    return False

