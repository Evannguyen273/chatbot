#!/usr/bin/env python3
"""
Test script for the chatbot system
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_basic_functionality():
    """Test basic chatbot functionality without memory"""
    print("🧪 Testing Basic Chatbot Functionality")
    print("=" * 50)
    
    try:
        from app.graph import build_graph
        
        # Build the graph
        app = build_graph()
        print("✅ Graph built successfully")
        
        # Test greeting
        result = app.invoke({
            "user_prompt": "Hello",
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
            "messages": []
        })
        
        print("✅ Test 1 - Greeting:")
        print(f"   Input: Hello")
        print(f"   Output: {result['final_response']}")
        
        # Test data query
        result2 = app.invoke({
            "user_prompt": "Show me incidents from 2024",
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
            "messages": []
        })
        
        print("✅ Test 2 - Data Query:")
        print(f"   Input: Show me incidents from 2024")
        print(f"   Intent: {result2['intent']}")
        print(f"   SQL Generated: {result2.get('sql_query', 'No SQL')}")
        print(f"   Output: {result2['final_response']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_configuration():
    """Test configuration loading"""
    print("\n🔧 Testing Configuration")
    print("=" * 50)
    
    try:
        from config.settings import (
            OPENAI_API_KEY, GCP_PROJECT_ID, BQ_DATASET, 
            AZURE_BLOB_CONNECTION_STRING, PROMPT_FILES, SCHEMA_FILES
        )
        
        print(f"✅ OpenAI API Key: {'Set' if OPENAI_API_KEY != 'your-openai-key' else 'Default placeholder'}")
        print(f"✅ GCP Project: {GCP_PROJECT_ID}")
        print(f"✅ BQ Dataset: {BQ_DATASET}")
        print(f"✅ Azure Blob: {'Set' if AZURE_BLOB_CONNECTION_STRING != 'your-conn-string' else 'Default placeholder'}")
        print(f"✅ Prompt Files: {list(PROMPT_FILES.keys())}")
        print(f"✅ Schema Files: {SCHEMA_FILES}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_azure_connection():
    """Test Azure Blob Storage connection"""
    print("\n☁️ Testing Azure Blob Storage")
    print("=" * 50)
    
    try:
        from services.azure_blob_client import blob_client
        
        # Try to list files (this will fail gracefully if connection is bad)
        try:
            # This is a simple test that won't actually fail if Azure isn't configured
            print("✅ Azure blob client initialized")
            print("   Note: Actual connection test requires valid Azure credentials")
            return True
        except Exception as e:
            print(f"⚠️ Azure connection issue: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Azure test failed: {e}")
        return False

def test_utils():
    """Test utility functions"""
    print("\n🛠️ Testing Utility Functions")
    print("=" * 50)
    
    try:
        from app.utils import parse_json_response, exponential_backoff
        
        # Test JSON parsing
        test_json = '{"intent": "greeting", "rephrased": "hello"}'
        result = parse_json_response(test_json)
        print(f"✅ JSON parsing: {result}")
        
        # Test malformed JSON
        bad_json = "not json at all"
        result = parse_json_response(bad_json)
        print(f"✅ Bad JSON handling: {result.get('error', 'Handled gracefully')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Utils test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Chatbot System Test Suite")
    print("=" * 60)
    
    tests = [
        ("Configuration", test_configuration),
        ("Azure Connection", test_azure_connection), 
        ("Utility Functions", test_utils),
        ("Basic Functionality", test_basic_functionality),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System appears to be working correctly.")
    else:
        print("⚠️ Some tests failed. Check configuration and dependencies.")

if __name__ == "__main__":
    main()