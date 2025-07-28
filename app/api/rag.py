import os
import tempfile
import hashlib
import json
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

from app.core.vectorstore import load_documents as load_vectorstore_documents, delete_vector_store
from app.core.chains import response
from app.core.document_processing import load_and_split_documents

router = APIRouter()

# Creating a class for the response 
class FileUploadResponse(BaseModel):
    message: str
    
# Creating a route for the API 
@router.post("/upload-files", response_model=FileUploadResponse)
async def upload_files(files: List[UploadFile] = File(...)):
    existing_hashes = set()
    if os.path.exists("processed_hashes.json"):
        try:
            with open("processed_hashes.json", "r") as f:
                existing_hashes = set(json.load(f))
        except json.JSONDecodeError:
            existing_hashes = set()
    
    new_hashes = set()
    tmp_paths = []
    
    try:
        for file in files:
            content = await file.read()
            file_hash = hashlib.sha256(content).hexdigest()
            
            if file_hash in existing_hashes:
                continue  # Skip duplicate file
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
                tmp.write(content)
                tmp_paths.append(tmp.name)
                new_hashes.add(file_hash)
        
        if tmp_paths:
            chunks = load_and_split_documents(tmp_paths)
            load_vectorstore_documents(chunks)
            # Update existing hashes with new ones
            existing_hashes.update(new_hashes)
            with open("processed_hashes.json", "w") as f:
                json.dump(list(existing_hashes), f)
        
        processed_count = len(new_hashes)
        return {"message": f"{processed_count} new file(s) processed successfully. {len(files) - processed_count} duplicate(s) skipped."}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    finally:
        # Clean up temporary files
        for path in tmp_paths:
            if os.path.exists(path):
                os.remove(path)

# RAG QUERY

# Creating a class for the query 
class RAGQuery(BaseModel):
    query: str
    history: List[dict] = []

# Creating a class for the response 
class RAGQueryResponse(BaseModel):
    answer: str
    
@router.post("/rag-query",response_model=RAGQueryResponse)
async def rag_query(query: RAGQuery):
    answer = response(query.query, query.history)
    return {"answer": answer}

@router.post("/delete-store", response_model=FileUploadResponse)
async def delete_store():
    try:
        delete_vector_store()
        return {"message": "Vector store cleared successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear vector store: {e}")
