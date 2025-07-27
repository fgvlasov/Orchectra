"""
Base agent class for the orchestrator platform.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from ..models.task import Task, TaskResult, TaskStatus
from ..config.settings import settings
from ..utils.logging import async_logger


class BaseAgent(ABC):
    """Base class for all agents in the orchestrator."""
    
    def __init__(self, name: str, llm: Optional[ChatOpenAI] = None):
        """Initialize the base agent."""
        self.name = name
        self.llm = llm or self._create_llm()
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.is_running = False
        self.processed_tasks = 0
        self.failed_tasks = 0
        
    def _create_llm(self) -> ChatOpenAI:
        """Create the language model instance."""
        return ChatOpenAI(
            model=settings.openai.model,
            temperature=settings.openai.temperature,
            max_tokens=settings.openai.max_tokens,
            openai_api_key=settings.openai.api_key
        )
    
    @abstractmethod
    async def process_task(self, task: Task) -> TaskResult:
        """Process a task and return the result."""
        pass
    
    async def validate_input(self, task: Task) -> bool:
        """Validate task input."""
        # Base validation - can be overridden by subclasses
        if not task.payload:
            return False
        return True
    
    async def handle_error(self, error: Exception, task: Task) -> TaskResult:
        """Handle errors during task processing."""
        await async_logger.log_error(error, {
            "agent_name": self.name,
            "task_id": task.id,
            "task_type": task.type
        })
        
        return TaskResult(
            task_id=task.id,
            success=False,
            error=str(error),
            agent_name=self.name
        )
    
    async def start(self) -> None:
        """Start the agent's processing loop."""
        self.is_running = True
        await async_logger.log_task_start("agent_start", self.name, "agent_startup")
        
        while self.is_running:
            try:
                # Wait for tasks with timeout
                try:
                    task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                
                # Process the task
                await self._process_task_with_logging(task)
                
            except Exception as e:
                await async_logger.log_error(e, {"agent_name": self.name})
    
    async def stop(self) -> None:
        """Stop the agent's processing loop."""
        self.is_running = False
        await async_logger.log_task_complete("agent_stop", self.name, True, 0.0)
    
    async def submit_task(self, task: Task) -> None:
        """Submit a task to this agent."""
        await self.task_queue.put(task)
    
    async def _process_task_with_logging(self, task: Task) -> None:
        """Process a task with comprehensive logging."""
        start_time = datetime.utcnow()
        
        try:
            # Validate input
            if not await self.validate_input(task):
                raise ValueError(f"Invalid input for task {task.id}")
            
            # Process task
            result = await self.process_task(task)
            
            # Update statistics
            self.processed_tasks += 1
            
            # Log completion
            duration = (datetime.utcnow() - start_time).total_seconds()
            await async_logger.log_task_complete(task.id, self.name, result.success, duration)
            
        except Exception as e:
            # Handle error
            result = await self.handle_error(e, task)
            self.failed_tasks += 1
            
            # Log error
            duration = (datetime.utcnow() - start_time).total_seconds()
            await async_logger.log_task_complete(task.id, self.name, False, duration)
    
    async def get_status(self) -> Dict[str, Any]:
        """Get agent status information."""
        return {
            "name": self.name,
            "is_running": self.is_running,
            "processed_tasks": self.processed_tasks,
            "failed_tasks": self.failed_tasks,
            "queue_size": self.task_queue.qsize(),
            "success_rate": self.processed_tasks / (self.processed_tasks + self.failed_tasks) if (self.processed_tasks + self.failed_tasks) > 0 else 0.0
        }
    
    async def call_llm(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Call the language model with messages."""
        try:
            # Convert messages to LangChain format
            langchain_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    langchain_messages.append(SystemMessage(content=msg["content"]))
                elif msg["role"] == "user":
                    langchain_messages.append(HumanMessage(content=msg["content"]))
            
            # Call LLM
            response = await self.llm.agenerate([langchain_messages])
            return response.generations[0][0].text.strip()
            
        except Exception as e:
            await async_logger.log_error(e, {
                "agent_name": self.name,
                "operation": "llm_call"
            })
            raise
    
    async def call_llm_simple(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Simple LLM call with a single prompt."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        return await self.call_llm(messages) 