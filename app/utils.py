from langchain.prompts import PromptTemplate
import json
import time
import logging
from services.azure_blob_client import blob_client
from config.settings import PROMPT_FILES, SCHEMA_FILES

# Configure logging
logger = logging.getLogger(__name__)

# Load prompts and schemas at startup with error handling
def load_prompts_and_schemas():
    """Load prompts and schemas from Azure Blob Storage with fallbacks"""
    loaded_prompts = {}
    schemas_content = ""
    
    try:
        # Load prompts
        for key, file in PROMPT_FILES.items():
            try:
                content = blob_client.fetch_text_file(file)
                loaded_prompts[key] = content
                logger.info("Loaded prompt: %s", key)
            except Exception as e:
                logger.warning("Failed to load prompt %s: %s", key, str(e))
                # Provide fallback prompts
                loaded_prompts[key] = get_fallback_prompt(key)
        
        # Load schemas
        schema_parts = []
        for file in SCHEMA_FILES:
            try:
                content = blob_client.fetch_text_file(file)
                schema_parts.append(f"=== {file.upper()} ===\n{content}")
                logger.info("Loaded schema: %s", file)
            except Exception as e:
                logger.warning("Failed to load schema %s: %s", file, str(e))
                schema_parts.append(f"=== {file.upper()} ===\nSchema unavailable")
        
        schemas_content = "\n\n".join(schema_parts)
        
    except Exception as e:
        logger.error("Critical error loading prompts/schemas: %s", str(e))
        # Use complete fallbacks
        loaded_prompts = get_all_fallback_prompts()
        schemas_content = "Schema information unavailable from Azure Blob Storage"
    
    return loaded_prompts, schemas_content

def get_fallback_prompt(prompt_type: str) -> str:
    """Provide fallback prompts when Azure Blob is unavailable"""
    fallbacks = {
        "classify_intent": """
        Analyze the user input and classify intent. 
        History: {history}
        Current input: {prompt}
        
        Respond in JSON format:
        {{"intent": "greeting|general|data_query", "rephrased": "rephrased query if data_query"}}
        """,
        "general_response": """
        You are a helpful H&M data assistant.
        History: {history}
        Respond naturally to: {prompt}
        """,
        "generate_sql": """
        Generate BigQuery SQL for H&M incident/problem data.
        Query: {rephrased}
        Schemas: {schemas}
        
        Rules:
        - Use LIMIT 100
        - Only SELECT queries
        - Use BigQuery syntax
        """,
        "error_analyzer": """
        Analyze SQL error and suggest action:
        Error: {error_msg}
        Query: {sql_query}
        
        Respond in JSON:
        {{"analysis": "explanation", "action": "retry|rephrase|fail", "suggested_sql": "optional"}}
        """
    }
    return fallbacks.get(prompt_type, f"Fallback prompt for {prompt_type}")

def get_all_fallback_prompts() -> dict:
    """Get all fallback prompts"""
    return {key: get_fallback_prompt(key) for key in PROMPT_FILES.keys()}

# Load at module import
LOADED_PROMPTS, SCHEMAS = load_prompts_and_schemas()

def get_classify_prompt(history_str: str) -> str:
    """Get intent classification prompt"""
    base_prompt = LOADED_PROMPTS.get("classify_intent", get_fallback_prompt("classify_intent"))
    return PromptTemplate.from_template(base_prompt).format(history=history_str, prompt="{prompt}")

def get_general_response_prompt(history_str: str, user_prompt: str) -> str:
    """Get general response prompt"""
    base_prompt = LOADED_PROMPTS.get("general_response", get_fallback_prompt("general_response"))
    return base_prompt.format(history=history_str, prompt=user_prompt)

def get_sql_gen_prompt(rephrased: str, schemas: str = None) -> str:
    """Get SQL generation prompt"""
    if schemas is None:
        schemas = SCHEMAS
    base_prompt = LOADED_PROMPTS.get("generate_sql", get_fallback_prompt("generate_sql"))
    return base_prompt.format(rephrased=rephrased, schemas=schemas)

def get_error_analysis_prompt(error_msg: str, sql_query: str) -> str:
    """Get error analysis prompt"""
    base_prompt = LOADED_PROMPTS.get("error_analyzer", get_fallback_prompt("error_analyzer"))
    return base_prompt.format(error_msg=error_msg, sql_query=sql_query)

def exponential_backoff(retry_count: int):
    """Exponential backoff delay"""
    delay = min(2 ** retry_count, 16)  # Cap at 16 seconds
    logger.info("Waiting %d seconds before retry", delay)
    time.sleep(delay)

def parse_json_response(response: str) -> dict:
    """Parse JSON response with fallback"""
    try:
        # Clean response first
        response = response.strip()
        
        # Look for JSON in the response
        if "{" in response and "}" in response:
            start = response.find("{")
            end = response.rfind("}") + 1
            json_str = response[start:end]
            return json.loads(json_str)
        else:
            # No JSON found, return default
            return {"error": "No JSON found in response"}
            
    except json.JSONDecodeError as e:
        logger.warning("JSON parse error: %s", str(e))
        return {"error": "Invalid JSON", "raw_response": response}
    except Exception as e:
        logger.error("Unexpected error parsing JSON: %s", str(e))
        return {"error": "Parse error", "raw_response": response}

def refresh_prompts_and_schemas():
    """Refresh prompts and schemas from Azure Blob Storage"""
    global LOADED_PROMPTS, SCHEMAS
    logger.info("Refreshing prompts and schemas from Azure Blob")
    LOADED_PROMPTS, SCHEMAS = load_prompts_and_schemas()
    return {"status": "refreshed", "prompts_count": len(LOADED_PROMPTS)}