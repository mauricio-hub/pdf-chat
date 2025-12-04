from typing import TypedDict


class AgentState(TypedDict):
    """State that flows through the RAG agent."""

    question: str
    context: str
    answer: str
