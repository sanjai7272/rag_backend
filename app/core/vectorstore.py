from langchain_pinecone import PineconeVectorStore
from app.core.config import PINECONE_INDEX_NAME
from app.core.embeddings import get_embeddings

def load_documents(chunks):
    embeddings = get_embeddings()
    PineconeVectorStore.from_documents(
        chunks, embeddings, index_name=PINECONE_INDEX_NAME
    )

def get_vector_store():
    embeddings = get_embeddings()
    return PineconeVectorStore.from_existing_index(
        PINECONE_INDEX_NAME, embeddings
    )

def delete_vector_store():
    vectorstore = get_vector_store()
    vectorstore.delete(delete_all=True)