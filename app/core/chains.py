from typing import List
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

from app.core.llm import get_llm
from app.core.vectorstore import get_vector_store

def response(query: str, history: List[dict] = []):
    vectorstore = get_vector_store()
    if not vectorstore:
        return "The document store is empty or corrupted. Please upload documents first."

    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Answer the user's question based on the context provided and the chat history. If you don't know the answer, just say that you don't know. Don't try to make up an answer.\n\nContext: {context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ])

    chat_history = []
    for msg in history:
        if msg.get("role") == "user":
            chat_history.append(HumanMessage(content=msg.get("content")))
        elif msg.get("role") == "assistant":
            chat_history.append(AIMessage(content=msg.get("content")))
            
    retriever = vectorstore.as_retriever()
    document_chain = create_stuff_documents_chain(llm, prompt)
    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    result = retrieval_chain.invoke({
        "input": query,
        "chat_history": chat_history
    })

    return result["answer"]

