"""
Task-related data models for the orchestrator.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4


class TaskStatus(str, Enum):
    """Status of a task in the system."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(str, Enum):
    """Types of tasks that can be processed."""
    PLAN = "plan"
    RETRIEVE = "retrieve"
    ANALYZE = "analyze"
    COMPLIANCE_CHECK = "compliance_check"
    SYNTHESIZE = "synthesize"
    VERIFY = "verify"


@dataclass
class Task:
    """Represents a unit of work to be processed by an agent."""
    id: str = field(default_factory=lambda: str(uuid4()))
    type: TaskType = TaskType.PLAN
    payload: Dict[str, Any] = field(default_factory=dict)
    sender: str = "user"
    recipient: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 0
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)


@dataclass
class TaskResult:
    """Result of a task execution."""
    task_id: str
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    execution_time: float = 0.0
    completed_at: datetime = field(default_factory=datetime.utcnow)
    agent_name: Optional[str] = None
    logs: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if isinstance(self.completed_at, str):
            self.completed_at = datetime.fromisoformat(self.completed_at)


@dataclass
class TaskGraph:
    """Represents a graph of tasks with dependencies."""
    tasks: List[Task] = field(default_factory=list)
    edges: List[tuple[str, str]] = field(default_factory=list)  # (from_task_id, to_task_id)
    
    def add_task(self, task: Task) -> None:
        """Add a task to the graph."""
        self.tasks.append(task)
    
    def add_dependency(self, from_task_id: str, to_task_id: str) -> None:
        """Add a dependency between tasks."""
        self.edges.append((from_task_id, to_task_id))
    
    def get_ready_tasks(self, completed_task_ids: List[str]) -> List[Task]:
        """Get tasks that are ready to execute (all dependencies completed)."""
        ready_tasks = []
        
        for task in self.tasks:
            if task.status != TaskStatus.PENDING:
                continue
                
            # Check if all dependencies are completed
            dependencies_met = True
            for from_id, to_id in self.edges:
                if to_id == task.id and from_id not in completed_task_ids:
                    dependencies_met = False
                    break
            
            if dependencies_met:
                ready_tasks.append(task)
        
        return sorted(ready_tasks, key=lambda t: t.priority, reverse=True)
    
    def is_complete(self, completed_task_ids: List[str]) -> bool:
        """Check if all tasks in the graph are completed."""
        return all(task.id in completed_task_ids for task in self.tasks)


@dataclass
class TaskExecutionLog:
    """Log entry for task execution."""
    task_id: str
    agent_name: str
    action: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = field(default_factory=dict)
    level: str = "INFO"  # INFO, WARNING, ERROR
    
    def __post_init__(self):
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp) 