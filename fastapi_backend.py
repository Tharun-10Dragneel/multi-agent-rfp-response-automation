
"""
FastAPI Backend for RFP Automation System
Provides REST APIs for:
- OEM Catalog Management
- Chat Interface
- RFP Workflow Management
- Dashboard Data
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import uuid
from datetime import datetime
import os
from pathlib import Path

from models import AnalyzeRFPRequest, ChatMessage, ChatResponse, OEMProduct, RFPScanRequest
from utils import save_catalog, save_test_pricing
from logging_config import setup_logging, get_logger
from middleware import RateLimitMiddleware, SecurityHeadersMiddleware, RequestLoggingMiddleware
from database import init_db, get_db
from auth import create_user_token, get_current_user, require_admin, User
from exceptions import handle_exception
from api_docs import setup_openapi
from tasks import task_manager, generate_rfp_report_task, send_notification_task, process_rfp_scan_task
from cache import cache, get_cached_catalog_products, cache_catalog_products
from monitoring import monitor, get_dashboard_metrics
from config import config, validate_config, get_config_summary

# Setup logging
setup_logging(
    level=os.getenv("LOG_LEVEL", "INFO"),
    log_file=os.getenv("LOG_FILE", "logs/app.log"),
    enable_console=True
)
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RFP Automation System",
    description="AI-powered B2B RFP Response Automation",
    version="1.0.0"
)

# Setup OpenAPI documentation
setup_openapi(app)

# Apply middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, calls=100, period=60)

# Add exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle all exceptions globally"""
    return handle_exception(exc)

# CORS middleware for React frontend
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# HELPERS
# ============================================================

def error_response(message: str, status_code: int = 400, details: Optional[Dict] = None):
    """Consistent error response format"""
    content = {"error": True, "message": message}
    if details:
        content["details"] = details
    raise HTTPException(status_code=status_code, detail=content)

# ============================================================
# IN-MEMORY STORAGE (Replace with database in production)
# ============================================================

# Storage
oem_catalog_db = []
chat_sessions = {}
test_pricing_db = {}
REPORTS_DIR = Path("data") / "reports"

# LangGraph manages sessions internally with MemorySaver

# ============================================================
# STARTUP EVENT
# ============================================================

@app.on_event("startup")
async def startup_event():
    """Load initial data on startup and validate environment"""
    global oem_catalog_db, test_pricing_db

    # Initialize database
    init_db()
    
    # Validate required environment variables
    cerebras_key = os.getenv('CEREBRAS_API_KEY')
    if not cerebras_key:
        logger.warning("CEREBRAS_API_KEY not set. Chat/agent features will not work.")
    else:
        logger.info("Cerebras API key configured")

    if os.path.exists('data/catalog.json'):
        with open('data/catalog.json', 'r') as f:
            oem_catalog_db = json.load(f)
            logger.info(f"Loaded {len(oem_catalog_db)} products from catalog")

    if os.path.exists('data/test_pricing.json'):
        with open('data/test_pricing.json', 'r') as f:
            test_pricing_db = json.load(f)
            logger.info(f"Loaded {len(test_pricing_db)} test types from pricing data")

    logger.info("RFP Automation System initialized (LangGraph)")

# ============================================================
# AUTHENTICATION MODELS
# ============================================================

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]

# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "RFP Automation System",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check with monitoring data"""
    # Run all health checks
    checks = await monitor.run_all_checks()
    
    # Get overall status
    overall_status = monitor.get_overall_status(checks)
    
    # Build response
    response = {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "checks": {
            name: {
                "status": check.status,
                "message": check.message,
                "duration_ms": check.duration_ms,
                "details": check.details
            }
            for name, check in checks.items()
        },
        "system": {
            "catalog_items": len(oem_catalog_db),
            "test_types": len(test_pricing_db),
            "active_tasks": len(task_manager.running_tasks),
            "cache_size": len(cache.cache)
        }
    }
    
    # Return appropriate HTTP status code
    status_code = 200 if overall_status == "healthy" else (503 if overall_status == "critical" else 200)
    
    return response

