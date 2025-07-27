"""
Unit tests for supply chain agents.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from typing import Dict, Any, List

from orchestrator.agents.supply_chain_agents import (
    InternalRetrieverAgent, ExternalRetrieverAgent,
    RiskAnalysisAgent, ESGComplianceAgent
)
from orchestrator.models.task import Task, TaskType
from orchestrator.utils.supplier_parser import SupplierDataParser


class TestInternalRetrieverAgent:
    """Test cases for InternalRetrieverAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create a test agent instance."""
        config = {
            "data_sources": ["test_data/suppliers.csv"],
            "top_k": 5,
            "similarity_threshold": 0.7
        }
        return InternalRetrieverAgent(config)
    
    @pytest.fixture
    def sample_suppliers(self):
        """Sample supplier data for testing."""
        return [
            {
                "id": "supplier_001",
                "name": "Test Supplier 1",
                "country": "Germany",
                "industry": "Technology",
                "esg_score": 0.85,
                "financial_stability": 0.8,
                "prior_violations": 0,
                "risk_level": "low"
            },
            {
                "id": "supplier_002",
                "name": "Test Supplier 2",
                "country": "China",
                "industry": "Manufacturing",
                "esg_score": 0.35,
                "financial_stability": 0.6,
                "prior_violations": 2,
                "risk_level": "medium"
            }
        ]
    
    @pytest.mark.asyncio
    async def test_process_task_success(self, agent, sample_suppliers):
        """Test successful task processing."""
        # Mock the _load_supplier_data method
        with patch.object(agent, '_load_supplier_data', return_value=sample_suppliers):
            task = Task(
                type=TaskType.RETRIEVE,
                payload={"query": "test query"},
                sender="test"
            )
            
            result = await agent.process_task(task)
            
            assert result.success is True
            assert result.data["total_suppliers"] == 2
            assert result.data["filtered_count"] == 2
            assert result.data["data_source"] == "internal_supplier_database"
    
    @pytest.mark.asyncio
    async def test_process_task_failure(self, agent):
        """Test task processing failure."""
        # Mock the _load_supplier_data method to raise an exception
        with patch.object(agent, '_load_supplier_data', side_effect=Exception("Test error")):
            task = Task(
                type=TaskType.RETRIEVE,
                payload={"query": "test query"},
                sender="test"
            )
            
            result = await agent.process_task(task)
            
            assert result.success is False
            assert "Test error" in result.error
    
    @pytest.mark.asyncio
    async def test_filter_suppliers(self, agent, sample_suppliers):
        """Test supplier filtering."""
        query = "test query"
        filtered = await agent._filter_suppliers(sample_suppliers, query)
        
        # Should return suppliers up to top_k limit
        assert len(filtered) <= agent.top_k
        assert all(supplier in sample_suppliers for supplier in filtered)


class TestExternalRetrieverAgent:
    """Test cases for ExternalRetrieverAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create a test agent instance."""
        config = {
            "data_sources": ["test_data/external/"],
            "api_endpoints": ["country_esg_ratings", "violation_database"],
            "top_k": 10,
            "similarity_threshold": 0.6
        }
        return ExternalRetrieverAgent(config)
    
    @pytest.mark.asyncio
    async def test_process_task_success(self, agent):
        """Test successful task processing."""
        task = Task(
            type=TaskType.RETRIEVE,
            payload={"query": "test query"},
            sender="test"
        )
        
        result = await agent.process_task(task)
        
        assert result.success is True
        assert "external_data" in result.data
        assert "data_sources" in result.data
        assert "api_endpoints" in result.data
    
    @pytest.mark.asyncio
    async def test_retrieve_external_data(self, agent):
        """Test external data retrieval."""
        data = await agent._retrieve_external_data()
        
        # Should return mock data structure
        assert "country_esg_ratings" in data
        assert "sanction_lists" in data
        assert "violation_database" in data
        assert "sustainability_reports" in data
        
        # Check data types
        assert isinstance(data["country_esg_ratings"], dict)
        assert isinstance(data["sanction_lists"], list)
        assert isinstance(data["violation_database"], dict)


class TestRiskAnalysisAgent:
    """Test cases for RiskAnalysisAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create a test agent instance."""
        config = {
            "risk_factors": {
                "country_esg_rating": {"weight": 0.25, "threshold": 0.6},
                "prior_violations": {"weight": 0.30, "threshold": 0.7},
                "supply_category_risk": {"weight": 0.20, "threshold": 0.5},
                "financial_stability": {"weight": 0.25, "threshold": 0.6}
            },
            "composite_risk_threshold": 0.65
        }
        return RiskAnalysisAgent(config)
    
    @pytest.fixture
    def sample_suppliers(self):
        """Sample supplier data for testing."""
        return [
            {
                "id": "supplier_001",
                "name": "Low Risk Supplier",
                "country": "Germany",
                "industry": "Technology",
                "esg_score": 0.85,
                "financial_stability": 0.8,
                "prior_violations": 0,
                "supply_category": "Software",
                "risk_level": "low"
            },
            {
                "id": "supplier_002",
                "name": "High Risk Supplier",
                "country": "Russia",
                "industry": "Mining",
                "esg_score": 0.25,
                "financial_stability": 0.4,
                "prior_violations": 5,
                "supply_category": "Raw Materials",
                "risk_level": "high"
            }
        ]
    
    @pytest.fixture
    def sample_external_data(self):
        """Sample external data for testing."""
        return {
            "country_esg_ratings": {
                "Germany": 0.85,
                "Russia": 0.25
            },
            "sanction_lists": [
                {"entity": "High Risk Supplier", "country": "Russia", "reason": "Trade sanctions"}
            ],
            "violation_database": {
                "High Risk Supplier": ["Environmental violations", "Safety violations"]
            }
        }
    
    @pytest.mark.asyncio
    async def test_process_task_success(self, agent, sample_suppliers, sample_external_data):
        """Test successful task processing."""
        task = Task(
            type=TaskType.ANALYZE,
            payload={
                "suppliers": sample_suppliers,
                "external_data": sample_external_data
            },
            sender="test"
        )
        
        result = await agent.process_task(task)
        
        assert result.success is True
        assert "risk_analysis" in result.data
        assert "high_risk_suppliers" in result.data
        assert len(result.data["risk_analysis"]) == 2
    
    def test_calculate_country_esg_risk(self, agent, sample_external_data):
        """Test country ESG risk calculation."""
        supplier = {"country": "Germany"}
        risk = agent._calculate_country_esg_risk(supplier, sample_external_data)
        
        # Germany has 0.85 rating, so risk should be 1 - 0.85 = 0.15
        assert risk == 0.15
        
        # Test unknown country
        supplier_unknown = {"country": "Unknown"}
        risk_unknown = agent._calculate_country_esg_risk(supplier_unknown, sample_external_data)
        assert risk_unknown == 0.5  # Default value
    
    def test_calculate_violation_risk(self, agent, sample_external_data):
        """Test violation risk calculation."""
        # Low violation supplier
        supplier_low = {"name": "Low Risk Supplier", "prior_violations": 0}
        risk_low = agent._calculate_violation_risk(supplier_low, sample_external_data)
        assert risk_low == 0.0
        
        # High violation supplier
        supplier_high = {"name": "High Risk Supplier", "prior_violations": 5}
        risk_high = agent._calculate_violation_risk(supplier_high, sample_external_data)
        assert risk_high > 0.5  # Should be high due to violations
    
    def test_calculate_category_risk(self, agent):
        """Test supply category risk calculation."""
        # High risk category
        supplier_high = {"supply_category": "Chemicals"}
        risk_high = agent._calculate_category_risk(supplier_high)
        assert risk_high == 0.8
        
        # Medium risk category
        supplier_medium = {"supply_category": "Textiles"}
        risk_medium = agent._calculate_category_risk(supplier_medium)
        assert risk_medium == 0.5
        
        # Low risk category
        supplier_low = {"supply_category": "Software"}
        risk_low = agent._calculate_category_risk(supplier_low)
        assert risk_low == 0.3
    
    def test_determine_risk_level(self, agent):
        """Test risk level determination."""
        assert agent._determine_risk_level(0.9) == "critical"
        assert agent._determine_risk_level(0.7) == "high"
        assert agent._determine_risk_level(0.5) == "medium"
        assert agent._determine_risk_level(0.2) == "low"


class TestESGComplianceAgent:
    """Test cases for ESGComplianceAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create a test agent instance."""
        config = {
            "compliance_frameworks": ["EU_CSDDD", "ISO_14001", "SA8000"],
            "risk_categories": {
                "environmental": ["carbon_emissions", "water_usage"],
                "social": ["labor_rights", "human_rights"],
                "governance": ["corruption", "transparency"]
            }
        }
        return ESGComplianceAgent(config)
    
    @pytest.fixture
    def sample_suppliers(self):
        """Sample supplier data for testing."""
        return [
            {
                "id": "supplier_001",
                "name": "Compliant Supplier",
                "country": "Germany",
                "industry": "Technology",
                "esg_score": 0.85,
                "financial_stability": 0.8,
                "prior_violations": 0
            },
            {
                "id": "supplier_002",
                "name": "Non-Compliant Supplier",
                "country": "China",
                "industry": "Chemicals",
                "esg_score": 0.25,
                "financial_stability": 0.3,
                "prior_violations": 5
            }
        ]
    
    @pytest.fixture
    def sample_external_data(self):
        """Sample external data for testing."""
        return {
            "violation_database": {
                "Non-Compliant Supplier": ["Labor violations", "Environmental violations"]
            },
            "sanction_lists": [
                {"entity": "Non-Compliant Supplier", "country": "China", "reason": "Trade restrictions"}
            ]
        }
    
    @pytest.mark.asyncio
    async def test_process_task_success(self, agent, sample_suppliers, sample_external_data):
        """Test successful task processing."""
        task = Task(
            type=TaskType.COMPLIANCE_CHECK,
            payload={
                "suppliers": sample_suppliers,
                "external_data": sample_external_data
            },
            sender="test"
        )
        
        result = await agent.process_task(task)
        
        assert result.success is True
        assert "compliance_assessment" in result.data
        assert "non_compliant_suppliers" in result.data
        assert len(result.data["compliance_assessment"]) == 2
    
    def test_assess_environmental_compliance(self, agent, sample_external_data):
        """Test environmental compliance assessment."""
        # Compliant supplier
        supplier_compliant = {"esg_score": 0.85, "industry": "Technology", "country": "Germany"}
        result = agent._assess_environmental_compliance(supplier_compliant, sample_external_data)
        
        assert result["compliant"] is True
        assert result["score"] == 0.85
        assert result["framework"] == "ISO_14001"
        
        # Non-compliant supplier
        supplier_non_compliant = {"esg_score": 0.25, "industry": "Chemicals", "country": "China"}
        result = agent._assess_environmental_compliance(supplier_non_compliant, sample_external_data)
        
        assert result["compliant"] is False
        assert len(result["issues"]) > 0
    
    def test_assess_social_compliance(self, agent, sample_external_data):
        """Test social compliance assessment."""
        # Compliant supplier
        supplier_compliant = {"name": "Compliant Supplier", "country": "Germany", "supplier_type": "Tier 1"}
        result = agent._assess_social_compliance(supplier_compliant, sample_external_data)
        
        assert result["compliant"] is True
        assert result["framework"] == "SA8000"
        
        # Non-compliant supplier
        supplier_non_compliant = {"name": "Non-Compliant Supplier", "country": "China", "supplier_type": "Tier 2"}
        result = agent._assess_social_compliance(supplier_non_compliant, sample_external_data)
        
        assert result["compliant"] is False
        assert len(result["issues"]) > 0
    
    def test_assess_governance_compliance(self, agent, sample_external_data):
        """Test governance compliance assessment."""
        # Compliant supplier
        supplier_compliant = {"name": "Compliant Supplier", "esg_score": 0.85, "financial_stability": 0.8}
        result = agent._assess_governance_compliance(supplier_compliant, sample_external_data)
        
        assert result["compliant"] is True
        assert result["score"] == 0.8
        assert result["framework"] == "EU_CSDDD"
        
        # Non-compliant supplier
        supplier_non_compliant = {"name": "Non-Compliant Supplier", "esg_score": 0.25, "financial_stability": 0.3}
        result = agent._assess_governance_compliance(supplier_non_compliant, sample_external_data)
        
        assert result["compliant"] is False
        assert len(result["issues"]) > 0
    
    def test_calculate_compliance_score(self, agent):
        """Test compliance score calculation."""
        environmental = {"score": 0.8}
        social = {"score": 0.7}
        governance = {"score": 0.9}
        
        score = agent._calculate_compliance_score(environmental, social, governance)
        expected_score = (0.8 + 0.7 + 0.9) / 3.0
        
        assert score == expected_score
    
    def test_generate_compliance_recommendations(self, agent):
        """Test compliance recommendations generation."""
        # All compliant
        environmental = {"compliant": True}
        social = {"compliant": True}
        governance = {"compliant": True}
        
        recommendations = agent._generate_compliance_recommendations(environmental, social, governance)
        assert "Maintain current compliance standards" in recommendations
        
        # Non-compliant
        environmental = {"compliant": False}
        social = {"compliant": True}
        governance = {"compliant": True}
        
        recommendations = agent._generate_compliance_recommendations(environmental, social, governance)
        assert "Implement environmental management system" in recommendations


class TestSupplierDataParser:
    """Test cases for SupplierDataParser."""
    
    @pytest.fixture
    def parser(self):
        """Create a test parser instance."""
        return SupplierDataParser()
    
    def test_clean_single_supplier(self, parser):
        """Test single supplier data cleaning."""
        raw_supplier = {
            "id": "  supplier_001  ",
            "name": "  Test Supplier  ",
            "country": "  Germany  ",
            "industry": "  Technology  ",
            "esg_score": "0.85",
            "financial_stability": "0.8",
            "prior_violations": "0",
            "annual_spend": "1000000",
            "contract_duration": "3",
            "risk_level": "  LOW  "
        }
        
        cleaned = parser._clean_single_supplier(raw_supplier)
        
        assert cleaned["id"] == "supplier_001"
        assert cleaned["name"] == "Test Supplier"
        assert cleaned["country"] == "Germany"
        assert cleaned["industry"] == "Technology"
        assert cleaned["esg_score"] == 0.85
        assert cleaned["financial_stability"] == 0.8
        assert cleaned["prior_violations"] == 0
        assert cleaned["annual_spend"] == 1000000.0
        assert cleaned["contract_duration"] == 3
        assert cleaned["risk_level"] == "low"
    
    def test_validate_supplier_data(self, parser):
        """Test supplier data validation."""
        suppliers = [
            {
                "id": "supplier_001",
                "name": "Valid Supplier",
                "country": "Germany",
                "industry": "Technology",
                "esg_score": 0.85,
                "financial_stability": 0.8
            },
            {
                "id": "supplier_002",
                "name": "Invalid Supplier",
                "country": "Germany",
                "industry": "Technology",
                "esg_score": 1.5,  # Invalid score
                "financial_stability": 0.8
            }
        ]
        
        validation = parser.validate_supplier_data(suppliers)
        
        assert validation["valid"] is False
        assert validation["total_suppliers"] == 2
        assert len(validation["errors"]) > 0
        assert "Invalid ESG score" in validation["errors"][0]


if __name__ == "__main__":
    pytest.main([__file__]) 