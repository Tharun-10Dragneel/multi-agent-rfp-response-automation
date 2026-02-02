#!/usr/bin/env python3
"""
Simple test for database integration
Tests the fixed database client without complex imports
"""
import os
import asyncio
from datetime import datetime

# Set environment
os.environ["DATABASE_URL"] = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/rfp_automation")

async def test_database():
    """Test database connection and basic operations"""
    print("🔍 Testing Database Integration...")
    
    try:
        # Import the official Drizzle client
        from backend.core.db.client import drizzle_client
        
        # Test health check
        health = drizzle_client.health_check()
        print(f"✅ Database Health: {health['status']}")
        print(f"   Message: {health['message']}")
        
        if health['status'] == 'healthy':
            # Test saving a session
            test_session_id = f"test_{int(datetime.utcnow().timestamp())}"
            
            success = await drizzle_client.save_chat_session(test_session_id, {
                "current_step": "TEST",
                "session_id": test_session_id
            })
            
            if success:
                print("✅ Successfully saved chat session")
                
                # Test loading the session
                loaded = await drizzle_client.load_chat_session(test_session_id)
                if loaded:
                    print("✅ Successfully loaded chat session")
                    print(f"   Current step: {loaded.get('current_step')}")
                else:
                    print("❌ Failed to load chat session")
                
                # Test saving a message
                msg_success = await drizzle_client.save_chat_message(
                    test_session_id, 
                    "user", 
                    "Test message for database integration"
                )
                
                if msg_success:
                    print("✅ Successfully saved chat message")
                    
                    # Test getting messages
                    messages = await drizzle_client.get_chat_messages(test_session_id)
                    print(f"✅ Retrieved {len(messages)} messages")
                    
                else:
                    print("❌ Failed to save chat message")
            else:
                print("❌ Failed to save chat session")
        else:
            print("❌ Database not healthy")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure SQLAlchemy is installed: pip install sqlalchemy==2.0.23 psycopg2-binary==2.9.9")
    except Exception as e:
        print(f"❌ Database test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_database())
