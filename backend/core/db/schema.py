"""
Drizzle ORM schema for RFP Automation System
Type-safe database schema definitions for Supabase PostgreSQL
"""
from datetime import datetime
from typing import Optional
import uuid

from drizzle_orm import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    JSON,
    UUID,
    ForeignKey,
    Table,
    Enum as DrizzleEnum,
)
from drizzle_orm import relationship


# Enums
class UserRole:
    SALES = "sales"
    MANAGER = "manager"
    ADMIN = "admin"


class MessageType:
    USER = "user"
    ASSISTANT = "assistant"


class InteractionType:
    RESPONSE = "response"
    TOOL_CALL = "tool_call"
    ERROR = "error"


# Tables
users_table = Table(
    "users_table",
    Column("id", UUID, primary_key=True, default=uuid.uuid4),
    Column("name", String(255), nullable=False),
    Column("email", String(255), nullable=False, unique=True),
    Column("role", DrizzleEnum("user_role", [UserRole.SALES, UserRole.MANAGER, UserRole.ADMIN]), nullable=False, default=UserRole.SALES),
    Column("manager_id", UUID, ForeignKey("users_table.id")),
    Column("created_at", DateTime, default=datetime.utcnow),
)


rfps_table = Table(
    "rfps_table",
    Column("id", UUID, primary_key=True, default=uuid.uuid4),
    Column("title", String(500), nullable=False),
    Column("client_name", String(255), nullable=False),
    Column("description", Text),
    Column("submission_date", DateTime),
    Column("submitted_by", UUID, ForeignKey("users_table.id"), nullable=False),
    Column("status", String(50), default="identified"),
    Column("priority_score", Integer, default=0),
    Column("budget_range", String(100)),
    Column("technical_requirements", JSON, default=list),
    Column("sales_analysis", JSON),
    Column("technical_analysis", JSON),
    Column("pricing_analysis", JSON),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("updated_at", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
)


rfp_files_table = Table(
    "rfp_files_table",
    Column("id", UUID, primary_key=True, default=uuid.uuid4),
    Column("rfp_id", UUID, ForeignKey("rfps_table.id"), nullable=False),
    Column("file_name", String(255), nullable=False),
    Column("file_path", String(500), nullable=False),
    Column("file_size", Integer),
    Column("uploaded_at", DateTime, default=datetime.utcnow),
)


chat_sessions_table = Table(
    "chat_sessions",
    Column("id", UUID, primary_key=True, default=uuid.uuid4),
    Column("session_id", String(255), unique=True, nullable=False),
    Column("current_step", String(50), default="IDLE"),
    Column("next_node", String(50), default="main_agent"),
    Column("rfps_identified", JSON, default=list),
    Column("selected_rfp", JSON),
    Column("user_selected_rfp_id", String(255)),
    Column("technical_analysis", JSON),
    Column("pricing_analysis", JSON),
    Column("final_response", Text),
    Column("report_path", String(500)),
    Column("product_summary", Text),
    Column("test_summary", Text),
    Column("waiting_for_user", Boolean, default=False),
    Column("user_prompt", Text),
    Column("error", Text),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("updated_at", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
)


chat_messages_table = Table(
    "chat_messages",
    Column("id", UUID, primary_key=True, default=uuid.uuid4),
    Column("session_id", String(255), nullable=False),
    Column("message_type", DrizzleEnum("message_type", [MessageType.USER, MessageType.ASSISTANT]), nullable=False),
    Column("content", Text, nullable=False),
    Column("metadata", JSON, default=dict),
    Column("created_at", DateTime, default=datetime.utcnow),
)


agent_interactions_table = Table(
    "agent_interactions",
    Column("id", UUID, primary_key=True, default=uuid.uuid4),
    Column("session_id", String(255), nullable=False),
    Column("agent_name", String(100), nullable=False),
    Column("interaction_type", DrizzleEnum("interaction_type", [InteractionType.RESPONSE, InteractionType.TOOL_CALL, InteractionType.ERROR]), default=InteractionType.RESPONSE),
    Column("input_data", JSON, default=dict),
    Column("output_data", JSON, default=dict),
    Column("reasoning", Text),
    Column("tool_calls", JSON, default=list),
    Column("created_at", DateTime, default=datetime.utcnow),
)


# Type definitions for type safety
class User:
    id: uuid.UUID
    name: str
    email: str
    role: UserRole
    manager_id: Optional[uuid.UUID]
    created_at: datetime


class RFP:
    id: uuid.UUID
    title: str
    client_name: str
    description: Optional[str]
    submission_date: Optional[datetime]
    submitted_by: uuid.UUID
    status: str
    priority_score: int
    budget_range: Optional[str]
    technical_requirements: list
    sales_analysis: Optional[dict]
    technical_analysis: Optional[dict]
    pricing_analysis: Optional[dict]
    created_at: datetime
    updated_at: datetime


class ChatSession:
    id: uuid.UUID
    session_id: str
    current_step: str
    next_node: str
    rfps_identified: list
    selected_rfp: Optional[dict]
    user_selected_rfp_id: Optional[str]
    technical_analysis: Optional[dict]
    pricing_analysis: Optional[dict]
    final_response: Optional[str]
    report_path: Optional[str]
    product_summary: Optional[str]
    test_summary: Optional[str]
    waiting_for_user: bool
    user_prompt: Optional[str]
    error: Optional[str]
    created_at: datetime
    updated_at: datetime


class ChatMessage:
    id: uuid.UUID
    session_id: str
    message_type: MessageType
    content: str
    metadata: dict
    created_at: datetime


class AgentInteraction:
    id: uuid.UUID
    session_id: str
    agent_name: str
    interaction_type: InteractionType
    input_data: dict
    output_data: dict
    reasoning: Optional[str]
    tool_calls: list
    created_at: datetime


# Table registry for easy access
TABLES = {
    "users": users_table,
    "rfps": rfps_table,
    "rfp_files": rfp_files_table,
    "chat_sessions": chat_sessions_table,
    "chat_messages": chat_messages_table,
    "agent_interactions": agent_interactions_table,
}
