from .state import AgentState
from core.llm import get_llm
from tools import search


def retrieve_context(state: AgentState) -> AgentState:
    """Search for relevant chunks in the vector store."""
    question = state["question"]
    
    # Search for relevant chunks
    results = search(question, n_results=3)
    
    # Format context from results
    if results:
        context_parts = [f"[Chunk {i+1}]\n{r['text']}" for i, r in enumerate(results)]
        context = "\n\n".join(context_parts)
    else:
        context = ""
    
    return {**state, "context": context}


def generate_answer(state: AgentState) -> AgentState:
    """Generate answer using the retrieved context."""
    llm = get_llm(streaming=False)
    
    if state["context"]:
        prompt = f"""Answer the question based on the provided context from the documents.
If the context doesn't contain relevant information, say so.

Context:
{state["context"]}

Question: {state["question"]}

Answer:"""
    else:
        prompt = f"""No documents have been uploaded yet, or no relevant information was found.
Please let the user know they need to upload a PDF first.

Question: {state["question"]}

Answer:"""
    
    response = llm.invoke(prompt)
    return {**state, "answer": response.content}
