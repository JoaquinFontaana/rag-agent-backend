from langchain_huggingface import HuggingFaceEmbeddings
from functools import lru_cache

@lru_cache()
def get_embbeding_function():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")