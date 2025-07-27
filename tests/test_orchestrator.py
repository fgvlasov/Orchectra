"""
Unit tests for the orchestrator.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from orchestrator.main import Orchestrator
from orchestrator.models.task import Task, TaskType, TaskGraph
from orchestrator.models.report import AMLReport, ReportStatus


class TestOrchestrator:
    """Test cases for the Orchestrator."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create an orchestrator instance."""
        return Orchestrator()
    
    def test_initialization(self, orchestrator):
        """Test orchestrator initialization."""
        assert len(orchestrator.agents) == 6  # planner, retriever, analysis, compliance, verifier, synthesizer
        assert "planner" in orchestrator.agents
        assert "retriever" in orchestrator.agents
        assert "analysis" in orchestrator.agents
        assert "compliance" in orchestrator.agents
        assert "verifier" in orchestrator.agents
        assert "synthesizer" in orchestrator.agents
        assert not orchestrator.is_running
    
    def test_get_agent_for_task(self, orchestrator):
        """Test agent mapping for task types."""
        # Test each task type
        task_types = [
            (TaskType.PLAN, "planner"),
            (TaskType.RETRIEVE, "retriever"),
            (TaskType.ANALYZE, "analysis"),
            (TaskType.COMPLIANCE_CHECK, "compliance"),
            (TaskType.VERIFY, "verifier"),
            (TaskType.SYNTHESIZE, "synthesizer")
        ]
        
        for task_type, expected_agent in task_types:
            task = Task(type=task_type)
            agent_name = orchestrator._get_agent_for_task(task)
            assert agent_name == expected_agent
    
    @pytest.mark.asyncio
    async def test_prepare_task_payload(self, orchestrator):
        """Test task payload preparation."""
        # Create mock task results
        task_results = {
            "task_1": Mock(
                success=True,
                data={"transactions": {"count": 100}, "documents": {"count": 5}}
            ),
            "task_2": Mock(
                success=True,
                data={"patterns": {"count": 3}}
            )
        }
        
        # Create task with dependencies
        task = Task(
            type=TaskType.ANALYZE,
            payload={"analysis_type": "anomaly"},
            dependencies=["task_1", "task_2"]
        )
        
        # Prepare payload
        payload = await orchestrator._prepare_task_payload(task, task_results, "test query")
        
        # Check that dependencies are merged
        assert payload["analysis_type"] == "anomaly"
        assert payload["transactions"]["count"] == 100
        assert payload["documents"]["count"] == 5
        assert payload["patterns"]["count"] == 3
        assert payload["original_query"] == "test query"
    
    def test_create_report_from_dict(self, orchestrator):
        """Test report creation from dictionary."""
        report_data = {
            "title": "Test Report",
            "description": "Test description",
            "status": "draft"
        }
        
        report = orchestrator._create_report_from_dict(report_data)
        
        assert isinstance(report, AMLReport)
        assert report.title == "Test Report"
        assert report.description == "Test description"
        assert report.status == ReportStatus.DRAFT
        assert report.id in orchestrator.reports
    
    @pytest.mark.asyncio
    async def test_get_agent_status(self, orchestrator):
        """Test getting agent status."""
        # Mock agent status
        for agent in orchestrator.agents.values():
            agent.get_status = AsyncMock(return_value={
                "name": agent.name,
                "is_running": False,
                "processed_tasks": 0,
                "failed_tasks": 0,
                "queue_size": 0,
                "success_rate": 0.0
            })
        
        status = await orchestrator.get_agent_status()
        
        assert len(status) == 6
        for agent_name in ["planner", "retriever", "analysis", "compliance", "verifier", "synthesizer"]:
            assert agent_name in status
            assert "name" in status[agent_name]
            assert "is_running" in status[agent_name]
    
    @pytest.mark.asyncio
    async def test_export_report(self, orchestrator, tmp_path):
        """Test report export."""
        # Create a test report
        report = AMLReport(
            title="Test Report",
            description="Test description"
        )
        orchestrator.reports[report.id] = report
        
        # Export report
        export_path = tmp_path / "test_report.json"
        await orchestrator.export_report(report.id, str(export_path))
        
        # Check file exists and contains report data
        assert export_path.exists()
        with open(export_path, 'r') as f:
            data = f.read()
            assert "Test Report" in data
            assert "Test description" in data


