from fastapi import APIRouter, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from src.rag.store import ingest_file, list_documents, delete_document, get_document_chunks

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
    responses={404: {"description": "Not found"}}
)

@router.post("", summary="Upload a document", description="Upload and ingest a document into the RAG system")
def add_document(file: UploadFile):
    try:
        document_id = ingest_file(file)
        return JSONResponse(
            content={
                "message": "File uploaded successfully",
                "document_id": document_id
            },
            status_code=201
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", summary="List all documents", description="Get a list of all documents in the RAG system")
def get_documents():
    try:
        documents = list_documents()
        return JSONResponse(content={"documents": documents}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{document_id}", summary="Delete a document", description="Delete a document and all its chunks from the RAG system")
def remove_document(document_id: str):
    try:
        success = delete_document(document_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        return JSONResponse(content={"message": "Document deleted successfully"}, status_code=200)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{document_id}/chunks", summary="Get document chunks", description="Get all chunks for a specific document")
def get_chunks(document_id: str):
    try:
        chunks = get_document_chunks(document_id)
        if not chunks:
            raise HTTPException(status_code=404, detail="Document not found or has no chunks")
        return JSONResponse(content={"chunks": chunks}, status_code=200)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    