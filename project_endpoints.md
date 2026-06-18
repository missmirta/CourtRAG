---
name: project-endpoints
description: All REST API endpoints for the courtRag FastAPI app with curl examples
metadata: 
  node_type: memory
  type: project
  originSessionId: bd5a5092-6e7a-4e63-b835-e34cd749fea3
---

Base URL: `http://localhost:8001` (port 8000 is taken by Docker)

## Endpoints

### GET /health
```bash
curl http://localhost:8001/health
```

### POST /ask
```bash
curl -X POST http://localhost:8001/ask \
  -H "Content-Type: application/json" \
  -d '{"text": "What is this case about?"}'
```

### POST /upload
Accepts a PDF file, returns `job_id` immediately (ingestion runs in background thread).
```bash
curl -X POST http://localhost:8001/upload \
  --form 'file=@"/path/to/document.pdf"'
```

### GET /upload/{job_id}
Poll ingestion job status. Status values: `processing` → `done` or `error`.
```bash
curl http://localhost:8001/upload/{job_id}
```

### GET /documents
List all unique document filenames stored in Qdrant.
```bash
curl http://localhost:8001/documents
```

### DELETE /documents/{filename}
Delete all Qdrant chunks belonging to a document by filename.
```bash
curl -X DELETE http://localhost:8001/documents/filename.pdf
```

**Why:** New endpoints should be added here as they are created.
**How to apply:** When user asks about available endpoints or how to call the API, refer to this list.
