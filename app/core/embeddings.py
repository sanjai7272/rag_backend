from langchain_community.embeddings import HuggingFaceEmbeddings
from functools import lru_cache

@lru_cache(maxsize=1)
def get_embeddings():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"device": "cpu"})