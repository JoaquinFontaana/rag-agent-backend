from functools import lru_cache
from src.rag import get_vector_store

@lru_cache()
def get_retriever():
    return get_vector_store().as_retriever()

def retrieve_documents(query:str):
    try:  
        if not query:
            raise Exception("The query for the retriever cant be empty")  
        get_retriever().invoke(query)
    except Exception as ex:
        raise Exception(f"The retrieve query failed. {str(ex)}")