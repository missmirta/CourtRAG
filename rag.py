from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
import os

COURT_PROMPT = PromptTemplate(
    template="""You are a legal assistant that helps analyze court cases.
                Use ONLY the provided documents to answer.
                If there is insufficient information — say so directly.
                Always indicate which document the information was taken from.

                Context from court documents:
                {context}

                Question: {question}

                Answer (with source references):""",
    input_variables=["context", "question"]
)

def load_rag_chain():
    embeddings = OpenAIEmbeddings()

    client = QdrantClient(
        url=os.environ["QDRANT_URL"],
        api_key=os.environ["QDRANT_API_KEY"],
    )
    vectorstore = QdrantVectorStore(
        client=client,
        collection_name="court_docs",
        embedding=embeddings,
    )

    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0
    )

    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(
            search_kwargs={"k": 5}
        ),
        chain_type_kwargs={"prompt": COURT_PROMPT},
        return_source_documents=True
    )

    return chain

def ask(question: str) -> dict:
    chain = load_rag_chain()
    result = chain.invoke({"query": question})

    sources = []
    for doc in result["source_documents"]:
        sources.append({
            "source": doc.metadata.get("source", "невідомо"),
            "page": doc.metadata.get("page", 0),
            "excerpt": doc.page_content[:200]
        })

    return {
        "answer": result["result"],
        "sources": sources
    }