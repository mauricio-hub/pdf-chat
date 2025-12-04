# Backend – PDF Chat Agent

FastAPI backend for RAG-powered PDF conversations.

## Features

- PDF text extraction and chunking
- Vector storage with ChromaDB (local)
- Semantic search for relevant context
- OpenAI LLM for answer generation
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
├── tools/               # RAG tools
│   ├── pdf.py           # PDF processing
│   └── vectorstore.py   # ChromaDB operations
└── core/                # Core utilities
    ├── config.py        # Configuration
    └── llm.py           # LLM wrapper (OpenAI)
```

## API Endpoints

| Method | Endpoint               | Description              |
|--------|------------------------|--------------------------|
| GET    | /health                | Health check             |
| POST   | /api/documents/upload  | Upload PDF               |
| GET    | /api/documents         | List uploaded documents  |
| PATCH  | /api/documents/{id}/tag| Update document tag      |
| DELETE | /api/documents/{id}    | Delete document          |
| POST   | /api/chat              | Chat with documents      |
| POST   | /api/chat/stream       | Chat with streaming      |

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

1. **Upload**: User uploads PDF with category tag
2. **Process**: Extract text, split into chunks
3. **Store**: Save in ChromaDB with metadata
4. **Question**: User asks a question
5. **Search**: Find relevant chunks (filter by document optional)
6. **Answer**: OpenAI generates response with context
