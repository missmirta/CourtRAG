import shutil
import tempfile
import os
import uuid
import threading
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from rag import ask
from ingest import ingest_file

app = FastAPI(title="Court RAG API")

jobs: dict[str, dict] = {}

def qdrant_client() -> QdrantClient:
    return QdrantClient(url=os.environ["QDRANT_URL"], api_key=os.environ["QDRANT_API_KEY"])

class Question(BaseModel):
    text: str

@app.post("/ask")
def ask_question(question: Question):
    return ask(question.text)

@app.post("/upload")
def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "processing", "filename": file.filename}

    def run():
        try:
            ingest_file(tmp_path, source_name=file.filename)
            jobs[job_id]["status"] = "done"
        except Exception as e:
            jobs[job_id]["status"] = "error"
            jobs[job_id]["error"] = str(e)
        finally:
            os.remove(tmp_path)

    threading.Thread(target=run, daemon=True).start()

    return {"job_id": job_id, "status": "processing", "filename": file.filename}

@app.get("/upload/{job_id}")
def upload_status(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return {"job_id": job_id, **job}

@app.get("/documents")
def list_documents():
    client = qdrant_client()
    sources = set()
    offset = None
    while True:
        points, offset = client.scroll(
            collection_name="court_docs",
            with_payload=True,
            limit=100,
            offset=offset,
        )
        for point in points:
            source = point.payload.get("metadata", {}).get("source")
            if source:
                sources.add(source)
        if offset is None:
            break
    return {"documents": sorted(sources)}

@app.delete("/documents/{filename:path}")
def delete_document(filename: str):
    client = qdrant_client()
    client.delete(
        collection_name="court_docs",
        points_selector=Filter(
            must=[FieldCondition(key="metadata.source", match=MatchValue(value=filename))]
        ),
    )
    return {"status": "deleted", "filename": filename}

@app.get("/health")
def health():
    return {"status": "ok"}
