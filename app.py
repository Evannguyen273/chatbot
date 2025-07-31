"""
H&M Data Assistant Application - Flask API + Interactive Console
"""
import sys
import os
from typing import Dict, Any
import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.graph import build_graph
from app.nodes import AgentState
from config.environment import ENVIRONMENT, detect_environment
from config.env_config import get_config
from services.blob_session_manager import BlobSessionManager
from utils.console import ProductionConsole

class DataAssistant:
    """Interactive data assistant for H&M ServiceNow data with session management"""
    
    def __init__(self, use_unicode: bool = True, use_blob_sessions: bool = True):
        """Initialize the assistant"""
        self.use_unicode = use_unicode
        self.use_blob_sessions = use_blob_sessions
        self.symbols = self._get_symbols()
        self.console = ProductionConsole() # Use the production-safe console
        
        # Session management - like your legacy system
        self.user_conversation_histories = {}  # Similar to your legacy user_conversation_histories
        self.conversation_data_db = []         # Similar to your legacy conversation_data_db
        self.feedback_and_comments = {}        # Similar to your legacy feedback_and_comments
        
        # Blob session manager (replaces SQL Server database)
        self.session_manager = None
        if use_blob_sessions:
            try:
                self.session_manager = BlobSessionManager()
                self.console.print_success("Blob session storage ready")
            except Exception as e:
                self.console.print_error(f"Blob session storage failed: {e}")
                self.use_blob_sessions = False
        
        self.console.print_init("Initializing H&M Data Assistant...")
        try:
            self.app = build_graph()
            self.console.print_success("Assistant ready!")
        except Exception as e:
            self.console.print_error(f"Failed to initialize assistant: {e}")
            sys.exit(1)
    
    def _get_symbols(self) -> Dict[str, str]:
        """Get symbols based on environment support"""
        if self.use_unicode:
            return {
                'rocket': '🚀',
                'check': '✅',
                'cross': '❌',
                'robot': '🤖',
                'thinking': '🤔',
                'target': '🎯',
                'chat': '💬',
                'wave': '👋',
                'numbers': '🔢'
            }
        else:
            return {
                'rocket': '[INIT]',
                'check': '[OK]',
                'cross': '[ERROR]',
                'robot': '[BOT]',
                'thinking': '[PROCESSING]',
                'target': '[APP]',
                'chat': '[USER]',
                'wave': '[BYE]',
                'numbers': '[TEST]'
            }
    
    def create_initial_state(self, user_prompt: str, user_id: str = None) -> Dict[str, Any]:
        """Create initial state for the workflow with conversation history"""
        # Get conversation history for this user
        messages = []
        if user_id:
            # Load from blob storage if available
            if self.session_manager and self.use_blob_sessions:
                try:
                    conversations = self.session_manager.load_user_conversations(user_id)
                    # Convert to new format and take last 3 exchanges
                    recent_conversations = conversations[-3:] if conversations else []
                    messages = [{"user": q, "bot": a} for q, a in recent_conversations]
                except Exception as e:
                    print(f"Could not load user history from blob: {e}")
            
            # Fallback to in-memory if blob fails or not available
            if not messages and user_id in self.user_conversation_histories:
                history = self.user_conversation_histories[user_id][-3:]  # Last 3 exchanges
                messages = [{"user": q, "bot": a} for q, a in history]
        
        return {
            "user_prompt": user_prompt,
            "retry_count": 0,
            "intent": "",
            "rephrased_prompt": "",
            "relevant_schemas": "",
            "sql_query": "",
            "results": "",
            "final_response": "",
            "error_msg": "",
            "analysis": "",
            "analysis_action": "",
            "messages": messages  # Include conversation history
        }
    
    def process_query(self, user_input: str, user_id: str = None) -> Dict[str, Any]:
        """Process a user query through the workflow with session management"""
        try:
            self.console.print_processing(f"Processing: {user_input}")
            
            # Create initial state with user session
            state = self.create_initial_state(user_input, user_id)
            
            # Run through the workflow
            result = self.app.invoke(state)
            
            # Extract final response and SQL query
            final_response = result.get("final_response", "Sorry, I couldn't process your request.")
            sql_query = result.get("sql_query", "No SQL generated")
            
            # Store conversation data (like legacy system)
            conversation_entry = {
                "user_query": user_input,
                "sql_query": sql_query,
                "response": final_response,
                "timestamp": datetime.now().isoformat()
            }
            self.conversation_data_db.append(conversation_entry)
            
            # Update user conversation history (both in-memory and blob)
            if user_id:
                # Update in-memory
                if user_id not in self.user_conversation_histories:
                    self.user_conversation_histories[user_id] = []
                self.user_conversation_histories[user_id].append((user_input, final_response))
                
                # Save to blob storage
                if self.session_manager and self.use_blob_sessions:
                    try:
                        self.session_manager.save_user_conversations(
                            user_id, 
                            self.user_conversation_histories[user_id],
                            [conversation_entry]
                        )
                        self.console.print_success("Saved session to blob storage")
                    except Exception as e:
                        self.console.print_error(f"Could not save to blob storage: {e}")
            
            return {
                "user_input": user_input,
                "generated_sql_query": sql_query,
                "model_response": final_response,
                "intent": result.get("intent", "unknown"),
                "success": True
            }
            
        except Exception as e:
            error_msg = f"{self.symbols['cross']} Error processing query: {str(e)}"
            self.console.print_error(f"Error processing query: {str(e)}")
            
            # Store error in conversation data
            error_entry = {
                "user_query": user_input,
                "sql_query": "Error occurred",
                "response": "I encountered an error while processing your request. Please try again.",
                "timestamp": datetime.now().isoformat()
            }
            self.conversation_data_db.append(error_entry)
            
            return {
                "user_input": user_input,
                "generated_sql_query": "Error occurred",
                "model_response": "I encountered an error while processing your request. Please try again.",
                "success": False,
                "error": str(e)
            }
    
    
    def record_feedback(self, user_id: str, user_query: str, feedback_type: str) -> str:
        """Record user feedback for a specific query with blob storage"""
        if user_id not in self.feedback_and_comments:
            self.feedback_and_comments[user_id] = []
        
        feedback_entry = {
            "query": user_query,
            "feedback": feedback_type or "user did not provide feedback like or dislike",
            "comments": "user did not provide comments",
            "timestamp": datetime.now().isoformat()
        }
        self.feedback_and_comments[user_id].append(feedback_entry)
        
        # Save to blob storage
        if self.session_manager and self.use_blob_sessions:
            try:
                feedback_data = {
                    "user_id": user_id,
                    "feedback_entries": self.feedback_and_comments[user_id]
                }
                self.session_manager.save_user_feedback(user_id, feedback_data)
                print(f"{self.symbols['check']} Feedback saved to blob storage")
            except Exception as e:
                print(f"Could not save feedback to blob storage: {e}")
        
        return "Feedback recorded successfully."
    
    def record_comment(self, user_id: str, user_query: str, comment: str) -> str:
        """Record user comment for a specific query with blob storage"""
        if user_id not in self.feedback_and_comments:
            self.feedback_and_comments[user_id] = []
        
        # Find existing feedback entry and update comment
        for entry in self.feedback_and_comments[user_id]:
            if entry["query"] == user_query:
                entry["comments"] = comment or "user did not provide comments"
                break
        else:
            # If no existing entry, create new one
            self.feedback_and_comments[user_id].append({
                "query": user_query,
                "feedback": "user did not provide feedback like or dislike",
                "comments": comment or "user did not provide comments",
                "timestamp": datetime.now().isoformat()
            })
        
        # Save to blob storage
        if self.session_manager and self.use_blob_sessions:
            try:
                feedback_data = {
                    "user_id": user_id,
                    "feedback_entries": self.feedback_and_comments[user_id]
                }
                self.session_manager.save_user_feedback(user_id, feedback_data)
                print(f"{self.symbols['check']} Comment saved to blob storage")
            except Exception as e:
                print(f"Could not save comment to blob storage: {e}")
        
        return "Comment recorded successfully."
    
    def get_conversation_data(self) -> list:
        """Get all conversation data (like legacy endpoint)"""
        return self.conversation_data_db
    
    def run_interactive(self):
        """Run interactive mode"""
        print("\n" + "="*60)
        print(f"{self.symbols['target']} H&M Data Assistant - Interactive Mode")
        print("="*60)
        print("Ask me about your ServiceNow incident and problem data!")
        print("Type 'quit', 'exit', or 'bye' to stop.")
        print("-"*60)
        
        while True:
            try:
                # Get user input
                user_input = input(f"\n{self.symbols['chat']} You: ").strip()
                
                # Check for exit commands
                if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                    print(f"{self.symbols['wave']} Goodbye! Thanks for using H&M Data Assistant.")
                    break
                
                # Skip empty input
                if not user_input:
                    print("Please enter a question or type 'quit' to exit.")
                    continue
                
                # Process the query
                response = self.process_query(user_input)
                
                # Display response
                print(f"\n{self.symbols['robot']} Assistant: {response}")
                
            except KeyboardInterrupt:
                print(f"\n\n{self.symbols['wave']} Goodbye! Thanks for using H&M Data Assistant.")
                break
            except Exception as e:
                print(f"\n{self.symbols['cross']} Unexpected error: {e}")
                print("Please try again or type 'quit' to exit.")
    
    def run_examples(self):
        """Run some example queries"""
        print("\n" + "="*60)
        print("Running Example Queries")
        print("="*60)
        
        examples = [
            "Hi there!",
            "How many incidents were created this year?",
            "Show me critical problems",
            "What's the weather like?",
            "How many days in a year?"
        ]
        
        for i, example in enumerate(examples, 1):
            print(f"\n{self.symbols['numbers']} Example {i}: {example}")
            response = self.process_query(example)
            print(f"{self.symbols['robot']} Response: {response}")
            print("-" * 40)