@app.get("/api/health")
async def api_health_check():
    return await health_check()


# ============================================================
# AUTHENTICATION ENDPOINTS
# ============================================================

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Authenticate user and return JWT token"""
    try:
        token = create_user_token(request.email, request.password)
        
        if not token:
            logger.warning(f"Failed login attempt for email: {request.email}")
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )
        
        # Get user info (in production, fetch from database)
        user_info = {
            "email": request.email,
            "role": "admin" if "admin" in request.email else "user"
        }
        
        logger.info(f"Successful login for email: {request.email}")
        
        return TokenResponse(
            access_token=token,
            expires_in=30 * 60,  # 30 minutes
            user=user_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/auth/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information"""
    return {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "role": current_user.role
    }


@app.post("/api/auth/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout user (token invalidation would be handled in production)"""
    logger.info(f"User logged out: {current_user.email}")
    return {"message": "Successfully logged out"}


# ============================================================
# TASK MANAGEMENT ENDPOINTS
# ============================================================

@app.post("/api/tasks/report/{rfp_id}/{session_id}")
async def generate_report_task(rfp_id: str, session_id: str, current_user: User = Depends(get_current_user)):
    """Generate RFP report in background"""
    task_id = task_manager.create_task(
        name=f"Generate RFP Report - {rfp_id}",
        func=generate_rfp_report_task,
        rfp_id=rfp_id,
        session_id=session_id
    )
    
    return {
        "task_id": task_id,
        "message": "Report generation started",
        "status": "pending"
    }


@app.post("/api/tasks/scan")
async def scan_rfps_task(request: RFPScanRequest, current_user: User = Depends(get_current_user)):
    """Scan for RFP opportunities in background"""
    task_id = task_manager.create_task(
        name="RFP Opportunity Scan",
        func=process_rfp_scan_task,
        keywords=request.keywords,
        days_ahead=request.days_ahead
    )
    
    return {
        "task_id": task_id,
        "message": "RFP scan started",
        "status": "pending"
    }


@app.get("/api/tasks/{task_id}")
async def get_task_status(task_id: str, current_user: User = Depends(get_current_user)):
    """Get task status and results"""
    task = task_manager.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "task_id": task.id,
        "name": task.name,
        "status": task.status.value,
        "created_at": task.created_at.isoformat(),
        "started_at": task.started_at.isoformat() if task.started_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        "progress": task.progress,
        "result": task.result,
        "error": task.error
    }


@app.get("/api/tasks")
async def get_all_tasks(current_user: User = Depends(get_current_user)):
    """Get all tasks"""
    tasks = task_manager.get_all_tasks()
    
    return {
        "tasks": [
            {
                "task_id": task.id,
                "name": task.name,
                "status": task.status.value,
                "created_at": task.created_at.isoformat(),
                "progress": task.progress
            }
            for task in tasks.values()
        ],
        "total": len(tasks)
    }


