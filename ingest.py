from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
import os
import sys

def ingest_file(pdf_path: str, source_name: str = None):
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()
    name = source_name or os.path.basename(pdf_path)
    for doc in docs:
        doc.metadata["source"] = name
    print(f"Loaded {len(docs)} pages from {name}")
    _embed_and_upload(docs)

def ingest_folder(pdf_folder: str):
    docs = []
    for filename in os.listdir(pdf_folder):
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(f"{pdf_folder}/{filename}")
            docs.extend(loader.load())
    print(f"Loaded {len(docs)} pages from {pdf_folder}")
    _embed_and_upload(docs)

def _embed_and_upload(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = splitter.split_documents(docs)
    print(f"Chunks: {len(chunks)}")

    embeddings = OpenAIEmbeddings()
    QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        url=os.environ["QDRANT_URL"],
        api_key=os.environ["QDRANT_API_KEY"],
        collection_name="court_docs",
    )
    print("Completed! Saved to Qdrant.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Single file:  python ingest.py path/to/file.pdf")
        print("  Folder:       python ingest.py path/to/folder/")
        sys.exit(1)

    target = sys.argv[1]
    if os.path.isfile(target):
        ingest_file(target)
    elif os.path.isdir(target):
        ingest_folder(target)
    else:
        print(f"Error: '{target}' is not a valid file or folder.")
        sys.exit(1)
