"""
Environment configuration for Azure deployment
"""
import os
import platform

def detect_environment():
    """
    Detect if running in Azure or production environment
    Returns: bool - True if Unicode should be disabled
    """
    # Check for Azure App Service environment variables
    azure_indicators = [
        'WEBSITE_SITE_NAME',  # Azure App Service
        'APPSVC_RUN_ZIP',     # Azure App Service
        'WEBSITE_INSTANCE_ID' # Azure App Service
    ]
    
    # Check for container environment
    container_indicators = [
        'DOTNET_RUNNING_IN_CONTAINER',
        'ASPNETCORE_ENVIRONMENT'
    ]
    
    # Check if any Azure indicators are present
    is_azure = any(os.getenv(var) for var in azure_indicators)
    is_container = any(os.getenv(var) for var in container_indicators)
    
    # Check platform
    is_windows_server = platform.system() == 'Windows' and 'Server' in platform.release()
    
    # Disable Unicode in these environments
    should_disable_unicode = (
        is_azure or 
        is_container or 
        is_windows_server or
        os.getenv('DISABLE_UNICODE', 'false').lower() == 'true'
    )
    
    return should_disable_unicode

def get_log_config():
    """Get logging configuration for Azure"""
    return {
        'level': os.getenv('LOG_LEVEL', 'INFO'),
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'disable_unicode': detect_environment()
    }

# Environment settings
ENVIRONMENT = {
    'is_production': os.getenv('ENVIRONMENT', 'development') == 'production',
    'disable_unicode': detect_environment(),
    'log_level': os.getenv('LOG_LEVEL', 'INFO'),
    'max_query_length': int(os.getenv('MAX_QUERY_LENGTH', '500')),
    'timeout_seconds': int(os.getenv('TIMEOUT_SECONDS', '30'))
}