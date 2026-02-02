"""
Authentication and authorization for RFP Automation System
JWT-based authentication with role-based access control
"""
import os
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

logger = logging.getLogger(__name__)

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))

# Security scheme
security = HTTPBearer()


class User:
    """User model for authentication"""
    def __init__(self, user_id: str, email: str, role: str = "user"):
        self.user_id = user_id
        self.email = email
        self.role = role


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current user from JWT token"""
    token = credentials.credentials
    payload = verify_token(token)
    
    user_id = payload.get("sub")
    email = payload.get("email")
    role = payload.get("role", "user")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return User(user_id=user_id, email=email, role=role)


def require_role(required_role: str):
    """Decorator to require specific role"""
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker


def require_admin():
    """Require admin role"""
    return require_role("admin")


# Mock user database (replace with real database in production)
MOCK_USERS = {
    "admin@example.com": {
        "user_id": "admin_001",
        "email": "admin@example.com",
        "role": "admin",
        "password": "admin123"  # In production, use hashed passwords
    },
    "user@example.com": {
        "user_id": "user_001",
        "email": "user@example.com",
        "role": "user",
        "password": "user123"  # In production, use hashed passwords
    }
}


def authenticate_user(email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password"""
    user_data = MOCK_USERS.get(email)
    
    if user_data and user_data["password"] == password:
        return User(
            user_id=user_data["user_id"],
            email=user_data["email"],
            role=user_data["role"]
        )
    
    return None


def create_user_token(email: str, password: str) -> Optional[str]:
    """Create token for authenticated user"""
    user = authenticate_user(email, password)
    
    if user:
        token_data = {
            "sub": user.user_id,
            "email": user.email,
            "role": user.role
        }
        return create_access_token(token_data)
    
    return None
