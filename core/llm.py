from langchain_openai import ChatOpenAI
from .config import settings


def get_llm(streaming: bool = True) -> ChatOpenAI:
    """Create and return a configured LLM instance."""
    return ChatOpenAI(
        model=settings.MODEL_NAME,
        api_key=settings.OPENAI_API_KEY,
        streaming=streaming,
    )

