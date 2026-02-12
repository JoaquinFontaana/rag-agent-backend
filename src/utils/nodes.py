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
    # Extract latest human message from MessagesState (automatically updated)
    messages = state.get("messages", [])
    user_query = None
    
    # Get the most recent human message
    if messages and isinstance(messages[-1], HumanMessage):
        user_query = messages[-1].content

    if not user_query:
        logger.error("No human message found in messages array")
        return {"error": "Input query cannot be empty"}
    
    logger.info(f"Classifying query: {user_query}")
    
    try:
        llm = get_llm()

        structured_llm = llm.with_structured_output(
            ClassificationOutput,
            method="function_calling"
            )
        
        chain = CLASSIFICATOR_PROMPT | structured_llm

        result = cast(ClassificationOutput,chain.invoke({"query": user_query}))
        logger.info(f"Classification result: {result.category}, needs_retrieval: {result.needs_retrieval}")

        # Store user_query in state for other nodes to use
        return {"classification_query": result, "user_query": user_query}
    except Exception as e:
            logger.error(f"LLM Classification Error: {e}")
            return {"error": f"Error classifying query: {str(e)}"}


def retrieve(state:AgentState):
    try:
        # Use user_query set by classification_query node
        user_query = state.get("user_query")
        if not user_query:
            logger.error("user_query not found - classification_query should set it")
            return {"error": "No query available for retrieval"}
        
        logger.info(f"Retrieving documents for: {user_query}")
        docs = retrieve_documents(user_query)
        logger.info(f"Retrieved {len(docs)} documents")
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

def waiting_human_response(state: AgentState):
    if state.get('classification_query').category != "needs_human":
        error_message ="The response dont need human but the graph go to waiting human response node"
        logger.error(error_message)
        raise ValueError(error_message)
    waiting_message = "A human its going to join on the chat the more soon possible"

    return {"messages":[AIMessage(waiting_message)]}

def human_handoff(state: AgentState):
    """
    Human handoff node - interrupts execution for admin response.
    Multi-turn conversations work because check_human_active() at START
    routes back here when human_active=True.
    """
    # Get the latest user message from state
    messages = state.get("messages", [])
    user_message = messages[-1].content if messages and isinstance(messages[-1], HumanMessage) else state.get("user_query", "")
    
    #Interrupt to get admin response
    interrupt({
        "type": "human_handoff",
        "reason": state.get('classification_query').reason,
        "instruction": "Review and respond to user query",
        "user_message": user_message
    })
    
    # On resume: human input is in state via SDK update_state()
    # Assume human sets state["human_response"] + state["human_action"] = "resolve"/"continue"
    human_action = state.get("human_action", "resolve")
    human_response = state.get("human_response", "")
    
    if human_action == "resolve":
        return {
            "human_active": False,
            "messages": [AIMessage(content=human_response)]
        }
    else:  # continue conversation
        return {
            "human_active": True,
            "messages": [AIMessage(content=human_response)]
        }