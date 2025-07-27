"""
Logging utilities for the orchestrator platform.
"""

import logging
import sys
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
import asyncio
from contextlib import asynccontextmanager

from ..config.settings import settings


class OrchestratorLogger:
    """Centralized logging for the orchestrator platform."""
    
    def __init__(self, name: str = "orchestrator"):
        """Initialize the logger."""
        self.name = name
        self.logger = logging.getLogger(name)
        self.setup_logging()
        
        # In-memory log storage for audit
        self.audit_logs: List[Dict[str, Any]] = []
        self.max_audit_logs = 10000
    
    def setup_logging(self) -> None:
        """Setup logging configuration."""
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Set log level
        log_level = getattr(logging, settings.logging.level.upper(), logging.INFO)
        self.logger.setLevel(log_level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler (if configured)
        if settings.logging.file:
            file_path = Path(settings.logging.file)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(file_path)
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def log_task_start(self, task_id: str, agent_name: str, task_type: str) -> None:
        """Log task start."""
        message = f"Task {task_id} started by {agent_name} ({task_type})"
        self.logger.info(message)
        self._add_audit_log("task_start", {
            "task_id": task_id,
            "agent_name": agent_name,
            "task_type": task_type,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def log_task_complete(self, task_id: str, agent_name: str, success: bool, duration: float) -> None:
        """Log task completion."""
        status = "completed" if success else "failed"
        message = f"Task {task_id} {status} by {agent_name} in {duration:.2f}s"
        level = logging.INFO if success else logging.ERROR
        self.logger.log(level, message)
        
        self._add_audit_log("task_complete", {
            "task_id": task_id,
            "agent_name": agent_name,
            "success": success,
            "duration": duration,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def log_agent_message(self, from_agent: str, to_agent: str, message_type: str, data: Dict[str, Any]) -> None:
        """Log agent communication."""
        message = f"Message from {from_agent} to {to_agent}: {message_type}"
        self.logger.debug(message)
        
        # Sanitize data for logging (remove sensitive information)
        sanitized_data = self._sanitize_data(data)
        
        self._add_audit_log("agent_message", {
            "from_agent": from_agent,
            "to_agent": to_agent,
            "message_type": message_type,
            "data": sanitized_data,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def log_anomaly_detected(self, pattern_type: str, confidence: float, affected_transactions: List[str]) -> None:
        """Log detected anomaly."""
        message = f"Anomaly detected: {pattern_type} (confidence: {confidence:.2f})"
        self.logger.warning(message)
        
        self._add_audit_log("anomaly_detected", {
            "pattern_type": pattern_type,
            "confidence": confidence,
            "affected_transactions_count": len(affected_transactions),
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def log_compliance_check(self, pattern_id: str, status: str, regulation: str) -> None:
        """Log compliance check result."""
        message = f"Compliance check for pattern {pattern_id}: {status} ({regulation})"
        level = logging.INFO if status == "compliant" else logging.WARNING
        self.logger.log(level, message)
        
        self._add_audit_log("compliance_check", {
            "pattern_id": pattern_id,
            "status": status,
            "regulation": regulation,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def log_verification_result(self, pattern_id: str, consensus_reached: bool, consensus_score: float) -> None:
        """Log verification result."""
        status = "consensus" if consensus_reached else "disagreement"
        message = f"Verification for pattern {pattern_id}: {status} (score: {consensus_score:.2f})"
        self.logger.info(message)
        
        self._add_audit_log("verification_result", {
            "pattern_id": pattern_id,
            "consensus_reached": consensus_reached,
            "consensus_score": consensus_score,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """Log error with context."""
        message = f"Error: {str(error)}"
        if context:
            message += f" | Context: {context}"
        self.logger.error(message, exc_info=True)
        
        self._add_audit_log("error", {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {},
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def log_performance(self, operation: str, duration: float, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Log performance metrics."""
        message = f"Performance: {operation} took {duration:.2f}s"
        if metadata:
            message += f" | {metadata}"
        self.logger.info(message)
        
        self._add_audit_log("performance", {
            "operation": operation,
            "duration": duration,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def _add_audit_log(self, event_type: str, data: Dict[str, Any]) -> None:
        """Add log entry to audit trail."""
        log_entry = {
            "event_type": event_type,
            "data": data
        }
        
        self.audit_logs.append(log_entry)
        
        # Maintain log size limit
        if len(self.audit_logs) > self.max_audit_logs:
            self.audit_logs = self.audit_logs[-self.max_audit_logs:]
    
    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize data to remove sensitive information."""
        sanitized = {}
        sensitive_keys = {'password', 'api_key', 'token', 'secret', 'ssn', 'credit_card'}
        
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = '[REDACTED]'
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_data(value)
            elif isinstance(value, list):
                sanitized[key] = [self._sanitize_data(item) if isinstance(item, dict) else item for item in value]
            else:
                sanitized[key] = value
        
        return sanitized
    
    def get_audit_logs(self, event_type: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get audit logs with optional filtering."""
        logs = self.audit_logs
        
        if event_type:
            logs = [log for log in logs if log["event_type"] == event_type]
        
        if limit:
            logs = logs[-limit:]
        
        return logs
    
    def export_audit_logs(self, file_path: str) -> None:
        """Export audit logs to JSON file."""
        with open(file_path, 'w') as f:
            json.dump(self.audit_logs, f, indent=2, default=str)
    
    def clear_audit_logs(self) -> None:
        """Clear audit logs."""
        self.audit_logs.clear()


# Global logger instance
logger = OrchestratorLogger()


@asynccontextmanager
async def log_task_execution(task_id: str, agent_name: str, task_type: str):
    """Context manager for logging task execution."""
    start_time = datetime.utcnow()
    logger.log_task_start(task_id, agent_name, task_type)
    
    try:
        yield
        success = True
    except Exception as e:
        success = False
        logger.log_error(e, {"task_id": task_id, "agent_name": agent_name})
        raise
    finally:
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.log_task_complete(task_id, agent_name, success, duration)


class AsyncLogger:
    """Async-compatible logger wrapper."""
    
    def __init__(self, logger_instance: OrchestratorLogger):
        """Initialize async logger."""
        self.logger = logger_instance
        self.loop = asyncio.get_event_loop()
    
    async def log_task_start(self, task_id: str, agent_name: str, task_type: str) -> None:
        """Async log task start."""
        await self.loop.run_in_executor(
            None, self.logger.log_task_start, task_id, agent_name, task_type
        )
    
    async def log_task_complete(self, task_id: str, agent_name: str, success: bool, duration: float) -> None:
        """Async log task completion."""
        await self.loop.run_in_executor(
            None, self.logger.log_task_complete, task_id, agent_name, success, duration
        )
    
    async def log_agent_message(self, from_agent: str, to_agent: str, message_type: str, data: Dict[str, Any]) -> None:
        """Async log agent message."""
        await self.loop.run_in_executor(
            None, self.logger.log_agent_message, from_agent, to_agent, message_type, data
        )
    
    async def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """Async log error."""
        await self.loop.run_in_executor(
            None, self.logger.log_error, error, context
        )


# Global async logger instance
async_logger = AsyncLogger(logger) 