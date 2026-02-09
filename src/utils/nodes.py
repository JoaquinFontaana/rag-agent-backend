from src.utils.llm import get_llm
from src.utils.state import AgentState
from src.utils.prompts import ClassificationOutput, CLASSIFICATOR_PROMPT, ANSWER_PROMPT
from typing import cast
from src.rag.retriever import retrieve_documents
from logging import getLogger
from langgraph.types import interrupt
from langchain_core.messages import AIMessage, HumanMessage
logger = getLogger(__name__)

def classification_query(state:AgentState):
    user_query = state.get("user_query")
    if not user_query:
        logger.error("The user query was empty in the classificate node")
        return {"error": "Input query cannot be empty"}
    try:
        llm = get_llm()

        structured_llm = llm.with_structured_output(
            ClassificationOutput,
            method="function_calling"
            )
        
        chain = CLASSIFICATOR_PROMPT | structured_llm

        result = cast(ClassificationOutput,chain.invoke({"query": user_query}))
        logger.info(f"Classification query result: {str(result)}")

        return {"classification_query": result, "messages":[HumanMessage(user_query)]}
    except Exception as e:
            logger.error(f"LLM Classification Error: {e}")
            return {"error": f"Error classifying query: {str(e)}"}


def retrieve(state:AgentState):
    try:
        docs = retrieve_documents(state["user_query"])
        return {"retrieved_docs":docs}
    except Exception as ex:
        msg = f"An error occurred in the retriever node. {str(ex)}"
        logger.error(f"Error in retrieve node: {msg}")
        return {"error":msg}

def handle_classification_error(state: AgentState):
    """Handles inappropriate queries."""

    classification = state.get("classification_query")

    error_messages = {
        "inappropriate": "I cannot help you with that type of query. Please keep the conversation appropriate.",
        "out_of_scope": f"Query out of scope: {classification.reason}. Please ask about our services.",
    }

    message = error_messages.get(
        classification.category,
        f"Could not process your query: {classification.reason}"
    )
    return {
        "response": message,
        "messages": [
            AIMessage(content=message)
        ] 
    }

def handle_technical_error(state: AgentState):
    """Handles technical errors (retrieval failures, etc)."""
    error_msg = state.get("error", "An unexpected error occurred")

    user_message = (
        "I'm experiencing technical difficulties accessing the knowledge base. "
        "Please try again in a moment, or rephrase your question."
    )
    
    logger.error(f"Technical error: {error_msg}")
    
    return {
        "response": user_message,
        "messages": [AIMessage(user_message)]
        }

def generate_response(state: AgentState):
    """Genera respuesta usando historial completo de conversación."""
    try:
        llm = get_llm()
        docs = state.get("retrieved_docs", [])

        # Preparar contexto
        if docs:
            context = "\n\n".join([doc.page_content for doc in docs])
            logger.info(f"Generating response with {len(docs)} retrieved documents")
        else:
            context = "No additional context available."
            logger.info("Generating response without retrieved documents")
        
        # Usar template con historial
        chain = ANSWER_PROMPT | llm
        
        response = chain.invoke({
            "context": context,
            "history": state["messages"]  
        }).content
        
        logger.info("Response generated successfully")
        
        return {
            "response": response,
            "messages": [AIMessage(content=response)]
        }
    
    except Exception as ex:
        logger.error(f"Generate response node: An exceptions has ocurred {str(ex)}")
        return {"error": str(ex)}
    
def human_handoff(state: AgentState):
    classification = state["classification_query"]
    
    if not state.get("human_active", False):
        # Initial handoff - interrupt with context
        interrupt({
            "type": "initial_handoff",
            "reason": classification.reason,
            "instruction": "Review and respond to user query",
            "query": state["user_query"]
        })
        # Execution pauses here until human resumes via Studio/LangSmith
        return {"human_active": True}  # Set on resume
    
    # On resume: human input is in state via SDK update_state()
    # Assume human sets state["human_response"] + state["human_action"] = "resolve"/"continue"
    human_action = state.get("human_action", "resolve")
    human_response = state.get("human_response", "")
    
    if human_action == "resolve":
        return {
            "response": human_response,
            "human_active": False,
            "messages": [AIMessage(content=human_response)]
        }
    else:  # continue conversation
        return {
            "response": human_response,
            "human_active": True,
            "messages": [AIMessage(content=human_response)]
        }