"""
Background task processing for RFP Automation System
Handles async tasks like report generation, email notifications, and data processing
"""
import asyncio
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import uuid
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    """Background task representation"""
    id: str
    name: str
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    progress: float = 0.0


class TaskManager:
    """Manages background tasks"""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
    
    def create_task(self, name: str, func: Callable, *args, **kwargs) -> str:
        """Create a new background task"""
        task_id = str(uuid.uuid4())
        
        task = Task(
            id=task_id,
            name=name,
            status=TaskStatus.PENDING,
            created_at=datetime.utcnow()
        )
        
        self.tasks[task_id] = task
        
        # Schedule the task
        async_task = asyncio.create_task(
            self._run_task(task_id, func, *args, **kwargs)
        )
        self.running_tasks[task_id] = async_task
        
        logger.info(f"Created background task: {name} (ID: {task_id})")
        return task_id
    
    async def _run_task(self, task_id: str, func: Callable, *args, **kwargs):
        """Execute a background task"""
        task = self.tasks[task_id]
        
        try:
            # Update status to running
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow()
            
            logger.info(f"Starting task: {task.name} (ID: {task_id})")
            
            # Execute the function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Update status to completed
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.result = result
            task.progress = 100.0
            
            logger.info(f"Completed task: {task.name} (ID: {task_id})")
            
        except Exception as e:
            # Update status to failed
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.utcnow()
            task.error = str(e)
            
            logger.error(f"Task failed: {task.name} (ID: {task_id}) - {e}")
        
        finally:
            # Clean up running task reference
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> Dict[str, Task]:
        """Get all tasks"""
        return self.tasks.copy()
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        if task_id in self.running_tasks:
            task = self.tasks[task_id]
            if task.status == TaskStatus.RUNNING:
                self.running_tasks[task_id].cancel()
                task.status = TaskStatus.FAILED
                task.error = "Task cancelled"
                task.completed_at = datetime.utcnow()
                
                logger.info(f"Cancelled task: {task.name} (ID: {task_id})")
                return True
        
        return False
    
    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """Clean up old completed/failed tasks"""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        tasks_to_remove = []
        for task_id, task in self.tasks.items():
            if (
                task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]
                and task.completed_at
                and task.completed_at < cutoff_time
            ):
                tasks_to_remove.append(task_id)
        
        for task_id in tasks_to_remove:
            del self.tasks[task_id]
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
        
        logger.info(f"Cleaned up {len(tasks_to_remove)} old tasks")


# Global task manager instance
task_manager = TaskManager()


# Example background tasks
async def generate_rfp_report_task(rfp_id: str, session_id: str) -> Dict[str, Any]:
    """Generate RFP report in background"""
    logger.info(f"Generating report for RFP: {rfp_id}")
    
    # Simulate report generation with progress updates
    for i in range(10):
        await asyncio.sleep(1)  # Simulate work
        # Update progress (would need to add progress tracking to Task)
        logger.info(f"Report generation progress: {(i + 1) * 10}%")
    
    # Generate actual report (placeholder)
    report_path = f"data/reports/{session_id}_{rfp_id}.pdf"
    
    return {
        "rfp_id": rfp_id,
        "session_id": session_id,
        "report_path": report_path,
        "generated_at": datetime.utcnow().isoformat()
    }


async def send_notification_task(user_email: str, message: str) -> Dict[str, Any]:
    """Send email notification in background"""
    logger.info(f"Sending notification to: {user_email}")
    
    # Simulate email sending
    await asyncio.sleep(2)
    
    # In production, integrate with email service
    logger.info(f"Notification sent to: {user_email}")
    
    return {
        "email": user_email,
        "message": message,
        "sent_at": datetime.utcnow().isoformat()
    }


async def process_rfp_scan_task(keywords: list, days_ahead: int) -> Dict[str, Any]:
    """Scan for RFP opportunities in background"""
    logger.info(f"Scanning for RFPs with keywords: {keywords}")
    
    # Simulate RFP scanning
    await asyncio.sleep(5)
    
    # In production, integrate with RFP scanning service
    mock_opportunities = [
        {
            "id": "rfp_001",
            "title": "Data Center Cabling Project",
            "client": "Tech Corp",
            "deadline": "2024-02-15",
            "value": "$250K"
        }
    ]
    
    return {
        "keywords": keywords,
        "days_ahead": days_ahead,
        "opportunities_found": len(mock_opportunities),
        "opportunities": mock_opportunities,
        "scanned_at": datetime.utcnow().isoformat()
    }
