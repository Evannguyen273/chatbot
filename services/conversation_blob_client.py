"""
Azure Blob Client for User Conversations
Separate blob client for user session storage using conversation connection string
"""
import os
from azure.storage.blob import BlobServiceClient

class ConversationBlobClient:
    """Azure Blob client specifically for user conversation storage"""
    
    def __init__(self, connection_string: str = None, container_name: str = None):
        """Initialize blob client for conversation storage"""
        # Use provided parameters or environment variables
        self.connection_string = connection_string or os.getenv("BLOB_CONNECTION_STRING_CONVERSATION")
        self.container_name = container_name or os.getenv("USER_SESSION_CONTAINER", "chatbot-conversation")
        
        if not self.connection_string:
            raise ValueError("BLOB_CONNECTION_STRING_CONVERSATION not found in environment variables")
        
        # Initialize Azure Blob Service Client
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        self.container_client = self.blob_service_client.get_container_client(self.container_name)
        
        # Ensure container exists
        self._ensure_container_exists()
    
    def _ensure_container_exists(self):
        """Create container if it doesn't exist"""
        try:
            self.container_client.create_container()
            print(f"✅ Created conversation container: {self.container_name}")
        except Exception as e:
            if "ContainerAlreadyExists" in str(e):
                print(f"✅ Conversation container exists: {self.container_name}")
            else:
                print(f"❌ Error with conversation container: {e}")
    
    def upload_text_file(self, blob_path: str, content: str, overwrite: bool = True):
        """Upload text content to blob storage"""
        try:
            blob_client = self.container_client.get_blob_client(blob_path)
            blob_client.upload_blob(content, overwrite=overwrite)
            return True
        except Exception as e:
            print(f"Error uploading to {blob_path}: {e}")
            return False
    
    def fetch_text_file(self, blob_path: str) -> str:
        """Fetch text content from blob storage"""
        try:
            blob_client = self.container_client.get_blob_client(blob_path)
            blob_content = blob_client.download_blob()
            return blob_content.readall().decode('utf-8')
        except Exception as e:
            print(f"Error fetching {blob_path}: {e}")
            raise
    
    def blob_exists(self, blob_path: str) -> bool:
        """Check if blob exists"""
        try:
            blob_client = self.container_client.get_blob_client(blob_path)
            blob_client.get_blob_properties()
            return True
        except Exception:
            return False
    
    def delete_blob(self, blob_path: str) -> bool:
        """Delete blob from storage"""
        try:
            blob_client = self.container_client.get_blob_client(blob_path)
            blob_client.delete_blob()
            return True
        except Exception as e:
            print(f"Error deleting {blob_path}: {e}")
            return False
    
    def list_user_blobs(self, user_id: str) -> list:
        """List all blobs for a specific user"""
        try:
            blobs = self.container_client.list_blobs(name_starts_with=f"{user_id}/")
            return [blob.name for blob in blobs]
        except Exception as e:
            print(f"Error listing blobs for user {user_id}: {e}")
            return []

def create_conversation_blob_client() -> ConversationBlobClient:
    """Factory function to create conversation blob client"""
    return ConversationBlobClient()

# Create default instance for backward compatibility
# This can be removed once all code is updated to use the factory function
try:
    conversation_blob_client = create_conversation_blob_client()
except Exception as e:
    print(f"Warning: Could not create default conversation blob client: {e}")
    conversation_blob_client = None