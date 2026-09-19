from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.rag.vectorstore import get_vectorstore


DOCUMENTS_PATH = Path("app/rag/documents/travel_guides")


def load_documents():

    documents = []

    for file_path in DOCUMENTS_PATH.glob("*.md"):

        text = file_path.read_text(
            encoding="utf-8"
        )

        documents.append(
            Document(
                page_content=text,
                metadata={
                    "source": str(file_path),
                    "type": "travel_guide",
                },
            )
        )

    return documents


def ingest_documents():

    documents = load_documents()

    if not documents:
        print("No documents found.")
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
    )

    chunks = splitter.split_documents(documents)

    vectorstore = get_vectorstore()

    vectorstore.add_documents(chunks)

    print(f"Loaded {len(documents)} documents.")
    print(f"Created {len(chunks)} chunks.")
    print("RAG ingestion completed.")


if __name__ == "__main__":
    ingest_documents()