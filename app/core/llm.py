from langchain_google_genai import ChatGoogleGenerativeAI
from functools import lru_cache

@lru_cache(maxsize=1)
def get_llm():
    return ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.2)