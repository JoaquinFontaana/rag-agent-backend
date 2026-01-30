from langchain_chroma import Chroma
from functools import lru_cache
from config import settings
from src.rag import get_embedding_function
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import logging
from fastapi import UploadFile,HTTPException
import shutil
import os
logger = logging.getLogger(__name__)

@lru_cache()
def get_vector_store() -> Chroma:
    return Chroma(
        collection_name="data",
        embedding_function=get_embedding_function(),
        persist_directory=settings.vector_store_path
        )

def ingest_file(file:UploadFile):
    try:
        # Validate input
        if not file:
            logger.warning("No file provided to add_documents")
            raise ValueError("No file provided to add")
        
        
        documents = parse_to_document(file)

        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=700,
            chunk_overlap=100
        )
        
        chunks = text_splitter.split_documents(documents)
        
        if not chunks:
            logger.warning("No chunks generated from documents")
            raise Exception("No chunks generated from documents")
        
        # Add chunks to vector store
        vector_store = get_vector_store()
        vector_store.add_documents(chunks)
        
        logger.info(f"Successfully added {len(chunks)} chunks from {len(documents)} documents")
        
    except Exception as e:
        logger.error(f"Error adding documents to vector store: {str(e)}", exc_info=True)

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