from langchain_chroma import Chroma
from functools import lru_cache
from langsmith import traceable
from config import settings
from src.rag import get_embedding_function
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import logging
from fastapi import UploadFile,HTTPException
import shutil
import os
from datetime import datetime
logger = logging.getLogger(__name__)

@traceable
@lru_cache()
def get_vector_store() -> Chroma:
    return Chroma(
        collection_name="data",
        embedding_function=get_embedding_function(),
        persist_directory=settings.vector_store_path
        )
@traceable
def ingest_file(file:UploadFile) -> str:
    try:
        # Validate input
        if not file:
            logger.warning("No file provided to add_documents")
            raise ValueError("No file provided to add")
        
        filename = file.filename or "unknown"
        document_id = f"{filename}_{datetime.now().timestamp()}"
        
        documents = parse_to_document(file)

        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=700,
            chunk_overlap=100
        )
        
        chunks = text_splitter.split_documents(documents)
        
        if not chunks:
            logger.warning("No chunks generated from documents")
            raise ValueError("No chunks generated from documents")
        
        # Add metadata to chunks
        for i, chunk in enumerate(chunks):
            chunk.metadata.update({
                "document_id": document_id,
                "filename": filename,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "uploaded_at": datetime.now().isoformat()
            })
        
        # Add chunks to vector store
        vector_store = get_vector_store()
        vector_store.add_documents(chunks)
        
        logger.info(f"Successfully added {len(chunks)} chunks from {len(documents)} documents")
        return document_id
        
    except Exception as e:
        logger.error(f"Error adding documents to vector store: {str(e)}", exc_info=True)
        raise
@traceable(
        run_type="parser"
)
def parse_to_document(file:UploadFile) -> list[Document]:
    temp_file_path = f"temp_{file.filename}"
    
    try:
        # Guardar el archivo subido en disco temporalmente
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        #Seleccionar el Loader según la extensión
        if not file.filename:
            raise HTTPException(status_code=400, detail="Nombre de archivo no proporcionado")
        
        if file.filename.endswith(".pdf"):
            loader = PyPDFLoader(temp_file_path)

        elif file.filename.endswith(".txt"):
            loader = TextLoader(temp_file_path)
        elif file.filename.endswith(".md"):
            loader = UnstructuredMarkdownLoader(temp_file_path)
        else:
            raise HTTPException(status_code=400, detail="Formato no soportado")
            
        documents = loader.load()
        
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # 6. Limpieza: Borrar archivo temporal siempre
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@traceable
def list_documents() -> list[dict]:
    """List all unique documents in the vector store"""
    try:
        vector_store = get_vector_store()
        collection = vector_store._collection
        
        # Get all documents with metadata
        results = collection.get(include=["metadatas"])
        
        if not results or not results.get("metadatas"):
            return []
        
        # Group by document_id to get unique documents
        documents_map = {}
        metadatas = results.get("metadatas")
        if metadatas:
            for metadata in metadatas:
                if metadata and "document_id" in metadata:
                    doc_id = metadata["document_id"]
                    if doc_id not in documents_map:
                        documents_map[doc_id] = {
                            "document_id": doc_id,
                            "filename": metadata.get("filename", "unknown"),
                            "uploaded_at": metadata.get("uploaded_at", ""),
                            "total_chunks": metadata.get("total_chunks", 0),
                        }
        
        return list(documents_map.values())
        
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}", exc_info=True)
        return []

@traceable
def delete_document(document_id: str) -> bool:
    """Delete all chunks of a specific document"""
    try:
        vector_store = get_vector_store()
        collection = vector_store._collection
        
        # Get all IDs for this document
        results = collection.get(
            where={"document_id": document_id},
            include=["metadatas"]
        )
        
        if not results or not results.get("ids"):
            logger.warning(f"No document found with ID: {document_id}")
            return False
        
        # Delete all chunks
        collection.delete(ids=results["ids"])
        logger.info(f"Successfully deleted document {document_id} ({len(results['ids'])} chunks)")
        return True
        
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {str(e)}", exc_info=True)
        return False

@traceable
def get_document_chunks(document_id: str) -> list[dict]:
    """Get all chunks for a specific document"""
    try:
        vector_store = get_vector_store()
        collection = vector_store._collection
        
        # Get all chunks for this document
        results = collection.get(
            where={"document_id": document_id},
            include=["metadatas", "documents"]
        )
        
        if not results or not results.get("ids"):
            return []
        
        chunks = []
        ids = results.get("ids") or []
        documents = results.get("documents") or []
        metadatas = results.get("metadatas") or []
        
        for i, chunk_id in enumerate(ids):
            chunks.append({
                "id": chunk_id,
                "content": documents[i] if i < len(documents) else "",
                "metadata": metadatas[i] if i < len(metadatas) else {},
            })
        
        # Sort by chunk_index
        chunks.sort(key=lambda x: x["metadata"].get("chunk_index", 0))
        return chunks
        
    except Exception as e:
        logger.error(f"Error getting chunks for document {document_id}: {str(e)}", exc_info=True)
        return []