def main():
    """Main application entry point"""
    print("H&M Data Assistant")
    
    # Auto-detect environment and disable Unicode if needed
    use_unicode = not detect_environment()
    
    # Allow manual override
    if os.getenv('USE_UNICODE', '').lower() == 'false':
        use_unicode = False
    elif os.getenv('USE_UNICODE', '').lower() == 'true':
        use_unicode = True
    
    # Initialize assistant
    assistant = DataAssistant(use_unicode=use_unicode)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--examples":
            assistant.run_examples()
        elif sys.argv[1] == "--query":
            if len(sys.argv) > 2:
                query = " ".join(sys.argv[2:])
                response = assistant.process_query(query)
                print(f"Query: {query}")
                print(f"Response: {response}")
            else:
                print("Please provide a query after --query")
        elif sys.argv[1] == "--no-unicode":
            # Force ASCII mode
            assistant = DataAssistant(use_unicode=False)
            assistant.run_interactive()
        elif sys.argv[1] == "--api":
            # Run Flask API mode
            run_flask_api(assistant)
        else:
            print("Usage: python app.py [--examples] [--query 'question'] [--no-unicode] [--api]")
    else:
        # Run interactive mode
        assistant.run_interactive()

# Flask API Functions
def run_flask_api(assistant: DataAssistant):
    """Run Flask API with the assistant instance"""
    app = Flask(__name__)
    CORS(app)
    
    @app.route('/query', methods=['POST'])
    def query():
        """Main query endpoint - matches your legacy API"""
        data = request.json
        user_input = data.get('user_query')
        user_id = data.get('user_id')
        
        # Process query through new workflow
        result = assistant.process_query(user_input, user_id)
        
        # Return in legacy format
        return jsonify({
            'user_input': result['user_input'],
            'generated_sql_query': result['generated_sql_query'],
            'model_response': result['model_response']
        })
    
    @app.route('/feedback', methods=['POST'])
    def feedback():
        """Feedback endpoint - matches your legacy API"""
        data = request.json
        user_id = data.get('user_id')
        user_query = data.get('user_query')
        feedback_type = data.get('feedback')
        comments = data.get('comments')
        
        feedback_msg = ""
        comment_msg = ""
        
        if feedback_type:
            feedback_msg = assistant.record_feedback(user_id, user_query, feedback_type)
        if comments:
            comment_msg = assistant.record_comment(user_id, user_query, comments)
        
        return jsonify({
            "feedback_message": feedback_msg,
            "comment_message": comment_msg
        }), 200
    
    @app.route('/finish', methods=['POST'])
    def finish():
        """Finish conversation endpoint - saves session to blob storage"""
        data = request.json
        user_id = data.get('user_id')
        
        if user_id and assistant.session_manager and assistant.use_blob_sessions:
            try:
                # Save final session data to blob storage
                conversations = assistant.user_conversation_histories.get(user_id, [])
                feedback_data = {
                    "user_id": user_id,
                    "feedback_entries": assistant.feedback_and_comments.get(user_id, [])
                }
                
                # Save both conversations and feedback
                assistant.session_manager.save_user_conversations(user_id, conversations)
                assistant.session_manager.save_user_feedback(user_id, feedback_data)
                
                return jsonify({
                    "message": "Conversation session saved successfully to blob storage.",
                    "saved_conversations": len(conversations),
                    "saved_feedback": len(feedback_data["feedback_entries"])
                }), 200
            except Exception as e:
                return jsonify({
                    "message": f"Error saving session: {str(e)}",
                    "fallback": "Session data retained in memory"
                }), 500
        else:
            return jsonify({
                "message": "Session completed (blob storage not available)"
            }), 200
    
    @app.route('/get_conversation', methods=['GET'])
    def get_conversation():
        """Get conversation data endpoint - matches your legacy API"""
        return jsonify({"result": assistant.get_conversation_data()})
    
    print("🚀 Starting Flask API server...")
    print("📡 API Endpoints:")
    print("   POST /query - Process user queries")
    print("   POST /feedback - Record user feedback")
    print("   POST /finish - End conversation session")
    print("   GET /get_conversation - Get all conversation data")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()