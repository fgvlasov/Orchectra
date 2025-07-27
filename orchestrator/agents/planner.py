"""
Planner agent for parsing user queries and creating task graphs.
"""

from typing import Dict, Any, List
from ..models.task import Task, TaskResult, TaskType, TaskGraph
from ..models.report import AMLReport
from .base import BaseAgent


class PlannerAgent(BaseAgent):
    """Agent responsible for planning and task decomposition."""
    
    def __init__(self, name: str = "planner"):
        """Initialize the planner agent."""
        super().__init__(name)
        self.system_prompt = """
        You are a task planning agent for an anti-money laundering (AML) analysis system.
        Your job is to parse user queries and create a structured plan of tasks that need to be executed.
        
        Available task types:
        - retrieve: Fetch transaction data and regulatory documents
        - analyze: Run anomaly detection and pattern analysis
        - compliance_check: Check patterns against AML regulations
        - synthesize: Create comprehensive reports
        - verify: Perform multi-agent verification
        
        Always create a logical flow of tasks with proper dependencies.
        """
    
    async def process_task(self, task: Task) -> TaskResult:
        """Process a planning task."""
        try:
            query = task.payload.get("query", "")
            if not query:
                raise ValueError("No query provided in task payload")
            
            # Create task graph
            task_graph = await self._create_task_graph(query)
            
            return TaskResult(
                task_id=task.id,
                success=True,
                data={
                    "task_graph": task_graph,
                    "query": query,
                    "total_tasks": len(task_graph.tasks)
                },
                agent_name=self.name
            )
            
        except Exception as e:
            return await self.handle_error(e, task)
    
    async def _create_task_graph(self, query: str) -> TaskGraph:
        """Create a task graph based on the user query."""
        # Use LLM to understand the query and plan tasks
        planning_prompt = f"""
        Analyze this AML analysis query and create a plan:
        
        Query: {query}
        
        Create a JSON response with the following structure:
        {{
            "tasks": [
                {{
                    "type": "task_type",
                    "description": "task description",
                    "priority": 1-5,
                    "dependencies": ["task_id1", "task_id2"]
                }}
            ]
        }}
        
        Task types available: retrieve, analyze, compliance_check, synthesize, verify
        """
        
        try:
            response = await self.call_llm_simple(planning_prompt, self.system_prompt)
            
            # Parse the response (in a real system, you'd use proper JSON parsing)
            # For now, we'll create a default plan
            task_graph = await self._create_default_plan(query)
            
        except Exception:
            # Fallback to default plan if LLM fails
            task_graph = await self._create_default_plan(query)
        
        return task_graph
    
    async def _create_default_plan(self, query: str) -> TaskGraph:
        """Create a default task plan for AML analysis."""
        task_graph = TaskGraph()
        
        # Create tasks based on query content
        tasks = []
        
        # Task 1: Retrieve data
        retrieve_task = Task(
            type=TaskType.RETRIEVE,
            payload={
                "query": query,
                "data_sources": ["transactions", "regulatory_docs"],
                "time_range": "last_30_days"
            },
            priority=1
        )
        tasks.append(retrieve_task)
        
        # Task 2: Analyze transactions
        analyze_task = Task(
            type=TaskType.ANALYZE,
            payload={
                "analysis_types": ["anomaly_detection", "pattern_detection"],
                "thresholds": {"anomaly": 0.05, "pattern": 0.7}
            },
            priority=2,
            dependencies=[retrieve_task.id]
        )
        tasks.append(analyze_task)
        
        # Task 3: Compliance check
        compliance_task = Task(
            type=TaskType.COMPLIANCE_CHECK,
            payload={
                "regulations": ["BSA", "PATRIOT_Act", "OFAC"],
                "risk_assessment": True
            },
            priority=3,
            dependencies=[analyze_task.id]
        )
        tasks.append(compliance_task)
        
        # Task 4: Verify findings
        verify_task = Task(
            type=TaskType.VERIFY,
            payload={
                "verification_method": "multi_agent_consensus",
                "consensus_threshold": 0.8
            },
            priority=4,
            dependencies=[compliance_task.id]
        )
        tasks.append(verify_task)
        
        # Task 5: Synthesize report
        synthesize_task = Task(
            type=TaskType.SYNTHESIZE,
            payload={
                "report_type": "aml_analysis",
                "include_recommendations": True
            },
            priority=5,
            dependencies=[verify_task.id]
        )
        tasks.append(synthesize_task)
        
        # Add tasks to graph
        for task in tasks:
            task_graph.add_task(task)
        
        # Add dependencies
        for task in tasks:
            for dep_id in task.dependencies:
                task_graph.add_dependency(dep_id, task.id)
        
        return task_graph
    
    async def validate_input(self, task: Task) -> bool:
        """Validate planner task input."""
        if not await super().validate_input(task):
            return False
        
        # Check for required fields
        if "query" not in task.payload:
            return False
        
        return True 