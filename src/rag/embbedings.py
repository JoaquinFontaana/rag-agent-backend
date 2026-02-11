from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from functools import lru_cache

@lru_cache()
def get_embedding_function():
    # This automatically downloads a lightweight version of the model
    return FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")