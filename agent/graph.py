from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import retrieve_context, generate_answer


def create_rag_agent():
    """Create and return the RAG agent graph."""

    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("retrieve", retrieve_context)
    graph.add_node("generate", generate_answer)

    # Set entry point
    graph.set_entry_point("retrieve")

    # Add edges
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)

    return graph.compile()
