from langchain_chroma import Chroma
from functools import lru_cache
from config import settings
from embbedings import get_embbeding_function

@lru_cache()
def get_vector_store() -> Chroma:
    return Chroma(
        collection_name="data",
        embedding_function=get_embbeding_function(),
        persist_directory=settings.vector_store_path
        )
