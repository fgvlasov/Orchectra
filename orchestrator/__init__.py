"""
Multi-Agent Orchestration Platform for AML Analysis

This package provides a complete multi-agent orchestration system using LangChain
for anti-money laundering (AML) use cases.
"""

__version__ = "1.0.0"
__author__ = "Orchectra Team"

from .main import Orchestrator
from .models.task import Task, TaskResult, TaskStatus
from .models.report import Report, SuspiciousPattern, ComplianceCheck

__all__ = [
    "Orchestrator",
    "Task",
    "TaskResult", 
    "TaskStatus",
    "Report",
    "SuspiciousPattern",
    "ComplianceCheck"
] 