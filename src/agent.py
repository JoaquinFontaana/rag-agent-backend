from langgraph.types import RetryPolicy
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.memory import MemorySaver
from langgraph.cache.memory import InMemoryCache
from functools import lru_cache
import os
from src.utils import (
    AgentState,
    handle_classification_error,
    handle_technical_error,
    generate_response,
    retrieve,
    classification_query,
    routing_after_classification,
    routing_after_retrieve,
    human_handoff,
    check_human_active,
    OutputState,
    InputState,
    waiting_human_response
)
from src.db import get_connection_pool
@lru_cache()
def get_workflow():
    workflow = StateGraph(AgentState,output_schema=OutputState,input_schema=InputState)

    # ========== NODOS ==========
    workflow.add_node(classification_query)
    workflow.add_node(retrieve, retry_policy=RetryPolicy())
    workflow.add_node(generate_response)
    workflow.add_node( handle_classification_error)
    workflow.add_node(handle_technical_error)
    workflow.add_node(waiting_human_response)
    workflow.add_node(human_handoff)
    # ========== EDGES ==========
    # Check human_active at START for multi-turn HITL conversations
    workflow.add_conditional_edges(
        START,
        check_human_active,
        {
            "human_handoff": "human_handoff",
            "classification_query": "classification_query"
        }
    )
    
    workflow.add_conditional_edges(
        "classification_query",
        routing_after_classification,
        {
            "retrieve": "retrieve",
            "generate_response": "generate_response",
            "handle_technical_error": "handle_technical_error",
            "handle_classification_error": "handle_classification_error",
            "waiting_human_response": "waiting_human_response"
        }
    )
    
    workflow.add_conditional_edges(
        "retrieve",
        routing_after_retrieve,
        {
            "generate_response": "generate_response",
            "handle_technical_error": "handle_technical_error"
        }
    )
    workflow.add_edge("waiting_human_response","human_handoff")

    workflow.add_edge("human_handoff",END)
    workflow.add_edge("generate_response", END)
    workflow.add_edge("handle_technical_error", END)
    workflow.add_edge("handle_classification_error", END)
    
    # Use MemorySaver for development, PostgresSaver for production
    use_memory = os.getenv("ENVIRONMENT", "development") == "development"
    
    if use_memory:
        checkpointer = MemorySaver()
    else:
        pool = get_connection_pool()
        checkpointer = PostgresSaver(pool)
        checkpointer.setup()
        
    cache = InMemoryCache()

    return workflow.compile(checkpointer=checkpointer, cache=cache)