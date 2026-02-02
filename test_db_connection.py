#!/usr/bin/env python3
"""
Test script for database and memory integration
Run this to verify Drizzle ORM and memory manager are working
"""
import asyncio
import os
from datetime import datetime

# Set environment variables
os.environ["DATABASE_URL"] = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/rfp_automation")

async def test_database_connection():
    """Test Drizzle database connection"""
    print("🔍 Testing Database Connection...")
    
    try:
        from backend.core.db.client import drizzle_client
        
        # Test health check
        health = drizzle_client.health_check()
        print(f"✅ Database Health: {health['status']}")
        print(f"   Message: {health['message']}")
        
        if health['status'] == 'healthy':
            return True
        else:
            print("❌ Database connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

async def test_memory_manager():
    """Test memory manager functionality"""
    print("\n🧠 Testing Memory Manager...")
    
    try:
        from backend.core.memory_manager import memory_manager
        
        # Test session creation
        session_id = "test_session_" + str(int(datetime.utcnow().timestamp()))
        print(f"📝 Created test session: {session_id}")
        
        # Test adding messages
        await memory_manager.add_user_message(session_id, "Hello, this is a test message")
        print("✅ Added user message")
        
        await memory_manager.add_ai_message(
            session_id, 
            "Hello! I'm the AI assistant. How can I help with your RFP?",
            metadata={"agent": "test", "step": "greeting"}
        )
        print("✅ Added AI message with metadata")
        
        # Test retrieving messages
        messages = memory_manager.get_messages(session_id)
        print(f"✅ Retrieved {len(messages)} messages")
        
        # Test session stats
        stats = memory_manager.get_session_stats(session_id)
        print(f"📊 Session Stats: {stats}")
        
        # Test agent state persistence
        test_state = {
            "current_step": "TEST_STEP",
            "rfps_identified": [{"title": "Test RFP", "client": "Test Client"}],
            "session_id": session_id
        }
        
        saved = await memory_manager.save_agent_state(session_id, test_state)
        print(f"💾 Saved agent state: {saved}")
        
        # Test loading state
        loaded_state = await memory_manager.load_agent_state(session_id)
        if loaded_state:
            print(f"📥 Loaded agent state: {loaded_state.get('current_step')}")
        else:
            print("⚠️  Could not load agent state (database may not be available)")
        
        # Test agent interaction logging
        await memory_manager.log_agent_interaction(
            session_id=session_id,
            agent_name="test_agent",
            input_data={"message": "test"},
            output_data={"response": "test response"},
            reasoning="Test reasoning for logging"
        )
        print("📝 Logged agent interaction")
        
        # Clean up
        memory_manager.clear_memory(session_id)
        print("🧹 Cleared test session")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory manager error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_chat_api():
    """Test chat API endpoint"""
    print("\n💬 Testing Chat API...")
    
    try:
        import requests
        import json
        
        # Test health endpoint
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Backend health check passed")
        else:
            print(f"❌ Backend health failed: {response.status_code}")
            return False
        
        # Test chat endpoint
        chat_data = {
            "message": "Test message for database integration",
            "session_id": "api_test_session"
        }
        
        response = requests.post(
            "http://localhost:8000/api/chat",
            json=chat_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Chat API response received")
            print(f"   Response: {result.get('response', 'No response')[:100]}...")
            return True
        else:
            print(f"❌ Chat API failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("⚠️  Backend not running. Start it with: python -m uvicorn backend.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Chat API test error: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Database & Memory Integration Tests\n")
    
    # Test database connection
    db_ok = await test_database_connection()
    
    # Test memory manager
    memory_ok = await test_memory_manager()
    
    # Test chat API
    api_ok = await test_chat_api()
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST RESULTS:")
    print(f"   Database Connection: {'✅ PASS' if db_ok else '❌ FAIL'}")
    print(f"   Memory Manager:     {'✅ PASS' if memory_ok else '❌ FAIL'}")
    print(f"   Chat API:           {'✅ PASS' if api_ok else '❌ FAIL'}")
    
    if db_ok and memory_ok:
        print("\n🎉 All core functionality working!")
        print("💡 Your database and memory integration is ready.")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
    
    print("="*50)

if __name__ == "__main__":
    asyncio.run(main())
