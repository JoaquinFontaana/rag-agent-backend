from fastapi import FastAPI,UploadFile
from fastapi.responses import JSONResponse
from rag.store import ingest_file
app = FastAPI()

@app.post("/documents")
def add_document(file:UploadFile):
    ingest_file(file)
    return JSONResponse(content="File uploaded sucessfull",status_code=201)
    