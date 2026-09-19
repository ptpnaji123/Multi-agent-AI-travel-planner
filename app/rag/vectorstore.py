import chromadb

from langchain_chroma import Chroma
from app.rag.embeddings import embeddings


CHROMA_PATH = "./chroma_db"


def get_vectorstore():

    return Chroma(
        collection_name="travel_guides",
        embedding_function=embeddings,
        persist_directory=CHROMA_PATH,
    )