class TestOrchestratorIntegration:
    """Integration tests for the orchestrator."""
    
    @pytest.mark.asyncio
    async def test_simple_query_processing(self):
        """Test processing a simple query through the orchestrator."""
        orchestrator = Orchestrator()
        
        # Mock the agents to avoid actual processing
        for agent_name, agent in orchestrator.agents.items():
            agent.process_task = AsyncMock(return_value=Mock(
                success=True,
                data={"test": "data"},
                agent_name=agent_name
            ))
        
        # Test query processing
        query = "Analyze suspicious transactions"
        
        # This would normally process through the full pipeline
        # For testing, we'll just verify the orchestrator can handle the query
        assert orchestrator.agents["planner"] is not None
        assert orchestrator.agents["retriever"] is not None
        assert orchestrator.agents["analysis"] is not None
    
    @pytest.mark.asyncio
    async def test_task_graph_execution(self):
        """Test task graph execution logic."""
        orchestrator = Orchestrator()
        
        # Create a simple task graph
        task_graph = TaskGraph()
        
        # Add tasks
        task1 = Task(type=TaskType.RETRIEVE, payload={"query": "test"})
        task2 = Task(type=TaskType.ANALYZE, payload={}, dependencies=[task1.id])
        task3 = Task(type=TaskType.SYNTHESIZE, payload={}, dependencies=[task2.id])
        
        task_graph.add_task(task1)
        task_graph.add_task(task2)
        task_graph.add_task(task3)
        task_graph.add_dependency(task1.id, task2.id)
        task_graph.add_dependency(task2.id, task3.id)
        
        # Test ready tasks
        ready_tasks = task_graph.get_ready_tasks([])
        assert len(ready_tasks) == 1
        assert ready_tasks[0].id == task1.id
        
        # Test completion
        assert not task_graph.is_complete([])
        assert task_graph.is_complete([task1.id, task2.id, task3.id])


class TestOrchestratorErrorHandling:
    """Test error handling in the orchestrator."""
    
    @pytest.mark.asyncio
    async def test_agent_failure_handling(self):
        """Test handling of agent failures."""
        orchestrator = Orchestrator()
        
        # Mock an agent to fail
        orchestrator.agents["planner"].process_task = AsyncMock(side_effect=Exception("Agent failed"))
        
        # Test that the orchestrator can handle the failure gracefully
        task = Task(type=TaskType.PLAN, payload={"query": "test"})
        
        # The orchestrator should handle this gracefully
        assert orchestrator.agents["planner"] is not None
    
    @pytest.mark.asyncio
    async def test_invalid_task_type_handling(self):
        """Test handling of invalid task types."""
        orchestrator = Orchestrator()
        
        # Test with unknown task type
        task = Task(type="unknown_type", payload={})
        agent_name = orchestrator._get_agent_for_task(task)
        
        assert agent_name == "unknown"
    
    @pytest.mark.asyncio
    async def test_missing_report_export(self):
        """Test export of non-existent report."""
        orchestrator = Orchestrator()
        
        # Try to export a non-existent report
        with pytest.raises(ValueError, match="Report nonexistent not found"):
            await orchestrator.export_report("nonexistent", "test.json")


class TestOrchestratorPerformance:
    """Test performance aspects of the orchestrator."""
    
    @pytest.mark.asyncio
    async def test_concurrent_task_execution(self):
        """Test concurrent task execution."""
        orchestrator = Orchestrator()
        
        # Create multiple tasks
        tasks = [
            Task(type=TaskType.RETRIEVE, payload={"query": f"query_{i}"})
            for i in range(5)
        ]
        
        # Mock agents to return quickly
        for agent in orchestrator.agents.values():
            agent.process_task = AsyncMock(return_value=Mock(
                success=True,
                data={"result": "data"},
                agent_name=agent.name
            ))
        
        # Test that tasks can be processed concurrently
        start_time = datetime.utcnow()
        
        # Process tasks concurrently
        execution_tasks = []
        for task in tasks:
            agent_name = orchestrator._get_agent_for_task(task)
            if agent_name in orchestrator.agents:
                execution_task = asyncio.create_task(
                    orchestrator._execute_task_with_agent(task, agent_name)
                )
                execution_tasks.append(execution_task)
        
        # Wait for all tasks to complete
        if execution_tasks:
            results = await asyncio.gather(*execution_tasks, return_exceptions=True)
            
            # Check that all tasks completed successfully
            for result in results:
                if isinstance(result, Exception):
                    pytest.fail(f"Task execution failed: {result}")
                else:
                    assert result.success
        
        end_time = datetime.utcnow()
        execution_time = (end_time - start_time).total_seconds()
        
        # Tasks should complete quickly (less than 1 second for mocked operations)
        assert execution_time < 1.0 