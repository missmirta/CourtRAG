# CourtRAG

A REST API that lets you upload Ukrainian legal documents (PDFs), stores them as vector embeddings in Qdrant, and answers natural language questions about them using GPT-4 — returning the answer along with the exact source documents it was based on.

## What it does

**CourtRAG** is a Retrieval-Augmented Generation (RAG) system built for legal research in the Ukrainian judicial and legislative domain.

The core idea: instead of asking GPT-4 to answer legal questions from memory (which hallucinate and go stale), you feed it only the relevant chunks from your own document library. The model is forced to answer strictly from what the documents say, and must cite which document it pulled from.

## How it works

1. Upload a PDF law or court document via `/upload`
2. The document is split into ~1000-character chunks and embedded (converted to vectors) using OpenAI's embedding model
3. Those vectors are stored in Qdrant — a cloud vector database — indexed for fast similarity search
4. When a question comes in via `/ask`, the system embeds the question, finds the 5 most semantically similar chunks from Qdrant, injects them into a prompt, and sends it to GPT-4
5. GPT-4 answers strictly from those chunks and the API returns both the answer and the source references

The upload is non-blocking — it returns a `job_id` immediately and processes in a background thread, so clients don't time out on large documents.

## Quick start

```bash
# Create virtual environment
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Configure credentials
cp .env.example .env
# Fill in OPENAI_API_KEY, QDRANT_URL, QDRANT_API_KEY

# Run the API
.venv/bin/uvicorn api:app --reload --port 8001
```

See [project_endpoints.md](project_endpoints.md) for all available endpoints.
