"""
Database configuration and models for RFP Automation System
Supports both SQLite and PostgreSQL with SQLAlchemy ORM
"""
import os
from typing import Optional
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./data/rfp_automation.db"
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("DATABASE_ECHO", "false").lower() == "true"
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class RFPOpportunity(Base):
    """RFP opportunities table"""
    __tablename__ = "rfp_opportunities"
    
    id = Column(String, primary_key=True)
    client_name = Column(String, nullable=False)
    project_title = Column(String, nullable=False)
    description = Column(Text)
    submission_deadline = Column(DateTime)
    budget_range = Column(String)
    priority_score = Column(Float)
    status = Column(String, default="new")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    raw_data = Column(Text)  # JSON string of original RFP data


class ChatSession(Base):
    """Chat sessions table"""
    __tablename__ = "chat_sessions"
    
    id = Column(String, primary_key=True)
    user_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    metadata = Column(Text)  # JSON string for session metadata


class ChatMessage(Base):
    """Chat messages table"""
    __tablename__ = "chat_messages"
    
    id = Column(String, primary_key=True)
    session_id = Column(String, nullable=False)
    message_type = Column(String)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata = Column(Text)  # JSON string for message metadata


class SystemLog(Base):
    """System logs table"""
    __tablename__ = "system_logs"
    
    id = Column(String, primary_key=True)
    level = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    module = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    extra_data = Column(Text)  # JSON string for additional log data


def init_db():
    """Initialize database tables"""
    try:
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_db_session():
    """Create a new database session"""
    return SessionLocal()
