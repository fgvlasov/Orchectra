"""
Main orchestrator for the multi-agent AML analysis platform.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from .models.task import Task, TaskResult, TaskStatus, TaskType, TaskGraph
from .models.report import AMLReport
from .agents import (
    PlannerAgent, RetrieverAgent, AnalysisAgent, 
    ComplianceAgent, VerifierAgent, SynthesizerAgent, BaseAgent
)
from .config.settings import settings
from .utils.logging import logger, async_logger


class Orchestrator:
    """Main orchestrator for the multi-agent AML analysis platform."""
    
    def __init__(self):
        """Initialize the orchestrator."""
        self.agents: Dict[str, BaseAgent] = {}
        self.task_results: Dict[str, TaskResult] = {}
        self.reports: Dict[str, AMLReport] = {}
        self.is_running = False
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.completed_tasks: List[str] = []
        
        # Initialize agents
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all agents."""
        # Create agents
        self.agents["planner"] = PlannerAgent()
        self.agents["retriever"] = RetrieverAgent()
        self.agents["analysis"] = AnalysisAgent()
        self.agents["compliance"] = ComplianceAgent()
        self.agents["verifier"] = VerifierAgent()
        self.agents["synthesizer"] = SynthesizerAgent()
        
        logger.info(f"Initialized {len(self.agents)} agents")
    
    async def start(self):
        """Start the orchestrator and all agents."""
        if self.is_running:
            return
        
        self.is_running = True
        logger.info("Starting orchestrator...")
        
        # Start all agents
        agent_tasks = []
        for agent_name, agent in self.agents.items():
            task = asyncio.create_task(agent.start())
            agent_tasks.append(task)
            logger.info(f"Started agent: {agent_name}")
        
        # Start the main orchestration loop
        orchestration_task = asyncio.create_task(self._orchestration_loop())
        
        # Wait for all tasks
        try:
            await asyncio.gather(orchestration_task, *agent_tasks)
        except Exception as e:
            logger.error(f"Error in orchestrator: {e}")
            await self.stop()
    
    async def stop(self):
        """Stop the orchestrator and all agents."""
        if not self.is_running:
            return
        
        self.is_running = False
        logger.info("Stopping orchestrator...")
        
        # Stop all agents
        for agent_name, agent in self.agents.items():
            await agent.stop()
            logger.info(f"Stopped agent: {agent_name}")
        
        logger.info("Orchestrator stopped")
    
    async def process_query(self, query: str) -> AMLReport:
        """Process a user query through the complete pipeline."""
        logger.info(f"Processing query: {query}")
        
        # Create initial planning task
        planning_task = Task(
            type=TaskType.PLAN,
            payload={"query": query},
            sender="user"
        )
        
        # Submit to planner
        await self.agents["planner"].submit_task(planning_task)
        
        # Wait for planning to complete
        planning_result = await self._wait_for_task_completion(planning_task.id)
        
        if not planning_result.success:
            raise Exception(f"Planning failed: {planning_result.error}")
        
        # Extract task graph
        task_graph = planning_result.data["task_graph"]
        
        # Execute the task graph
        final_result = await self._execute_task_graph(task_graph, query)
        
        return final_result
    
    async def _execute_task_graph(self, task_graph: TaskGraph, original_query: str) -> AMLReport:
        """Execute a task graph."""
        logger.info(f"Executing task graph with {len(task_graph.tasks)} tasks")
        
        # Track task dependencies and results
        task_results = {}
        completed_tasks = set()
        
        while not task_graph.is_complete(list(completed_tasks)):
            # Get ready tasks
            ready_tasks = task_graph.get_ready_tasks(list(completed_tasks))
            
            if not ready_tasks:
                logger.warning("No ready tasks but graph not complete - possible deadlock")
                break
            
            # Execute ready tasks concurrently
            execution_tasks = []
            for task in ready_tasks:
                # Prepare task payload with results from dependencies
                task.payload = await self._prepare_task_payload(task, task_results, original_query)
                
                # Submit task to appropriate agent
                agent_name = self._get_agent_for_task(task)
                if agent_name in self.agents:
                    execution_task = asyncio.create_task(
                        self._execute_task_with_agent(task, agent_name)
                    )
                    execution_tasks.append(execution_task)
                else:
                    logger.error(f"No agent found for task type: {task.type}")
            
            # Wait for all tasks to complete
            if execution_tasks:
                results = await asyncio.gather(*execution_tasks, return_exceptions=True)
                
                # Process results
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logger.error(f"Task execution failed: {result}")
                        task_results[ready_tasks[i].id] = TaskResult(
                            task_id=ready_tasks[i].id,
                            success=False,
                            error=str(result)
                        )
                    else:
                        task_results[ready_tasks[i].id] = result
                        completed_tasks.add(ready_tasks[i].id)
        
        # Extract final report from synthesizer task
        synthesizer_tasks = [t for t in task_graph.tasks if t.type == TaskType.SYNTHESIZE]
        if synthesizer_tasks:
            final_task_id = synthesizer_tasks[0].id
            if final_task_id in task_results:
                final_result = task_results[final_task_id]
                if final_result.success and "report" in final_result.data:
                    report_data = final_result.data["report"]
                    return self._create_report_from_dict(report_data)
        
        raise Exception("Failed to generate final report")
    
    async def _prepare_task_payload(self, task: Task, task_results: Dict[str, TaskResult], original_query: str) -> Dict[str, Any]:
        """Prepare task payload with results from dependencies."""
        payload = task.payload.copy()
        
        # Add results from dependent tasks
        for dep_id in task.dependencies:
            if dep_id in task_results:
                dep_result = task_results[dep_id]
                if dep_result.success:
                    payload.update(dep_result.data)
        
        # Add original query for context
        payload["original_query"] = original_query
        
        return payload
    
    def _get_agent_for_task(self, task: Task) -> str:
        """Get the agent name for a task type."""
        agent_mapping = {
            TaskType.PLAN: "planner",
            TaskType.RETRIEVE: "retriever",
            TaskType.ANALYZE: "analysis",
            TaskType.COMPLIANCE_CHECK: "compliance",
            TaskType.VERIFY: "verifier",
            TaskType.SYNTHESIZE: "synthesizer"
        }
        
        return agent_mapping.get(task.type, "unknown")
    
    async def _execute_task_with_agent(self, task: Task, agent_name: str) -> TaskResult:
        """Execute a task with a specific agent."""
        agent = self.agents[agent_name]
        
        # Submit task to agent
        await agent.submit_task(task)
        
        # Wait for completion
        return await self._wait_for_task_completion(task.id)
    
    async def _wait_for_task_completion(self, task_id: str, timeout: float = 300.0) -> TaskResult:
        """Wait for a task to complete."""
        start_time = datetime.utcnow()
        
        while (datetime.utcnow() - start_time).total_seconds() < timeout:
            # Check if task is in results
            for agent in self.agents.values():
                # This is a simplified approach - in a real system, you'd have better task tracking
                pass
            
            await asyncio.sleep(0.1)
        
        raise TimeoutError(f"Task {task_id} did not complete within {timeout} seconds")
    
    def _create_report_from_dict(self, report_data: Dict[str, Any]) -> AMLReport:
        """Create an AMLReport from dictionary data."""
        # This would need proper deserialization logic
        # For now, return a simple report
        report = AMLReport(
            title=report_data.get("title", "AML Analysis Report"),
            description=report_data.get("description", ""),
            status=report_data.get("status", "draft")
        )
        
        # Store the report
        self.reports[report.id] = report
        
        return report
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents."""
        status = {}
        for agent_name, agent in self.agents.items():
            status[agent_name] = await agent.get_status()
        return status
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task."""
        # This would need proper task tracking implementation
        return None
    
    async def get_agent_logs(self, agent_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get logs from agents."""
        if agent_name:
            if agent_name in self.agents:
                return logger.get_audit_logs(event_type=f"agent_{agent_name}")
            return []
        else:
            return logger.get_audit_logs()
    
    async def export_report(self, report_id: str, file_path: str):
        """Export a report to file."""
        if report_id not in self.reports:
            raise ValueError(f"Report {report_id} not found")
        
        report = self.reports[report_id]
        report_data = report.to_dict()
        
        with open(file_path, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        logger.info(f"Exported report {report_id} to {file_path}")


# Convenience function for running the orchestrator
async def run_orchestrator():
    """Run the orchestrator with a sample query."""
    orchestrator = Orchestrator()
    
    try:
        # Start the orchestrator
        await orchestrator.start()
        
        # Process a sample query
        query = "Analyze transactions for suspicious patterns in the last 30 days"
        report = await orchestrator.process_query(query)
        
        print(f"Generated report: {report.title}")
        print(f"Report ID: {report.id}")
        print(f"Status: {report.status}")
        
        # Export the report
        await orchestrator.export_report(report.id, "aml_report.json")
        
    except Exception as e:
        logger.error(f"Error running orchestrator: {e}")
    finally:
        await orchestrator.stop()


if __name__ == "__main__":
    asyncio.run(run_orchestrator()) 