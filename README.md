# Backend – PDF Chat Agent

FastAPI backend with LangGraph for RAG-powered PDF conversations.

## Features

- PDF text extraction and chunking
- Embeddings generation (OpenAI)
- Vector storage with ChromaDB (local)
- LangGraph agent for RAG flow
- Streaming responses

## Structure

```
backend/
├── main.py              # FastAPI entry point
├── requirements.txt     # Dependencies
├── api/                 # API layer
│   └── routes/
│       ├── chat.py      # Chat endpoint
│       └── documents.py # PDF upload endpoint
├── agent/               # LangGraph agent
│   ├── state.py         # State definition
│   ├── nodes.py         # Node functions
│   └── graph.py         # Graph definition
├── tools/               # RAG tools
│   ├── pdf.py           # PDF processing
│   ├── embeddings.py    # Embeddings generation
│   └── vectorstore.py   # ChromaDB operations
└── core/                # Core utilities
    ├── config.py        # Configuration
    └── llm.py           # LLM wrapper
```

## API Endpoints

| Method | Endpoint              | Description              |
|--------|-----------------------|--------------------------|
| GET    | /health               | Health check             |
| POST   | /api/documents/upload | Upload PDF               |
| GET    | /api/documents        | List uploaded documents  |
| POST   | /api/chat             | Chat with documents      |
| POST   | /api/chat/stream      | Chat with streaming      |

## Quick Start

1. Create virtual environment:
```bash
python -m venv venv
```

2. Activate virtual environment:
```bash
# Windows
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```
OPENAI_API_KEY=your_key_here
```

5. Run the server:
```bash
fastapi dev main.py
```

## RAG Flow

```
┌────────────┐     ┌─────────────┐     ┌──────────┐
│   Upload   │ ──▶ │   Chunk +   │ ──▶ │  Store   │
│    PDF     │     │   Embed     │     │ ChromaDB │
└────────────┘     └─────────────┘     └──────────┘

┌────────────┐     ┌─────────────┐     ┌──────────┐
│  Question  │ ──▶ │   Search    │ ──▶ │  Answer  │
│            │     │   Context   │     │   LLM    │
└────────────┘     └─────────────┘     └──────────┘
```

1. **Upload**: User uploads PDF
2. **Process**: Extract text, split into chunks, generate embeddings
3. **Store**: Save embeddings in ChromaDB
4. **Question**: User asks a question
5. **Search**: Find relevant chunks using semantic search
6. **Answer**: LLM generates response with context
