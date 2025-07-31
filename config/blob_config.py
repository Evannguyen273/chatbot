"""
Azure Blob Storage configuration for user sessions
"""
import os

# Container settings for user session storage - from environment
USER_SESSION_CONTAINER = os.getenv("USER_SESSION_CONTAINER", "chatbot-conversation")

# Blob connection string from environment
BLOB_CONNECTION_STRING_CONVERSATION = os.getenv("BLOB_CONNECTION_STRING_CONVERSATION")

# Blob path patterns
BLOB_PATHS = {
    "conversations": "{user_id}/conversations.json",
    "feedback": "{user_id}/feedback.json", 
    "metadata": "{user_id}/metadata.json"
}

# Session settings
SESSION_CONFIG = {
    "max_conversation_history": 100,  # Max conversations to keep per user
    "max_feedback_entries": 50,       # Max feedback entries per user
    "cleanup_after_days": 30,         # Clean up sessions older than 30 days
    "auto_save": True,                # Auto-save after each interaction
    "compression": False              # JSON compression (future feature)
}

# Fallback settings when blob storage is unavailable
FALLBACK_CONFIG = {
    "use_memory_only": True,
    "max_memory_sessions": 10,        # Max users to keep in memory
    "session_timeout_minutes": 60     # Clear memory sessions after 60 min
}