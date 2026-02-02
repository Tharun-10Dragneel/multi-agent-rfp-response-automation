"""
OpenAPI documentation configuration for RFP Automation System
Provides comprehensive API documentation with examples and schemas
"""
from typing import Dict, Any, List
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def custom_openapi(app: FastAPI) -> Dict[str, Any]:
    """Generate custom OpenAPI schema with enhanced documentation"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="RFP Automation System API",
        version="1.0.0",
        description="""
        ## AI-Powered Multi-Agent System for RFP Response Automation
        
        This API provides endpoints for:
        - **Authentication**: JWT-based user authentication
        - **RFP Management**: Create, analyze, and track RFP opportunities
        - **Chat Interface**: Interact with AI agents for RFP analysis
        - **Catalog Management**: Manage OEM product catalog
        - **Reports**: Generate and download RFP response reports
        
        ### Authentication
        Most endpoints require JWT authentication. Include the token in the Authorization header:
        `Authorization: Bearer <your-jwt-token>`
        
        ### Rate Limiting
        API is rate-limited to 100 requests per minute per IP address.
        
        ### Error Responses
        All errors return a consistent format:
        ```json
        {
            "error": true,
            "message": "Error description",
            "details": {}
        }
        ```
        """,
        routes=app.routes,
        servers=[
            {"url": "http://localhost:8000", "description": "Development server"},
            {"url": "https://api.rfp-automation.com", "description": "Production server"},
        ],
        tags=[
            {"name": "Authentication", "description": "User authentication and authorization"},
            {"name": "Health", "description": "System health checks"},
            {"name": "RFP", "description": "RFP opportunity management"},
            {"name": "Chat", "description": "AI chat interface"},
            {"name": "Catalog", "description": "OEM product catalog"},
            {"name": "Reports", "description": "Report generation and download"},
        ]
    )
    
    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT authentication token"
        }
    }
    
    # Add global security requirement
    openapi_schema["security"] = [{"BearerAuth": []}]
    
    # Add example schemas
    openapi_schema["components"]["schemas"].update({
        "Error": {
            "type": "object",
            "properties": {
                "error": {"type": "boolean", "example": True},
                "message": {"type": "string", "example": "Error description"},
                "details": {"type": "object", "example": {}}
            },
            "required": ["error", "message"]
        },
        "User": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "example": "user_001"},
                "email": {"type": "string", "example": "user@example.com"},
                "role": {"type": "string", "example": "user", "enum": ["user", "admin"]}
            },
            "required": ["user_id", "email", "role"]
        },
        "RFPOpportunity": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "example": "rfp_001"},
                "client_name": {"type": "string", "example": "Acme Corporation"},
                "project_title": {"type": "string", "example": "Data Center Cabling Infrastructure"},
                "description": {"type": "string", "example": "Complete cabling solution for new data center"},
                "submission_deadline": {"type": "string", "format": "date-time"},
                "budget_range": {"type": "string", "example": "$100K - $500K"},
                "priority_score": {"type": "number", "example": 8.5},
                "status": {"type": "string", "example": "new", "enum": ["new", "analyzing", "qualified", "rejected", "won", "lost"]}
            },
            "required": ["id", "client_name", "project_title", "status"]
        }
    })
    
    # Add response examples
    openapi_schema["components"]["examples"] = {
        "LoginSuccess": {
            "summary": "Successful login response",
            "value": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
                "user": {
                    "email": "user@example.com",
                    "role": "user"
                }
            }
        },
        "ChatResponse": {
            "summary": "AI agent response",
            "value": {
                "response": "I've analyzed the RFP and identified 3 key requirements...",
                "session_id": "session_001",
                "timestamp": "2024-01-15T10:30:00Z",
                "workflow_state": {
                    "current_node": "sales_agent",
                    "completed_nodes": ["main_agent"]
                }
            }
        },
        "ErrorResponse": {
            "summary": "Error response format",
            "value": {
                "error": True,
                "message": "RFP not found",
                "details": {
                    "resource": "RFP",
                    "identifier": "rfp_001"
                }
            }
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


def setup_openapi(app: FastAPI):
    """Setup custom OpenAPI documentation"""
    app.openapi = lambda: custom_openapi(app)
