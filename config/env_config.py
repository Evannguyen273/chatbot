"""
Environment Configuration Loader
Centralized environment variable management for the H&M Data Assistant
"""
import os
import json
from typing import Dict, Any, Optional

class EnvironmentConfig:
    """Centralized configuration management from environment variables"""
    
    def __init__(self):
        """Load and validate all environment variables"""
        self.load_config()
    
    def load_config(self):
        """Load all configuration from environment variables"""
        
        # BigQuery Configuration
        self.service_account_key = self._load_service_account_key()
        self.project_id = os.getenv("PROJECT_ID", "enterprise-dashboardnp-cd35")
        self.team_services_table = os.getenv("TEAM_SERVICES_TABLE")
        self.incident_table = os.getenv("INCIDENT_TABLE") 
        self.problem_table = os.getenv("PROBLEM_TABLE")
        
        # Azure OpenAI Configuration
        self.azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.azure_openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-12-01-preview")
        self.azure_openai_chat_deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "gpt-4o-mini")
        
        # Azure OpenAI Embeddings Configuration
        self.azure_openai_embedding_endpoint = os.getenv("AZURE_OPENAI_EMBEDDING_ENDPOINT")
        self.azure_openai_embedding_model = os.getenv("AZURE_OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
        self.azure_openai_embedding_api_version = os.getenv("AZURE_OPENAI_EMBEDDING_API_VERSION", "2023-05-15")
        self.azure_openai_embedding_key = os.getenv("AZURE_OPENAI_EMBEDDING_KEY")
        
        # Azure Blob Storage Configuration
        self.blob_connection_string = os.getenv("BLOB_CONNECTION_STRING")  # For schemas/prompts
        self.blob_connection_string_conversation = os.getenv("BLOB_CONNECTION_STRING_CONVERSATION")  # For user sessions
        self.user_session_container = os.getenv("USER_SESSION_CONTAINER", "chatbot-conversation")
        
        # Application Configuration
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.use_unicode = os.getenv("USE_UNICODE", "true").lower() == "true"
        self.debug_mode = os.getenv("DEBUG", "false").lower() == "true"
        self.llm_model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
    
    def _load_service_account_key(self) -> Optional[Dict[str, Any]]:
        """Load and parse Google Cloud service account key"""
        service_account_json = os.getenv("SERVICE_ACCOUNT_KEY_PATH")
        if service_account_json:
            try:
                return json.loads(service_account_json)
            except json.JSONDecodeError as e:
                print(f"Error parsing SERVICE_ACCOUNT_KEY_PATH: {e}")
                return None
        return None
    
    def get_bigquery_credentials(self) -> Dict[str, Any]:
        """Get BigQuery credentials configuration"""
        return {
            "service_account_info": self.service_account_key,
            "project_id": self.project_id
        }
    
    def get_azure_openai_config(self) -> Dict[str, str]:
        """Get Azure OpenAI configuration"""
        return {
            "endpoint": self.azure_openai_endpoint,
            "api_key": self.openai_api_key,
            "api_version": self.azure_openai_api_version,
            "deployment_name": self.azure_openai_chat_deployment
        }
    
    def get_azure_embedding_config(self) -> Dict[str, str]:
        """Get Azure OpenAI Embeddings configuration"""
        return {
            "endpoint": self.azure_openai_embedding_endpoint,
            "api_key": self.azure_openai_embedding_key,
            "api_version": self.azure_openai_embedding_api_version,
            "model": self.azure_openai_embedding_model
        }
    
    def get_blob_config(self) -> Dict[str, str]:
        """Get Azure Blob Storage configuration"""
        return {
            "schemas_connection_string": self.blob_connection_string,
            "conversation_connection_string": self.blob_connection_string_conversation,
            "user_session_container": self.user_session_container
        }
    
    def get_table_config(self) -> Dict[str, str]:
        """Get BigQuery table configuration"""
        return {
            "team_services": self.team_services_table,
            "incidents": self.incident_table,
            "problems": self.problem_table
        }
    
    def validate_config(self) -> Dict[str, bool]:
        """Validate that all required configuration is present"""
        validations = {
            "bigquery_credentials": self.service_account_key is not None,
            "azure_openai": all([
                self.azure_openai_endpoint,
                self.openai_api_key
            ]),
            "azure_embeddings": all([
                self.azure_openai_embedding_endpoint,
                self.azure_openai_embedding_key
            ]),
            "blob_storage": all([
                self.blob_connection_string,
                self.blob_connection_string_conversation
            ]),
            "tables": all([
                self.team_services_table,
                self.incident_table,
                self.problem_table
            ])
        }
        
        return validations
    
    def print_config_status(self):
        """Print configuration validation status"""
        validations = self.validate_config()
        
        print("🔧 Configuration Status:")
        for component, is_valid in validations.items():
            status = "✅" if is_valid else "❌"
            print(f"   {status} {component}")
        
        if not all(validations.values()):
            print("\n⚠️  Some configuration is missing. Check your .env file!")
        else:
            print("\n✅ All configuration validated successfully!")

# Global configuration instance
config = EnvironmentConfig()

# Export commonly used configurations
def get_config() -> EnvironmentConfig:
    """Get the global configuration instance"""
    return config