@app.delete("/api/tasks/{task_id}")
async def cancel_task(task_id: str, current_user: User = Depends(get_current_user)):
    """Cancel a running task"""
    success = task_manager.cancel_task(task_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Task not found or not running")
    
    return {"message": "Task cancelled successfully"}


@app.get("/api/reports/{session_id}/{rfp_id}")
async def get_report(session_id: str, rfp_id: str):
    """Download generated RFP report PDF."""
    safe_rfp_id = rfp_id.replace("/", "_")
    report_path = REPORTS_DIR / f"{session_id}_{safe_rfp_id}.pdf"
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(str(report_path), media_type="application/pdf", filename=report_path.name)

# ============================================================
# OEM CATALOG MANAGEMENT APIs
# ============================================================

@app.get("/api/catalog", response_model=List[OEMProduct])
async def get_catalog():
    """Get all OEM products from catalog"""
    # Try to get from cache first
    cached_products = get_cached_catalog_products()
    if cached_products:
        logger.debug("Returning cached catalog products")
        return cached_products
    
    # Load from database
    products = oem_catalog_db
    
    # Cache the result
    cache_catalog_products(products, ttl=3600)  # Cache for 1 hour
    
    return products

@app.post("/api/catalog", response_model=OEMProduct)
async def add_product(product: OEMProduct):
    """Add new product to catalog"""
    # Check if SKU already exists
    if any(p['sku'] == product.sku for p in oem_catalog_db):
        raise HTTPException(status_code=400, detail="SKU already exists")

    product_dict = product.dict()
    product_dict['created_at'] = datetime.now().isoformat()
    product_dict['updated_at'] = datetime.now().isoformat()

    oem_catalog_db.append(product_dict)
    
    # Invalidate cache
    cache.delete("catalog:products")
    logger.info(f"Invalidated catalog cache due to new product: {product.sku}")

    return product


# ============================================================
# CACHE MANAGEMENT ENDPOINTS
# ============================================================

@app.get("/api/cache/stats")
async def get_cache_stats(current_user: User = Depends(require_admin)):
    """Get cache statistics (admin only)"""
    return cache.get_stats()


@app.post("/api/cache/clear")
async def clear_cache(current_user: User = Depends(require_admin)):
    """Clear all cache entries (admin only)"""
    cache.clear()
    return {"message": "Cache cleared successfully"}


@app.post("/api/cache/cleanup")
async def cleanup_cache(current_user: User = Depends(require_admin)):
    """Clean up expired cache entries (admin only)"""
    expired_count = cache.cleanup_expired()
    return {"message": f"Cleaned up {expired_count} expired entries"}


# ============================================================
# MONITORING ENDPOINTS
# ============================================================

@app.get("/api/monitoring/metrics")
async def get_metrics(current_user: User = Depends(require_admin)):
    """Get system metrics (admin only)"""
    return get_dashboard_metrics()


@app.get("/api/monitoring/health")
async def get_detailed_health(current_user: User = Depends(require_admin)):
    """Get detailed health check results (admin only)"""
    checks = await monitor.run_all_checks()
    
    return {
        "overall_status": monitor.get_overall_status(checks),
        "last_check": monitor.last_check_time.isoformat(),
        "checks": {
            name: {
                "status": check.status,
                "message": check.message,
                "duration_ms": check.duration_ms,
                "timestamp": check.timestamp.isoformat(),
                "details": check.details
            }
            for name, check in checks.items()
        }
    }


# ============================================================
# CONFIGURATION ENDPOINTS
# ============================================================

@app.get("/api/config")
async def get_configuration(current_user: User = Depends(require_admin)):
    """Get application configuration (admin only)"""
    return config.to_dict()


@app.get("/api/config/summary")
async def get_config_summary_endpoint(current_user: User = Depends(require_admin)):
    """Get configuration summary (admin only)"""
    return get_config_summary()


@app.post("/api/config/validate")
async def validate_configuration(current_user: User = Depends(require_admin)):
    """Validate configuration (admin only)"""
    is_valid = validate_config()
    
    return {
        "valid": is_valid,
        "message": "Configuration is valid" if is_valid else "Configuration validation failed"
    }

    save_catalog(oem_catalog_db)

    return product_dict

@app.put("/api/catalog/{sku}", response_model=OEMProduct)
async def update_product(sku: str, product: OEMProduct):
    """Update existing product"""
    for i, p in enumerate(oem_catalog_db):
        if p['sku'] == sku:
            product_dict = product.dict()
            product_dict['updated_at'] = datetime.now().isoformat()
            product_dict['created_at'] = p.get('created_at', datetime.now().isoformat())
            oem_catalog_db[i] = product_dict

            save_catalog(oem_catalog_db)
            return product_dict

    raise HTTPException(status_code=404, detail="Product not found")

@app.delete("/api/catalog/{sku}")
async def delete_product(sku: str):
    """Delete product from catalog"""
    for i, p in enumerate(oem_catalog_db):
        if p['sku'] == sku:
            oem_catalog_db.pop(i)

            save_catalog(oem_catalog_db)
            return {"message": "Product deleted successfully"}

    raise HTTPException(status_code=404, detail="Product not found")

@app.post("/api/catalog/upload")
async def upload_catalog(file: UploadFile = File(...)):
    """Upload catalog from Excel/CSV file"""
    try:
        contents = await file.read()

        # Parse based on file type
        if file.filename.endswith('.json'):
            new_products = json.loads(contents)
        elif file.filename.endswith('.csv'):
            # Parse CSV (implement CSV parsing)
            raise HTTPException(status_code=400, detail="CSV parsing not implemented yet")
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        # Add to catalog
        for product in new_products:
            if not any(p['sku'] == product['sku'] for p in oem_catalog_db):
                product['created_at'] = datetime.now().isoformat()
                product['updated_at'] = datetime.now().isoformat()
                oem_catalog_db.append(product)

        save_catalog(oem_catalog_db)

        return {
            "message": f"Successfully uploaded {len(new_products)} products",
            "total_products": len(oem_catalog_db)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================
# CHAT APIs
# ============================================================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    from agents.graph import rfp_workflow
    from agents.state import create_initial_state, get_last_ai_message_content
    from langchain_core.messages import HumanMessage

    session_id = message.session_id

    try:
        prior_state = chat_sessions.get(session_id)
        if prior_state:
            state = dict(prior_state)
            state["messages"] = list(prior_state.get("messages", [])) + [HumanMessage(content=message.message)]
        else:
            state = create_initial_state(session_id, message.message)

        result = await rfp_workflow.ainvoke(
            state,
            config={"configurable": {"thread_id": session_id}}
        )

        response_text = get_last_ai_message_content(result)
        chat_sessions[session_id] = result

        return ChatResponse(
            response=response_text,
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            workflow_state={
                "current_step": result.get("current_step", "COMPLETE"),
                "rfps_identified": result.get("rfps_identified", []),
                "report_url": result.get("report_url")
            }
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return ChatResponse(
            response=f"Error: {str(e)}",
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            workflow_state={"status": "ERROR", "error": str(e)}
        )

@app.get("/api/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get chat history for a session (LangGraph manages this internally)"""
    return {"message": "Chat history is managed by LangGraph checkpointer"}

@app.get("/api/chat/state/{session_id}")
async def get_workflow_state(session_id: str):
    """Get current workflow state (managed by LangGraph)"""
    return {"message": "Workflow state managed by LangGraph checkpointer", "session_id": session_id}

@app.delete("/api/chat/{session_id}")
async def clear_session(session_id: str):
    """Clear chat session"""
    return {"message": "Session cleared (LangGraph handles cleanup)", "session_id": session_id}

# ============================================================
# RFP WORKFLOW APIs
# ============================================================

@app.post("/api/rfp/scan")
async def scan_rfps(request: RFPScanRequest):
    """Scan for RFPs (use /api/chat for LangGraph workflow)"""
    return {
        "message": "Please use /api/chat endpoint for RFP workflow with LangGraph agents",
        "total_found": 0,
        "rfps": []
    }

@app.post("/api/rfp/analyze")
async def analyze_rfp(request: AnalyzeRFPRequest):
    """Analyze a specific RFP"""
    # This would typically fetch from database
    # For now, return mock analysis
    return {
        "rfp_id": request.rfp_id,
        "status": "analyzed",
        "message": "Use chat interface for full workflow"
    }

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    return {
        "total_products": len(oem_catalog_db),
        "test_types": len(test_pricing_db),
        "system_status": "operational",
        "last_updated": datetime.now().isoformat(),
        "llm_configured": bool(os.getenv('CEREBRAS_API_KEY'))
    }