"""
Supabase database client for RFP Automation System
Direct Supabase Python client for database operations
"""
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logging.warning("Supabase client not available")

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Supabase client for database operations"""
    
    def __init__(self):
        self.client = None
        self.available = False
        
        if not SUPABASE_AVAILABLE:
            logger.warning("Supabase client not installed")
            return
        
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not supabase_url or not supabase_key:
            logger.warning("Supabase URL or key not configured")
            return
        
        try:
            self.client = create_client(supabase_url, supabase_key)
            self.available = True
            logger.info("Supabase client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase: {e}")
    
    def is_available(self) -> bool:
        """Check if Supabase client is available"""
        return self.available and self.client is not None
    
    async def save_chat_session(self, session_id: str, state: Dict[str, Any]) -> bool:
        """Save chat session state"""
        if not self.is_available():
            return False
        
        try:
            session_data = {
                "session_id": session_id,
                "current_step": state.get("current_step", "IDLE"),
                "next_node": state.get("next_node", "main_agent"),
                "rfps_identified": state.get("rfps_identified", []),
                "selected_rfp": state.get("selected_rfp"),
                "user_selected_rfp_id": state.get("user_selected_rfp_id"),
                "technical_analysis": state.get("technical_analysis"),
                "pricing_analysis": state.get("pricing_analysis"),
                "final_response": state.get("final_response"),
                "report_path": state.get("report_path"),
                "product_summary": state.get("product_summary"),
                "test_summary": state.get("test_summary"),
                "waiting_for_user": state.get("waiting_for_user", False),
                "user_prompt": state.get("user_prompt"),
                "error": state.get("error"),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Upsert session
            result = self.client.table("chat_sessions").upsert(session_data).execute()
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Error saving chat session: {e}")
            return False
    
    async def load_chat_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load chat session state"""
        if not self.is_available():
            return None
        
        try:
            result = self.client.table("chat_sessions").select("*").eq("session_id", session_id).execute()
            
            if result.data:
                session = result.data[0]
                return {
                    "messages": [],  # Messages loaded separately
                    "current_step": session.get("current_step", "IDLE"),
                    "next_node": session.get("next_node", "main_agent"),
                    "rfps_identified": session.get("rfps_identified", []),
                    "selected_rfp": session.get("selected_rfp"),
                    "user_selected_rfp_id": session.get("user_selected_rfp_id"),
                    "technical_analysis": session.get("technical_analysis"),
                    "pricing_analysis": session.get("pricing_analysis"),
                    "final_response": session.get("final_response"),
                    "report_path": session.get("report_path"),
                    "product_summary": session.get("product_summary"),
                    "test_summary": session.get("test_summary"),
                    "waiting_for_user": session.get("waiting_for_user", False),
                    "user_prompt": session.get("user_prompt"),
                    "agent_reasoning": [],
                    "tool_calls_made": [],
                    "session_id": session_id,
                    "error": session.get("error")
                }
                
        except Exception as e:
            logger.error(f"Error loading chat session: {e}")
        
        return None
    
    async def save_chat_message(self, session_id: str, message_type: str, 
                              content: str, metadata: Dict[str, Any] = None) -> bool:
        """Save chat message"""
        if not self.is_available():
            return False
        
        try:
            message_data = {
                "session_id": session_id,
                "message_type": message_type,
                "content": content,
                "metadata": metadata or {},
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = self.client.table("chat_messages").insert(message_data).execute()
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Error saving chat message: {e}")
            return False
    
    async def get_chat_messages(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get chat messages"""
        if not self.is_available():
            return []
        
        try:
            result = self.client.table("chat_messages").select("*").eq("session_id", session_id).order("created_at", desc=False).limit(limit).execute()
            
            return [
                {
                    "id": msg["id"],
                    "session_id": msg["session_id"],
                    "message_type": msg["message_type"],
                    "content": msg["content"],
                    "metadata": msg.get("metadata", {}),
                    "created_at": msg["created_at"]
                }
                for msg in result.data
            ]
            
        except Exception as e:
            logger.error(f"Error getting chat messages: {e}")
            return []
    
    async def save_agent_interaction(self, session_id: str, agent_name: str, 
                                   interaction_data: Dict[str, Any]) -> bool:
        """Save agent interaction"""
        if not self.is_available():
            return False
        
        try:
            interaction = {
                "session_id": session_id,
                "agent_name": agent_name,
                "interaction_type": interaction_data.get("type", "response"),
                "input_data": interaction_data.get("input", {}),
                "output_data": interaction_data.get("output", {}),
                "reasoning": interaction_data.get("reasoning", ""),
                "tool_calls": interaction_data.get("tool_calls", []),
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = self.client.table("agent_interactions").insert(interaction).execute()
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Error saving agent interaction: {e}")
            return False
    
    async def create_rfp_record(self, rfp_data: Dict[str, Any]) -> Optional[str]:
        """Create RFP record"""
        if not self.is_available():
            return None
        
        try:
            rfp_record = {
                "title": rfp_data.get("title"),
                "client_name": rfp_data.get("client_name"),
                "description": rfp_data.get("description"),
                "submission_date": rfp_data.get("submission_date"),
                "status": "identified",
                "priority_score": rfp_data.get("priority_score", 0),
                "budget_range": rfp_data.get("budget_range"),
                "technical_requirements": rfp_data.get("technical_requirements", []),
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = self.client.table("rfps").insert(rfp_record).execute()
            return result.data[0].get("id")
                
        except Exception as e:
            logger.error(f"Error creating RFP record: {e}")
        
        return None
    
    def health_check(self) -> Dict[str, Any]:
        """Check Supabase connection"""
        if not self.is_available():
            return {
                "status": "disabled",
                "message": "Supabase client not available"
            }
        
        try:
            # Simple query to test connection
            result = self.client.table("chat_sessions").select("count").execute()
            
            return {
                "status": "healthy",
                "message": "Supabase connection successful"
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Supabase connection failed: {str(e)}"
            }


# Global Supabase client instance
supabase_client = SupabaseClient()
    
    def health_check(self) -> Dict[str, Any]:
        """Check Drizzle database connection"""
        if not self.is_available():
            return {
                "status": "disabled",
                "message": "Drizzle ORM not available"
            }
        
        try:
            with self.session_factory() as session:
                # Simple query to test connection
                stmt = select(chat_sessions_table).limit(1)
                session.execute(stmt)
                
                return {
                    "status": "healthy",
                    "message": "Drizzle ORM connection successful"
                }
                
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Drizzle connection failed: {str(e)}"
            }


# Global Drizzle client instance
drizzle_client = DrizzleClient()
