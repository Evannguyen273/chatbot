"""
Azure Blob Storage manager for user sessions and conversations
Perfect replacement for SQL Server database in legacy system
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any
from services.conversation_blob_client import conversation_blob_client
from config.blob_config import SESSION_CONFIG, BLOB_PATHS

class BlobSessionManager:
    """Manages user sessions and conversations in Azure Blob Storage"""
    
    def __init__(self, container_name: str = None):
        """Initialize with container for user sessions"""
        self.container_name = container_name or os.getenv("USER_SESSION_CONTAINER", "chatbot-conversation")
        self.blob_client = conversation_blob_client
        self.session_config = SESSION_CONFIG
        self.blob_paths = BLOB_PATHS
    
    def _get_user_path(self, user_id: str, file_type: str) -> str:
        """Generate blob path for user data"""
        return f"{user_id}/{file_type}.json"
    
    def user_exists(self, user_id: str) -> bool:
        """Check if user has existing session data"""
        try:
            conversations_path = self._get_user_path(user_id, "conversations")
            return self.blob_client.blob_exists(conversations_path)
        except Exception:
            return False
    
    def load_user_conversations(self, user_id: str) -> List[tuple]:
        """Load user conversation history - matches legacy format"""
        try:
            conversations_path = self._get_user_path(user_id, "conversations")
            content = self.blob_client.fetch_text_file(conversations_path)
            data = json.loads(content)
            
            # Convert to legacy format: [(question, answer), ...]
            conversations = []
            for entry in data.get("history", []):
                conversations.append((entry.get("user", ""), entry.get("bot", "")))
            
            return conversations
        except Exception as e:
            print(f"No existing conversations for user {user_id}: {e}")
            return []
    
    def save_user_conversations(self, user_id: str, conversations: List[tuple], 
                              conversation_data: List[Dict] = None) -> bool:
        """Save user conversations - matches legacy functionality"""
        try:
            # Prepare conversation data
            conversation_history = {
                "user_id": user_id,
                "last_updated": datetime.now().isoformat(),
                "history": [
                    {"user": q, "bot": a, "timestamp": datetime.now().isoformat()}
                    for q, a in conversations
                ],
                "detailed_data": conversation_data or []
            }
            
            # Save conversations
            conversations_path = self._get_user_path(user_id, "conversations")
            
            # Use the correct blob client method
            content = json.dumps(conversation_history, indent=2)
            self.blob_client.upload_text_file(conversations_path, content, overwrite=True)
            
            return True
        except Exception as e:
            print(f"Error saving conversations for user {user_id}: {e}")
            return False
    
    def save_user_feedback(self, user_id: str, feedback_data: Dict[str, Any]) -> bool:
        """Save user feedback data"""
        try:
            feedback_path = self._get_user_path(user_id, "feedback")
            feedback_data["last_updated"] = datetime.now().isoformat()
            
            content = json.dumps(feedback_data, indent=2)
            self.blob_client.upload_text_file(feedback_path, content, overwrite=True)
                  
            return True
        except Exception as e:
            print(f"Error saving feedback for user {user_id}: {e}")
            return False
    
    def load_user_feedback(self, user_id: str) -> Dict[str, Any]:
        """Load user feedback data"""
        try:
            feedback_path = self._get_user_path(user_id, "feedback")
            content = self.blob_client.fetch_text_file(feedback_path)
            return json.loads(content)
        except Exception as e:
            print(f"Error loading feedback for user {user_id}: {e}")
            return {"user_id": user_id, "feedback_entries": []}
    
    def get_user_session_summary(self, user_id: str) -> Dict[str, Any]:
        """Get complete user session summary"""
        try:
            conversations = self.load_user_conversations(user_id)
            feedback = self.load_user_feedback(user_id)
            
            return {
                "user_id": user_id,
                "conversation_count": len(conversations),
                "last_conversation": conversations[-1] if conversations else None,
                "feedback_count": len(feedback.get("feedback_entries", [])),
                "session_exists": len(conversations) > 0
            }
        except Exception as e:
            return {"user_id": user_id, "error": str(e), "session_exists": False}
    
    def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """Clean up sessions older than specified days"""
        # TODO: Implement cleanup logic
        # List all blobs, check timestamps, delete old ones
        pass