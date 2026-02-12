from src.utils.state import AgentState
from langgraph.graph import END

def check_human_active(state: AgentState):
    """
    Check at START if human is active.
    If yes, route directly to human_handoff for multi-turn conversation.
    If no, proceed with normal classification flow.
    """
    if state.get("human_active", False):
        return "human_handoff"
    return "classification_query"

def routing_after_classification(state:AgentState):
    if state.get("error"):
        return "handle_technical_error"
    classification = state.get("classification_query")

    category = classification.category
    
    if category == "appropriate":
        if classification.needs_retrieval:
            return "retrieve"
        else:
            return "generate_response"
    else:
        if category == "needs_human":
            return "waiting_human_response"
        else:
            return "handle_classification_error"
    
def routing_after_retrieve(state:AgentState):
    if state.get("error"):
        return "handle_technical_error"
    return "generate_response"

def routing_after_human_handoff(state:AgentState):
    if state.get("human_active"):
        return "human_handoff"
    else:
        return END