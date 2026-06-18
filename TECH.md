# Technology Stack

## Current stack

| Layer | Technology |
|---|---|
| API | FastAPI + Uvicorn |
| LLM | GPT-4 (OpenAI) |
| Embeddings | `text-embedding-ada-002` (OpenAI) |
| Vector DB | Qdrant Cloud (Frankfurt, AWS) |
| RAG chain | LangChain Classic (`RetrievalQA`) |
| PDF parsing | PyPDFLoader (LangChain Community) |
| Config | python-dotenv |

## Future improvements

| Area | Technology | Why |
|---|---|---|
| Cheaper/faster embeddings | `text-embedding-3-small` | 5× cheaper than ada-002, same quality |
| Faster LLM | GPT-4o-mini | 10× cheaper than GPT-4, good enough for retrieval-based answers |
| Async ingestion queue | Celery + Redis | Replace background threads — survives crashes, retries on failure, scalable across workers |
| Better chunking | LlamaIndex node parsers | Splits by sentence/paragraph boundaries instead of character count — better context preservation for legal text |
| Hybrid search | Qdrant sparse + dense vectors | Combine semantic search with keyword (BM25) matching — critical for legal docs where exact article numbers matter |
| Re-ranking | Cohere Rerank or cross-encoder | Re-scores the top-k results before sending to GPT — reduces irrelevant context in the prompt |
| Caching | Redis semantic cache | Cache answers for similar questions — avoids redundant OpenAI calls |
| Auth | JWT / API keys | Protect endpoints before any production use |
| Observability | LangSmith or Langfuse | Trace every RAG call — see what chunks were retrieved, latency, token usage |
| Multiple file formats | Unstructured.io | Parse Word, HTML, scanned PDFs (OCR) — not just clean PDFs |
