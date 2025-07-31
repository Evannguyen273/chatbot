"""
Environment Validation Script
Run this to verify your .env configuration is correct
"""
import os
from config.env_config import get_config

def main():
    """Validate environment configuration"""
    print("🔧 H&M Data Assistant - Environment Validation")
    print("=" * 60)
    
    try:
        # Load configuration
        config = get_config()
        
        # Print configuration status
        config.print_config_status()
        
        # Test individual components
        print("\n📋 Detailed Configuration:")
        
        # BigQuery Configuration
        bigquery_config = config.get_bigquery_credentials()
        print(f"   📊 BigQuery Project: {config.project_id}")
        print(f"   📊 Service Account: {'✅ Loaded' if bigquery_config['service_account_info'] else '❌ Missing'}")
        
        # Azure OpenAI Configuration  
        openai_config = config.get_azure_openai_config()
        print(f"   🤖 OpenAI Endpoint: {openai_config['endpoint'][:50]}..." if openai_config['endpoint'] else "❌ Missing")
        print(f"   🤖 OpenAI Deployment: {openai_config['deployment_name']}")
        
        # Azure Blob Configuration
        blob_config = config.get_blob_config()
        print(f"   💾 Schemas Blob: {'✅ Configured' if blob_config['schemas_connection_string'] else '❌ Missing'}")
        print(f"   💾 Conversation Blob: {'✅ Configured' if blob_config['conversation_connection_string'] else '❌ Missing'}")
        print(f"   💾 Container: {blob_config['user_session_container']}")
        
        # Table Configuration
        table_config = config.get_table_config()
        print(f"   📋 Incidents Table: {'✅ Set' if table_config['incidents'] else '❌ Missing'}")
        print(f"   📋 Problems Table: {'✅ Set' if table_config['problems'] else '❌ Missing'}")
        print(f"   📋 Team Services Table: {'✅ Set' if table_config['team_services'] else '❌ Missing'}")
        
        # Validation summary
        validations = config.validate_config()
        all_valid = all(validations.values())
        
        print(f"\n{'✅ Configuration Valid!' if all_valid else '❌ Configuration Issues Found'}")
        
        if not all_valid:
            print("\n⚠️  Missing Configuration:")
            for component, is_valid in validations.items():
                if not is_valid:
                    print(f"   ❌ {component}")
            
            print("\n💡 Check your .env file and ensure all required variables are set!")
        
        return all_valid
        
    except Exception as e:
        print(f"❌ Error validating configuration: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)