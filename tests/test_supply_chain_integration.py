"""
Integration tests for supply chain audit functionality.
"""

import pytest
import asyncio
import json
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, List

from orchestrator.utils.supplier_parser import SupplierDataParser
from orchestrator.agents.supply_chain_agents import (
    InternalRetrieverAgent, ExternalRetrieverAgent,
    RiskAnalysisAgent, ESGComplianceAgent
)
from orchestrator.models.task import Task, TaskType


class TestSupplyChainIntegration:
    """Integration tests for supply chain audit workflow."""
    
    @pytest.fixture
    def sample_suppliers_data(self):
        """Create sample suppliers data for testing."""
        return [
            {
                "id": "supplier_001",
                "name": "GreenTech Solutions",
                "country": "Germany",
                "industry": "Technology",
                "supplier_type": "Tier 1",
                "esg_score": 0.85,
                "financial_stability": 0.8,
                "prior_violations": 0,
                "supply_category": "Renewable Energy",
                "annual_spend": 1800000,
                "contract_duration": 5,
                "risk_level": "low"
            },
            {
                "id": "supplier_002",
                "name": "Chemical Solutions Ltd",
                "country": "China",
                "industry": "Chemicals",
                "supplier_type": "Tier 2",
                "esg_score": 0.20,
                "financial_stability": 0.3,
                "prior_violations": 8,
                "supply_category": "Chemicals",
                "annual_spend": 2800000,
                "contract_duration": 1,
                "risk_level": "critical"
            },
            {
                "id": "supplier_003",
                "name": "Steel Dynamics",
                "country": "Ukraine",
                "industry": "Steel",
                "supplier_type": "Tier 2",
                "esg_score": 0.15,
                "financial_stability": 0.2,
                "prior_violations": 12,
                "supply_category": "Metals",
                "annual_spend": 4100000,
                "contract_duration": 2,
                "risk_level": "critical"
            },
            {
                "id": "supplier_004",
                "name": "Organic Foods Co",
                "country": "Canada",
                "industry": "Agriculture",
                "supplier_type": "Tier 1",
                "esg_score": 0.80,
                "financial_stability": 0.7,
                "prior_violations": 0,
                "supply_category": "Food & Beverage",
                "annual_spend": 800000,
                "contract_duration": 4,
                "risk_level": "low"
            },
            {
                "id": "supplier_005",
                "name": "Textile Mills Ltd",
                "country": "Bangladesh",
                "industry": "Textiles",
                "supplier_type": "Tier 2",
                "esg_score": 0.20,
                "financial_stability": 0.3,
                "prior_violations": 7,
                "supply_category": "Apparel",
                "annual_spend": 1100000,
                "contract_duration": 1,
                "risk_level": "critical"
            }
        ]
    
    @pytest.fixture
    def temp_suppliers_file(self, sample_suppliers_data):
        """Create a temporary suppliers CSV file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            # Write header
            f.write("id,name,country,industry,supplier_type,esg_score,financial_stability,prior_violations,supply_category,annual_spend,contract_duration,risk_level\n")
            
            # Write data
            for supplier in sample_suppliers_data:
                f.write(f"{supplier['id']},{supplier['name']},{supplier['country']},{supplier['industry']},{supplier['supplier_type']},{supplier['esg_score']},{supplier['financial_stability']},{supplier['prior_violations']},{supplier['supply_category']},{supplier['annual_spend']},{supplier['contract_duration']},{supplier['risk_level']}\n")
        
        yield f.name
        
        # Cleanup
        os.unlink(f.name)
    
    @pytest.fixture
    def agent_configs(self):
        """Create agent configurations for testing."""
        return {
            "internal_retriever": {
                "data_sources": ["temp_suppliers.csv"],
                "top_k": 10,
                "similarity_threshold": 0.7
            },
            "external_retriever": {
                "data_sources": ["data/external/"],
                "api_endpoints": ["country_esg_ratings", "violation_database"],
                "top_k": 15,
                "similarity_threshold": 0.6
            },
            "risk_analysis": {
                "risk_factors": {
                    "country_esg_rating": {"weight": 0.25, "threshold": 0.6},
                    "prior_violations": {"weight": 0.30, "threshold": 0.7},
                    "supply_category_risk": {"weight": 0.20, "threshold": 0.5},
                    "financial_stability": {"weight": 0.25, "threshold": 0.6}
                },
                "composite_risk_threshold": 0.65
            },
            "esg_compliance": {
                "compliance_frameworks": ["EU_CSDDD", "ISO_14001", "SA8000"],
                "risk_categories": {
                    "environmental": ["carbon_emissions", "water_usage", "waste_management"],
                    "social": ["labor_rights", "human_rights", "health_safety"],
                    "governance": ["corruption", "transparency", "board_diversity"]
                }
            }
        }
    
    @pytest.mark.asyncio
    async def test_end_to_end_supply_chain_audit(self, temp_suppliers_file, agent_configs):
        """Test complete supply chain audit workflow."""
        print(f"\n🔍 Running end-to-end supply chain audit test")
        print(f"📁 Using suppliers file: {temp_suppliers_file}")
        
        # Step 1: Parse supplier data
        print("\n1. Parsing supplier data...")
        parser = SupplierDataParser()
        
        # Update the config to use the temp file
        agent_configs["internal_retriever"]["data_sources"] = [temp_suppliers_file]
        
        suppliers = parser.parse_suppliers(temp_suppliers_file)
        assert len(suppliers) == 5, f"Expected 5 suppliers, got {len(suppliers)}"
        
        validation = parser.validate_supplier_data(suppliers)
        assert validation["valid"] is True, f"Data validation failed: {validation['errors']}"
        
        print(f"✅ Parsed {len(suppliers)} suppliers successfully")
        
        # Step 2: Initialize agents
        print("\n2. Initializing agents...")
        internal_retriever = InternalRetrieverAgent(agent_configs["internal_retriever"])
        external_retriever = ExternalRetrieverAgent(agent_configs["external_retriever"])
        risk_analyzer = RiskAnalysisAgent(agent_configs["risk_analysis"])
        esg_compliance = ESGComplianceAgent(agent_configs["esg_compliance"])
        
        print("✅ All agents initialized")
        
        # Step 3: Execute analysis pipeline
        print("\n3. Executing analysis pipeline...")
        
        # 3.1 Internal data retrieval
        print("  3.1 Internal data retrieval...")
        internal_task = Task(
            type=TaskType.RETRIEVE,
            payload={"query": "Assess ESG and compliance risks for suppliers"},
            sender="test"
        )
        
        internal_result = await internal_retriever.process_task(internal_task)
        assert internal_result.success is True, f"Internal retrieval failed: {internal_result.error}"
        assert internal_result.data["filtered_count"] == 5
        
        print(f"   ✅ Retrieved {internal_result.data['filtered_count']} suppliers")
        
        # 3.2 External data retrieval
        print("  3.2 External data retrieval...")
        external_task = Task(
            type=TaskType.RETRIEVE,
            payload={"query": "Retrieve ESG and compliance data"},
            sender="test"
        )
        
        external_result = await external_retriever.process_task(external_task)
        assert external_result.success is True, f"External retrieval failed: {external_result.error}"
        
        print(f"   ✅ Retrieved external data from {len(external_result.data['data_sources'])} sources")
        
        # 3.3 Risk analysis
        print("  3.3 Risk analysis...")
        risk_task = Task(
            type=TaskType.ANALYZE,
            payload={
                "suppliers": internal_result.data["suppliers"],
                "external_data": external_result.data["external_data"]
            },
            sender="test"
        )
        
        risk_result = await risk_analyzer.process_task(risk_task)
        assert risk_result.success is True, f"Risk analysis failed: {risk_result.error}"
        
        risk_analysis = risk_result.data["risk_analysis"]
        high_risk_suppliers = risk_result.data["high_risk_suppliers"]
        
        assert len(risk_analysis) == 5, f"Expected 5 risk analyses, got {len(risk_analysis)}"
        
        print(f"   ✅ Analyzed {len(risk_analysis)} suppliers")
        print(f"   🚨 Found {len(high_risk_suppliers)} high-risk suppliers")
        
        # 3.4 ESG compliance assessment
        print("  3.4 ESG compliance assessment...")
        compliance_task = Task(
            type=TaskType.COMPLIANCE_CHECK,
            payload={
                "suppliers": internal_result.data["suppliers"],
                "external_data": external_result.data["external_data"]
            },
            sender="test"
        )
        
        compliance_result = await esg_compliance.process_task(compliance_task)
        assert compliance_result.success is True, f"Compliance assessment failed: {compliance_result.error}"
        
        compliance_assessment = compliance_result.data["compliance_assessment"]
        non_compliant_suppliers = compliance_result.data["non_compliant_suppliers"]
        
        assert len(compliance_assessment) == 5, f"Expected 5 compliance assessments, got {len(compliance_assessment)}"
        
        print(f"   ✅ Assessed {len(compliance_assessment)} suppliers")
        print(f"   ⚠️  Found {len(non_compliant_suppliers)} non-compliant suppliers")
        
        # Step 4: Validate results
        print("\n4. Validating results...")
        
        # Check that high-risk suppliers are correctly identified
        expected_high_risk = ["Chemical Solutions Ltd", "Steel Dynamics", "Textile Mills Ltd"]
        actual_high_risk = [s["supplier_name"] for s in high_risk_suppliers]
        
        for expected in expected_high_risk:
            assert expected in actual_high_risk, f"Expected high-risk supplier {expected} not found"
        
        print(f"   ✅ High-risk suppliers correctly identified: {actual_high_risk}")
        
        # Check risk levels
        risk_levels = {}
        for analysis in risk_analysis:
            supplier_name = analysis["supplier_name"]
            risk_level = analysis["risk_level"]
            risk_levels[supplier_name] = risk_level
        
        # Verify specific suppliers have expected risk levels
        assert risk_levels["GreenTech Solutions"] == "low", "GreenTech should be low risk"
        assert risk_levels["Chemical Solutions Ltd"] in ["high", "critical"], "Chemical Solutions should be high/critical risk"
        assert risk_levels["Steel Dynamics"] in ["high", "critical"], "Steel Dynamics should be high/critical risk"
        
        print(f"   ✅ Risk levels correctly assigned")
        
        # Check compliance results
        compliant_suppliers = [s for s in compliance_assessment if s["overall_compliant"]]
        non_compliant_suppliers = [s for s in compliance_assessment if not s["overall_compliant"]]
        
        # Should have some compliant and some non-compliant suppliers
        assert len(compliant_suppliers) > 0, "Should have at least one compliant supplier"
        assert len(non_compliant_suppliers) > 0, "Should have at least one non-compliant supplier"
        
        print(f"   ✅ Compliance assessment completed: {len(compliant_suppliers)} compliant, {len(non_compliant_suppliers)} non-compliant")
        
        # Step 5: Generate and validate report
        print("\n5. Generating report...")
        
        report = self._generate_test_report(
            suppliers=internal_result.data["suppliers"],
            risk_analysis=risk_analysis,
            compliance_assessment=compliance_assessment,
            external_data=external_result.data["external_data"]
        )
        
        # Validate report structure
        assert "metadata" in report
        assert "executive_summary" in report
        assert "risk_assessment" in report
        assert "compliance_analysis" in report
        assert "supplier_details" in report
        
        # Validate executive summary
        summary = report["executive_summary"]
        assert summary["total_suppliers_analyzed"] == 5
        assert summary["high_risk_suppliers"] >= 2  # Should have at least 2 high-risk suppliers
        assert summary["compliance_rate"] < 1.0  # Should have some non-compliant suppliers
        
        print(f"   ✅ Report generated successfully")
        print(f"   📊 Executive Summary:")
        print(f"      - Total suppliers: {summary['total_suppliers_analyzed']}")
        print(f"      - High-risk suppliers: {summary['high_risk_suppliers']}")
        print(f"      - Non-compliant suppliers: {summary['total_suppliers_analyzed'] - int(summary['total_suppliers_analyzed'] * summary['compliance_rate'])}")
        print(f"      - Overall risk score: {summary['overall_risk_score']:.2f}")
        print(f"      - Compliance rate: {summary['compliance_rate']:.1%}")
        
        # Step 6: Test report export
        print("\n6. Testing report export...")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(report, f, indent=2, default=str)
            report_file = f.name
        
        # Verify file was created and contains valid JSON
        with open(report_file, 'r') as f:
            exported_report = json.load(f)
        
        assert exported_report["metadata"]["total_suppliers"] == 5
        assert len(exported_report["supplier_details"]) == 5
        
        print(f"   ✅ Report exported to {report_file}")
        
        # Cleanup
        os.unlink(report_file)
        
        print("\n🎉 End-to-end supply chain audit test completed successfully!")
    
    def _generate_test_report(self, suppliers, risk_analysis, compliance_assessment, external_data):
        """Generate a test report from analysis results."""
        report = {
            "metadata": {
                "report_type": "supply_chain_risk_audit",
                "generated_at": "2024-01-01T00:00:00",
                "total_suppliers": len(suppliers),
                "analysis_version": "1.0.0"
            },
            "executive_summary": {
                "total_suppliers_analyzed": len(suppliers),
                "high_risk_suppliers": len([s for s in risk_analysis if s['risk_level'] in ['high', 'critical']]),
                "non_compliant_suppliers": len([s for s in compliance_assessment if not s['overall_compliant']]),
                "overall_risk_score": sum(s['composite_risk_score'] for s in risk_analysis) / len(risk_analysis),
                "compliance_rate": len([s for s in compliance_assessment if s['overall_compliant']]) / len(compliance_assessment)
            },
            "risk_assessment": {
                "risk_distribution": {},
                "high_risk_suppliers": [],
                "risk_factors_analysis": {}
            },
            "compliance_analysis": {
                "compliance_summary": {
                    "environmental": {"compliant": 0, "non_compliant": 0},
                    "social": {"compliant": 0, "non_compliant": 0},
                    "governance": {"compliant": 0, "non_compliant": 0}
                },
                "non_compliant_suppliers": []
            },
            "supplier_details": []
        }
        
        # Risk distribution
        for analysis in risk_analysis:
            risk_level = analysis['risk_level']
            report["risk_assessment"]["risk_distribution"][risk_level] = \
                report["risk_assessment"]["risk_distribution"].get(risk_level, 0) + 1
        
        # High-risk suppliers
        high_risk = [s for s in risk_analysis if s['risk_level'] in ['high', 'critical']]
        report["risk_assessment"]["high_risk_suppliers"] = [
            {
                "supplier_id": s['supplier_id'],
                "supplier_name": s['supplier_name'],
                "country": s['country'],
                "risk_score": s['composite_risk_score'],
                "risk_level": s['risk_level']
            }
            for s in high_risk
        ]
        
        # Compliance summary
        for assessment in compliance_assessment:
            for category in ["environmental", "social", "governance"]:
                if assessment[category]["compliant"]:
                    report["compliance_analysis"]["compliance_summary"][category]["compliant"] += 1
                else:
                    report["compliance_analysis"]["compliance_summary"][category]["non_compliant"] += 1
        
        # Non-compliant suppliers
        non_compliant = [s for s in compliance_assessment if not s['overall_compliant']]
        report["compliance_analysis"]["non_compliant_suppliers"] = [
            {
                "supplier_id": s['supplier_id'],
                "supplier_name": s['supplier_name'],
                "country": s['country'],
                "compliance_score": s['compliance_score']
            }
            for s in non_compliant
        ]
        
        # Supplier details
        for i, supplier in enumerate(suppliers):
            risk_info = next((r for r in risk_analysis if r['supplier_id'] == supplier['id']), None)
            compliance_info = next((c for c in compliance_assessment if c['supplier_id'] == supplier['id']), None)
            
            report["supplier_details"].append({
                "supplier_id": supplier['id'],
                "supplier_name": supplier['name'],
                "country": supplier['country'],
                "industry": supplier['industry'],
                "risk_analysis": risk_info,
                "compliance_assessment": compliance_info
            })
        
        return report
    
    @pytest.mark.asyncio
    async def test_supplier_data_validation(self, temp_suppliers_file):
        """Test supplier data validation functionality."""
        print(f"\n🔍 Testing supplier data validation")
        
        parser = SupplierDataParser()
        suppliers = parser.parse_suppliers(temp_suppliers_file)
        validation = parser.validate_supplier_data(suppliers)
        
        # Should be valid
        assert validation["valid"] is True
        
        # Should have correct statistics
        assert validation["total_suppliers"] == 5
        assert len(validation["countries"]) == 5  # 5 different countries
        assert len(validation["industries"]) == 5  # 5 different industries
        assert len(validation["supplier_types"]) == 2  # Tier 1 and Tier 2
        assert len(validation["risk_levels"]) == 3  # low, critical
        
        print(f"✅ Data validation passed")
        print(f"   - Countries: {validation['countries']}")
        print(f"   - Industries: {validation['industries']}")
        print(f"   - Supplier types: {validation['supplier_types']}")
        print(f"   - Risk levels: {validation['risk_levels']}")
    
    @pytest.mark.asyncio
    async def test_risk_analysis_accuracy(self, temp_suppliers_file, agent_configs):
        """Test risk analysis accuracy with known data."""
        print(f"\n🔍 Testing risk analysis accuracy")
        
        # Parse data
        parser = SupplierDataParser()
        suppliers = parser.parse_suppliers(temp_suppliers_file)
        
        # Initialize agents
        agent_configs["internal_retriever"]["data_sources"] = [temp_suppliers_file]
        internal_retriever = InternalRetrieverAgent(agent_configs["internal_retriever"])
        external_retriever = ExternalRetrieverAgent(agent_configs["external_retriever"])
        risk_analyzer = RiskAnalysisAgent(agent_configs["risk_analysis"])
        
        # Get data
        internal_task = Task(type=TaskType.RETRIEVE, payload={"query": "test"}, sender="test")
        internal_result = await internal_retriever.process_task(internal_task)
        
        external_task = Task(type=TaskType.RETRIEVE, payload={"query": "test"}, sender="test")
        external_result = await external_retriever.process_task(external_task)
        
        # Analyze risks
        risk_task = Task(
            type=TaskType.ANALYZE,
            payload={
                "suppliers": internal_result.data["suppliers"],
                "external_data": external_result.data["external_data"]
            },
            sender="test"
        )
        
        risk_result = await risk_analyzer.process_task(risk_task)
        risk_analysis = risk_result.data["risk_analysis"]
        
        # Test specific expectations
        for analysis in risk_analysis:
            supplier_name = analysis["supplier_name"]
            
            if supplier_name == "GreenTech Solutions":
                # Should be low risk due to high ESG score and no violations
                assert analysis["risk_level"] == "low", f"GreenTech should be low risk, got {analysis['risk_level']}"
                assert analysis["composite_risk_score"] < 0.4, f"GreenTech should have low risk score, got {analysis['composite_risk_score']}"
            
            elif supplier_name == "Chemical Solutions Ltd":
                # Should be high/critical risk due to low ESG score and many violations
                assert analysis["risk_level"] in ["high", "critical"], f"Chemical Solutions should be high/critical risk, got {analysis['risk_level']}"
                assert analysis["composite_risk_score"] > 0.6, f"Chemical Solutions should have high risk score, got {analysis['composite_risk_score']}"
            
            elif supplier_name == "Steel Dynamics":
                # Should be high/critical risk due to sanctions and violations
                assert analysis["risk_level"] in ["high", "critical"], f"Steel Dynamics should be high/critical risk, got {analysis['risk_level']}"
                assert analysis["composite_risk_score"] > 0.6, f"Steel Dynamics should have high risk score, got {analysis['composite_risk_score']}"
        
        print(f"✅ Risk analysis accuracy validated")
        print(f"   - GreenTech Solutions: {next(s['risk_level'] for s in risk_analysis if s['supplier_name'] == 'GreenTech Solutions')}")
        print(f"   - Chemical Solutions Ltd: {next(s['risk_level'] for s in risk_analysis if s['supplier_name'] == 'Chemical Solutions Ltd')}")
        print(f"   - Steel Dynamics: {next(s['risk_level'] for s in risk_analysis if s['supplier_name'] == 'Steel Dynamics')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 