"""
Unit tests for agent implementations.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from decimal import Decimal
from datetime import datetime

from orchestrator.models.task import Task, TaskType
from orchestrator.models.transaction import Transaction, TransactionType, RiskLevel
from orchestrator.agents import (
    PlannerAgent, RetrieverAgent, AnalysisAgent,
    ComplianceAgent, VerifierAgent, SynthesizerAgent
)


class TestPlannerAgent:
    """Test cases for PlannerAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create a planner agent instance."""
        return PlannerAgent()
    
    @pytest.mark.asyncio
    async def test_process_task_valid_query(self, agent):
        """Test processing a valid planning task."""
        task = Task(
            type=TaskType.PLAN,
            payload={"query": "Analyze suspicious transactions"}
        )
        
        result = await agent.process_task(task)
        
        assert result.success
        assert "task_graph" in result.data
        assert result.data["query"] == "Analyze suspicious transactions"
    
    @pytest.mark.asyncio
    async def test_process_task_invalid_query(self, agent):
        """Test processing a task with invalid query."""
        task = Task(
            type=TaskType.PLAN,
            payload={}  # Missing query
        )
        
        result = await agent.process_task(task)
        
        assert not result.success
        assert "No query provided" in result.error


class TestRetrieverAgent:
    """Test cases for RetrieverAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create a retriever agent instance."""
        return RetrieverAgent()
    
    @pytest.mark.asyncio
    async def test_process_task_valid_retrieval(self, agent):
        """Test processing a valid retrieval task."""
        task = Task(
            type=TaskType.RETRIEVE,
            payload={
                "query": "suspicious transactions",
                "data_sources": ["transactions", "regulatory_docs"]
            }
        )
        
        result = await agent.process_task(task)
        
        assert result.success
        assert "transactions" in result.data
        assert "documents" in result.data
    
    def test_create_sample_transactions(self, agent):
        """Test creation of sample transactions."""
        transactions = agent._create_sample_transactions()
        
        assert len(transactions) > 0
        assert all(isinstance(tx, Transaction) for tx in transactions)
    
    def test_create_sample_documents(self, agent):
        """Test creation of sample documents."""
        documents = agent._create_sample_documents()
        
        assert len(documents) > 0
        assert all("title" in doc for doc in documents)
        assert all("content" in doc for doc in documents)


class TestAnalysisAgent:
    """Test cases for AnalysisAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create an analysis agent instance."""
        return AnalysisAgent()
    
    @pytest.fixture
    def sample_transactions(self):
        """Create sample transactions for testing."""
        return [
            Transaction(
                amount=Decimal("1000"),
                transaction_type=TransactionType.TRANSFER,
                sender_id="entity_001",
                recipient_id="entity_002",
                risk_level=RiskLevel.LOW
            ),
            Transaction(
                amount=Decimal("50000"),
                transaction_type=TransactionType.TRANSFER,
                sender_id="entity_001",
                recipient_id="entity_003",
                risk_level=RiskLevel.HIGH
            )
        ]
    
    @pytest.mark.asyncio
    async def test_process_task_valid_analysis(self, agent, sample_transactions):
        """Test processing a valid analysis task."""
        task = Task(
            type=TaskType.ANALYZE,
            payload={
                "transactions": {
                    "transactions": [
                        {
                            "id": tx.id,
                            "amount": float(tx.amount),
                            "transaction_type": tx.transaction_type.value,
                            "sender_id": tx.sender_id,
                            "recipient_id": tx.recipient_id,
                            "risk_level": tx.risk_level.value
                        } for tx in sample_transactions
                    ]
                },
                "analysis_types": ["anomaly_detection", "pattern_detection"]
            }
        )
        
        result = await agent.process_task(task)
        
        assert result.success
        assert "anomalies" in result.data
        assert "patterns" in result.data
        assert "suspicious_patterns" in result.data
    
    def test_detect_anomalies(self, agent, sample_transactions):
        """Test anomaly detection."""
        # Fit the model first
        agent.anomaly_detector.fit(sample_transactions)
        agent.statistical_detector.fit(sample_transactions)
        
        # Test detection
        anomalies = asyncio.run(agent._detect_anomalies(sample_transactions, 0.05))
        
        assert "total_anomalies" in anomalies
        assert "anomaly_rate" in anomalies
        assert "anomalies" in anomalies


class TestComplianceAgent:
    """Test cases for ComplianceAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create a compliance agent instance."""
        return ComplianceAgent()
    
    @pytest.mark.asyncio
    async def test_process_task_valid_compliance_check(self, agent):
        """Test processing a valid compliance check task."""
        suspicious_patterns = [
            {
                "id": "pattern_001",
                "pattern_type": "structuring",
                "confidence": 0.8,
                "risk_level": "high",
                "indicators": ["multiple transactions", "under threshold"]
            }
        ]
        
        task = Task(
            type=TaskType.COMPLIANCE_CHECK,
            payload={
                "suspicious_patterns": suspicious_patterns,
                "regulations": ["BSA", "PATRIOT_Act"]
            }
        )
        
        result = await agent.process_task(task)
        
        assert result.success
        assert "compliance_checks" in result.data
        assert "summary" in result.data
    
    def test_get_relevant_regulations(self, agent):
        """Test regulation mapping."""
        regulations = agent._get_relevant_regulations("structuring", ["threshold"])
        assert "BSA" in regulations
        assert "PATRIOT_Act" in regulations


class TestVerifierAgent:
    """Test cases for VerifierAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create a verifier agent instance."""
        return VerifierAgent()
    
    @pytest.mark.asyncio
    async def test_process_task_valid_verification(self, agent):
        """Test processing a valid verification task."""
        suspicious_patterns = [
            {
                "id": "pattern_001",
                "pattern_type": "structuring",
                "confidence": 0.8,
                "risk_level": "high",
                "indicators": ["multiple transactions"]
            }
        ]
        
        task = Task(
            type=TaskType.VERIFY,
            payload={
                "suspicious_patterns": suspicious_patterns,
                "verification_method": "multi_agent_consensus",
                "consensus_threshold": 0.8
            }
        )
        
        result = await agent.process_task(task)
        
        assert result.success
        assert "verification_results" in result.data
        assert "summary" in result.data
    
    def test_calculate_consensus(self, agent):
        """Test consensus calculation."""
        agent_results = {
            "agent1": {"verified": True, "confidence": 0.8},
            "agent2": {"verified": True, "confidence": 0.9},
            "agent3": {"verified": False, "confidence": 0.7}
        }
        
        consensus_reached, consensus_score, disagreements = agent._calculate_consensus(agent_results, 0.8)
        
        assert isinstance(consensus_reached, bool)
        assert isinstance(consensus_score, float)
        assert isinstance(disagreements, list)


class TestSynthesizerAgent:
    """Test cases for SynthesizerAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create a synthesizer agent instance."""
        return SynthesizerAgent()
    
    @pytest.mark.asyncio
    async def test_process_task_valid_synthesis(self, agent):
        """Test processing a valid synthesis task."""
        task = Task(
            type=TaskType.SYNTHESIZE,
            payload={
                "transactions": {"transaction_count": 100, "total_amount": 50000},
                "analysis_results": {
                    "suspicious_patterns": [
                        {
                            "pattern_type": "structuring",
                            "confidence": 0.8,
                            "risk_level": "high"
                        }
                    ]
                },
                "compliance_results": {
                    "compliance_checks": [
                        {
                            "pattern_id": "pattern_001",
                            "status": "non_compliant",
                            "regulation_reference": "BSA"
                        }
                    ]
                },
                "verification_results": {
                    "verification_results": [
                        {
                            "pattern_id": "pattern_001",
                            "consensus_reached": True,
                            "consensus_score": 0.8
                        }
                    ]
                }
            }
        )
        
        result = await agent.process_task(task)
        
        assert result.success
        assert "report" in result.data
        assert "report_id" in result.data
        assert "summary" in result.data


# Integration test for agent communication
class TestAgentIntegration:
    """Integration tests for agent communication."""
    
    @pytest.mark.asyncio
    async def test_agent_chain_execution(self):
        """Test a simple chain of agent executions."""
        # Create agents
        planner = PlannerAgent()
        retriever = RetrieverAgent()
        analysis = AnalysisAgent()
        
        # Test planning
        plan_task = Task(
            type=TaskType.PLAN,
            payload={"query": "Find suspicious transactions"}
        )
        plan_result = await planner.process_task(plan_task)
        assert plan_result.success
        
        # Test retrieval
        retrieve_task = Task(
            type=TaskType.RETRIEVE,
            payload={"query": "suspicious transactions"}
        )
        retrieve_result = await retriever.process_task(retrieve_task)
        assert retrieve_result.success
        
        # Test analysis with retrieved data
        analysis_task = Task(
            type=TaskType.ANALYZE,
            payload={
                "transactions": retrieve_result.data["transactions"],
                "analysis_types": ["anomaly_detection"]
            }
        )
        analysis_result = await analysis.process_task(analysis_task)
        assert analysis_result.success 