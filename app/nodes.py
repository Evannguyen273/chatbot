from typing import TypedDict, List
from langchain_openai import ChatOpenAI
from config.env_config import get_config
from app.utils import get_classify_prompt, get_general_response_prompt, get_sql_gen_prompt, get_error_analysis_prompt, exponential_backoff, parse_json_response, SCHEMAS
from services.bigquery_client import bq_client
import pandas as pd
import logging

# Load centralized configuration
config = get_config()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

llm = ChatOpenAI(model=config.llm_model)

class AgentState(TypedDict):
    user_prompt: str
    intent: str
    rephrased_prompt: str
    relevant_schemas: str
    sql_query: str
    results: str
    final_response: str
    error_msg: str
    analysis: str
    analysis_action: str  # Added missing field for error analysis action
    retry_count: int
    messages: List[dict]  # For history: [{'user': '...', 'bot': '...'}]

def classify_intent(state: AgentState) -> AgentState:
    """Classify user intent and rephrase query if needed"""
    try:
        history_str = "\n".join([f"User: {m['user']}\nBot: {m['bot']}" for m in state.get("messages", [])])
        prompt = get_classify_prompt(history_str).format(prompt=state["user_prompt"])
        response = llm.invoke(prompt).content
        parsed = parse_json_response(response)
        
        state["intent"] = parsed.get("intent", "general")
        state["rephrased_prompt"] = parsed.get("rephrased", state["user_prompt"])
        
        logger.info("Classified intent: %s", state["intent"])
        return state
        
    except Exception as e:
        logger.error("Error in classify_intent: %s", str(e))
        state["intent"] = "general"
        state["rephrased_prompt"] = state["user_prompt"]
        return state

def general_response(state: AgentState) -> AgentState:
    """Handle general/greeting responses"""
    try:
        history_str = "\n".join([f"User: {m['user']}\nBot: {m['bot']}" for m in state.get("messages", [])])
        prompt = get_general_response_prompt(history_str, state['user_prompt'])
        state["final_response"] = llm.invoke(prompt).content
        
        logger.info("Generated general response")
        return state
        
    except Exception as e:
        logger.error("Error in general_response: %s", str(e))
        # Fallback responses
        if any(greeting in state["user_prompt"].lower() for greeting in ["hi", "hello", "hey"]):
            state["final_response"] = "Hello! I'm your H&M data assistant. How can I help you with incident or problem data today?"
        else:
            state["final_response"] = "I can help you query and analyze your H&M incident and problem data. What would you like to know?"
        return state

def retrieve_schemas(state: AgentState) -> AgentState:
    """Retrieve relevant schemas from Azure Blob Storage"""
    try:
        state["relevant_schemas"] = SCHEMAS  # Loaded from Blob in utils.py
        logger.info("Retrieved schemas from Azure Blob Storage")
        return state
        
    except Exception as e:
        logger.error("Error retrieving schemas: %s", str(e))
        state["relevant_schemas"] = "Schema information unavailable"
        return state

def generate_sql(state: AgentState) -> AgentState:
    """Generate SQL query from natural language"""
    try:
        prompt = get_sql_gen_prompt(state["rephrased_prompt"], state["relevant_schemas"])
        response = llm.invoke(prompt).content
        
        # Clean up SQL response
        sql_query = response.strip()
        if "```sql" in sql_query:
            sql_query = sql_query.split("```sql")[1].split("```")[0].strip()
        elif "```" in sql_query:
            sql_query = sql_query.split("```")[1].strip()
        
        state["sql_query"] = sql_query
        logger.info("Generated SQL query")
        return state
        
    except Exception as e:
        logger.error("Error generating SQL: %s", str(e))
        state["error_msg"] = f"Failed to generate SQL query: {str(e)}"
        return state

def execute_sql(state: AgentState) -> AgentState:
    """Execute SQL query on BigQuery"""
    try:
        if not state.get("sql_query"):
            state["error_msg"] = "No SQL query to execute"
            return state
            
        df = bq_client.execute_query(state["sql_query"])
        
        if df is not None and not df.empty:
            # Limit display for large results
            if len(df) > 100:
                display_df = df.head(100)
                state["results"] = f"{display_df.to_markdown(index=False)}\n\n(Showing first 100 rows of {len(df)} total)"
            else:
                state["results"] = df.to_markdown(index=False)
            
            state["final_response"] = f"Results for '{state['user_prompt']}':\n{state['results']}"
            state["error_msg"] = ""
            logger.info("SQL executed successfully, returned %d rows", len(df))
        else:
            state["results"] = "No data found"
            state["final_response"] = "No data found matching your query."
            state["error_msg"] = ""
            
    except Exception as e:
        error_msg = str(e)
        state["error_msg"] = error_msg
        state["retry_count"] = state.get("retry_count", 0) + 1
        logger.error("SQL execution error: %s", error_msg)
        
    return state

def error_analyzer(state: AgentState) -> AgentState:
    """Analyze errors and determine next action"""
    if not state.get("error_msg"):
        state["analysis_action"] = "end"
        return state
    
    try:
        # Check retry limit
        if state.get("retry_count", 0) >= config.max_retries:
            state["analysis_action"] = "fail"
            state["final_response"] = f"Failed after {config.max_retries} attempts: {state['error_msg']}"
            return state
        
        # Analyze the error
        prompt = get_error_analysis_prompt(state["error_msg"], state["sql_query"])
        response = llm.invoke(prompt).content
        parsed = parse_json_response(response)
        
        state["analysis"] = parsed.get("analysis", "")
        action = parsed.get("action", "fail")
        
        # Map actions to valid workflow actions
        if action == "retry":
            state["analysis_action"] = "retry"
            if "suggested_sql" in parsed:
                state["sql_query"] = parsed["suggested_sql"]
            exponential_backoff(state["retry_count"])
        elif action == "rephrase":
            state["analysis_action"] = "rephrase"
        elif action == "ask_user":
            state["analysis_action"] = "ask_user"
            state["final_response"] = f"Error: {state['error_msg']}. Could you please clarify your question?"
        else:
            state["analysis_action"] = "fail"
            state["final_response"] = f"Unable to process your request: {state['error_msg']}"
        
        logger.info("Error analysis: action=%s, retry_count=%d", action, state.get("retry_count", 0))
        return state
        
    except Exception as e:
        logger.error("Error in error_analyzer: %s", str(e))
        state["analysis_action"] = "fail"
        state["final_response"] = f"An unexpected error occurred: {state['error_msg']}"
        return state

def update_history(state: AgentState) -> AgentState:
    """Update conversation history"""
    try:
        if "messages" not in state:
            state["messages"] = []
        
        state["messages"].append({
            "user": state["user_prompt"], 
            "bot": state.get("final_response", "No response generated")
        })
        
        logger.info("Updated conversation history")
        return state
        
    except Exception as e:
        logger.error("Error updating history: %s", str(e))
        return state