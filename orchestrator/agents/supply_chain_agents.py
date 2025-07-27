"""
Supply Chain specific agents for ESG and compliance risk assessment.
"""

import asyncio
import json
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base import BaseAgent
from ..models.task import Task, TaskResult, TaskStatus
from ..utils.logging import logger


class InternalRetrieverAgent(BaseAgent):
    """Agent for retrieving internal supplier data."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.data_sources = config.get("data_sources", [])
        self.top_k = config.get("top_k", 10)
        self.similarity_threshold = config.get("similarity_threshold", 0.7)
    
    async def process_task(self, task: Task) -> TaskResult:
        """Process supplier data retrieval task."""
        try:
            logger.info(f"InternalRetrieverAgent processing task: {task.id}")
            
            # Load supplier data
            suppliers_data = await self._load_supplier_data()
            
            # Filter and rank suppliers based on query
            query = task.payload.get("query", "")
            filtered_suppliers = await self._filter_suppliers(suppliers_data, query)
            
            result_data = {
                "suppliers": filtered_suppliers,
                "total_suppliers": len(suppliers_data),
                "filtered_count": len(filtered_suppliers),
                "data_source": "internal_supplier_database"
            }
            
            return TaskResult(
                task_id=task.id,
                success=True,
                data=result_data
            )
            
        except Exception as e:
            logger.error(f"Error in InternalRetrieverAgent: {e}")
            return TaskResult(
                task_id=task.id,
                success=False,
                error=str(e)
            )
    
    async def _load_supplier_data(self) -> List[Dict[str, Any]]:
        """Load supplier data from CSV file."""
        try:
            suppliers_file = self.data_sources[0] if self.data_sources else "data/suppliers.csv"
            df = pd.read_csv(suppliers_file)
            
            # Convert DataFrame to list of dictionaries
            suppliers = df.to_dict('records')
            
            logger.info(f"Loaded {len(suppliers)} suppliers from {suppliers_file}")
            return suppliers
            
        except Exception as e:
            logger.error(f"Error loading supplier data: {e}")
            return []
    
    async def _filter_suppliers(self, suppliers: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Filter suppliers based on query criteria."""
        # For MVP, return all suppliers
        # In production, implement semantic search or filtering logic
        return suppliers[:self.top_k]


class ExternalRetrieverAgent(BaseAgent):
    """Agent for retrieving external ESG and compliance data."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.data_sources = config.get("data_sources", [])
        self.api_endpoints = config.get("api_endpoints", [])
        self.top_k = config.get("top_k", 15)
        self.similarity_threshold = config.get("similarity_threshold", 0.6)
    
    async def process_task(self, task: Task) -> TaskResult:
        """Process external data retrieval task."""
        try:
            logger.info(f"ExternalRetrieverAgent processing task: {task.id}")
            
            # Retrieve external data
            external_data = await self._retrieve_external_data()
            
            result_data = {
                "external_data": external_data,
                "data_sources": self.data_sources,
                "api_endpoints": self.api_endpoints,
                "retrieved_count": len(external_data)
            }
            
            return TaskResult(
                task_id=task.id,
                success=True,
                data=result_data
            )
            
        except Exception as e:
            logger.error(f"Error in ExternalRetrieverAgent: {e}")
            return TaskResult(
                task_id=task.id,
                success=False,
                error=str(e)
            )
    
    async def _retrieve_external_data(self) -> Dict[str, Any]:
        """Retrieve external ESG and compliance data."""
        # Mock external data for MVP
        # In production, implement actual API calls and document retrieval
        
        external_data = {
            "country_esg_ratings": {
                "Germany": 0.85,
                "Denmark": 0.90,
                "Canada": 0.80,
                "USA": 0.75,
                "Israel": 0.80,
                "Thailand": 0.60,
                "Mexico": 0.65,
                "India": 0.55,
                "Malaysia": 0.65,
                "Turkey": 0.50,
                "Argentina": 0.45,
                "Brazil": 0.40,
                "Vietnam": 0.45,
                "China": 0.35,
                "Russia": 0.25,
                "Ukraine": 0.20,
                "Iran": 0.15,
                "Bangladesh": 0.30
            },
            "sanction_lists": [
                {"entity": "Chemical Manufacturing", "country": "Iran", "reason": "Trade sanctions"},
                {"entity": "Steel Dynamics", "country": "Ukraine", "reason": "Conflict zone"},
                {"entity": "MetalCorp Industries", "country": "Russia", "reason": "Trade restrictions"}
            ],
            "violation_database": {
                "Chemical Solutions Ltd": ["Environmental violations", "Safety violations"],
                "Textile Mills Ltd": ["Labor violations", "Safety violations"],
                "Chemical Manufacturing": ["Sanctions violations", "Environmental violations"],
                "Steel Dynamics": ["Trade violations", "Safety violations"]
            },
            "sustainability_reports": {
                "GreenTech Solutions": {"rating": 0.85, "certifications": ["ISO_14001", "GRI_Standards"]},
                "Clean Energy Systems": {"rating": 0.90, "certifications": ["ISO_14001", "SA8000"]},
                "Organic Foods Co": {"rating": 0.80, "certifications": ["Organic", "Fair Trade"]}
            }
        }
        
        return external_data


class RiskAnalysisAgent(BaseAgent):
    """Agent for analyzing supply chain risks."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.risk_factors = config.get("risk_factors", {})
        self.composite_risk_threshold = config.get("composite_risk_threshold", 0.65)
    
    async def process_task(self, task: Task) -> TaskResult:
        """Process risk analysis task."""
        try:
            logger.info(f"RiskAnalysisAgent processing task: {task.id}")
            
            # Extract data from previous tasks
            suppliers_data = task.payload.get("suppliers", [])
            external_data = task.payload.get("external_data", {})
            
            # Analyze risks for each supplier
            risk_analysis = await self._analyze_supplier_risks(suppliers_data, external_data)
            
            result_data = {
                "risk_analysis": risk_analysis,
                "risk_factors": self.risk_factors,
                "composite_risk_threshold": self.composite_risk_threshold,
                "high_risk_suppliers": [s for s in risk_analysis if s["composite_risk_score"] >= self.composite_risk_threshold]
            }
            
            return TaskResult(
                task_id=task.id,
                success=True,
                data=result_data
            )
            
        except Exception as e:
            logger.error(f"Error in RiskAnalysisAgent: {e}")
            return TaskResult(
                task_id=task.id,
                success=False,
                error=str(e)
            )
    
    async def _analyze_supplier_risks(self, suppliers: List[Dict[str, Any]], external_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze risks for each supplier."""
        risk_analysis = []
        
        for supplier in suppliers:
            # Calculate individual risk factors
            country_esg_risk = self._calculate_country_esg_risk(supplier, external_data)
            violation_risk = self._calculate_violation_risk(supplier, external_data)
            category_risk = self._calculate_category_risk(supplier)
            financial_risk = self._calculate_financial_risk(supplier)
            
            # Calculate composite risk score
            composite_score = (
                country_esg_risk * self.risk_factors.get("country_esg_rating", {}).get("weight", 0.25) +
                violation_risk * self.risk_factors.get("prior_violations", {}).get("weight", 0.30) +
                category_risk * self.risk_factors.get("supply_category_risk", {}).get("weight", 0.20) +
                financial_risk * self.risk_factors.get("financial_stability", {}).get("weight", 0.25)
            )
            
            # Determine risk level
            risk_level = self._determine_risk_level(composite_score)
            
            risk_analysis.append({
                "supplier_id": supplier["id"],
                "supplier_name": supplier["name"],
                "country": supplier["country"],
                "industry": supplier["industry"],
                "risk_factors": {
                    "country_esg_rating": country_esg_risk,
                    "prior_violations": violation_risk,
                    "supply_category_risk": category_risk,
                    "financial_stability": financial_risk
                },
                "composite_risk_score": composite_score,
                "risk_level": risk_level,
                "flags": self._generate_risk_flags(supplier, external_data)
            })
        
        return risk_analysis
    
    def _calculate_country_esg_risk(self, supplier: Dict[str, Any], external_data: Dict[str, Any]) -> float:
        """Calculate country ESG risk score."""
        country = supplier["country"]
        country_ratings = external_data.get("country_esg_ratings", {})
        
        # Get country rating, default to 0.5 if not found
        country_rating = country_ratings.get(country, 0.5)
        
        # Convert to risk score (higher rating = lower risk)
        return 1.0 - country_rating
    
    def _calculate_violation_risk(self, supplier: Dict[str, Any], external_data: Dict[str, Any]) -> float:
        """Calculate violation risk score."""
        supplier_name = supplier["name"]
        prior_violations = supplier.get("prior_violations", 0)
        violation_db = external_data.get("violation_database", {})
        
        # Base risk from prior violations
        base_risk = min(prior_violations / 10.0, 1.0)
        
        # Additional risk from violation database
        db_violations = violation_db.get(supplier_name, [])
        db_risk = len(db_violations) * 0.2
        
        return min(base_risk + db_risk, 1.0)
    
    def _calculate_category_risk(self, supplier: Dict[str, Any]) -> float:
        """Calculate supply category risk score."""
        category = supplier.get("supply_category", "")
        
        # Risk categories (higher risk categories)
        high_risk_categories = ["Chemicals", "Mining", "Steel", "Metals"]
        medium_risk_categories = ["Textiles", "Plastics", "Construction", "Forestry"]
        
        if category in high_risk_categories:
            return 0.8
        elif category in medium_risk_categories:
            return 0.5
        else:
            return 0.3
    
    def _calculate_financial_risk(self, supplier: Dict[str, Any]) -> float:
        """Calculate financial stability risk score."""
        financial_stability = supplier.get("financial_stability", 0.5)
        
        # Convert to risk score (higher stability = lower risk)
        return 1.0 - financial_stability
    
    def _determine_risk_level(self, composite_score: float) -> str:
        """Determine risk level based on composite score."""
        if composite_score >= 0.8:
            return "critical"
        elif composite_score >= 0.6:
            return "high"
        elif composite_score >= 0.3:
            return "medium"
        else:
            return "low"
    
    def _generate_risk_flags(self, supplier: Dict[str, Any], external_data: Dict[str, Any]) -> List[str]:
        """Generate risk flags for the supplier."""
        flags = []
        
        # Check sanctions
        sanction_lists = external_data.get("sanction_lists", [])
        for sanction in sanction_lists:
            if (sanction["entity"] == supplier["name"] or 
                sanction["country"] == supplier["country"]):
                flags.append(f"Sanctioned: {sanction['reason']}")
        
        # Check violations
        violation_db = external_data.get("violation_database", {})
        if supplier["name"] in violation_db:
            flags.append(f"Violations: {', '.join(violation_db[supplier['name']])}")
        
        # Check ESG score
        if supplier.get("esg_score", 1.0) < 0.3:
            flags.append("Low ESG Score")
        
        # Check financial stability
        if supplier.get("financial_stability", 1.0) < 0.4:
            flags.append("Financial Instability")
        
        return flags


class ESGComplianceAgent(BaseAgent):
    """Agent for ESG compliance assessment."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.compliance_frameworks = config.get("compliance_frameworks", [])
        self.risk_categories = config.get("risk_categories", {})
    
    async def process_task(self, task: Task) -> TaskResult:
        """Process ESG compliance assessment task."""
        try:
            logger.info(f"ESGComplianceAgent processing task: {task.id}")
            
            # Extract data from previous tasks
            suppliers_data = task.payload.get("suppliers", [])
            external_data = task.payload.get("external_data", {})
            
            # Assess compliance for each supplier
            compliance_assessment = await self._assess_compliance(suppliers_data, external_data)
            
            result_data = {
                "compliance_assessment": compliance_assessment,
                "compliance_frameworks": self.compliance_frameworks,
                "risk_categories": self.risk_categories,
                "non_compliant_suppliers": [s for s in compliance_assessment if not s["overall_compliant"]]
            }
            
            return TaskResult(
                task_id=task.id,
                success=True,
                data=result_data
            )
            
        except Exception as e:
            logger.error(f"Error in ESGComplianceAgent: {e}")
            return TaskResult(
                task_id=task.id,
                success=False,
                error=str(e)
            )
    
    async def _assess_compliance(self, suppliers: List[Dict[str, Any]], external_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Assess ESG compliance for each supplier."""
        compliance_assessment = []
        
        for supplier in suppliers:
            # Assess each ESG category
            environmental_compliance = self._assess_environmental_compliance(supplier, external_data)
            social_compliance = self._assess_social_compliance(supplier, external_data)
            governance_compliance = self._assess_governance_compliance(supplier, external_data)
            
            # Overall compliance assessment
            overall_compliant = (
                environmental_compliance["compliant"] and
                social_compliance["compliant"] and
                governance_compliance["compliant"]
            )
            
            compliance_assessment.append({
                "supplier_id": supplier["id"],
                "supplier_name": supplier["name"],
                "country": supplier["country"],
                "industry": supplier["industry"],
                "environmental": environmental_compliance,
                "social": social_compliance,
                "governance": governance_compliance,
                "overall_compliant": overall_compliant,
                "compliance_score": self._calculate_compliance_score(
                    environmental_compliance, social_compliance, governance_compliance
                ),
                "recommendations": self._generate_compliance_recommendations(
                    environmental_compliance, social_compliance, governance_compliance
                )
            })
        
        return compliance_assessment
    
    def _assess_environmental_compliance(self, supplier: Dict[str, Any], external_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess environmental compliance."""
        issues = []
        compliant = True
        
        # Check ESG score
        esg_score = supplier.get("esg_score", 0.5)
        if esg_score < 0.4:
            issues.append("Low environmental performance score")
            compliant = False
        
        # Check industry-specific risks
        industry = supplier.get("industry", "")
        if industry in ["Chemicals", "Mining", "Steel"]:
            issues.append("High environmental impact industry")
            compliant = False
        
        # Check country environmental regulations
        country = supplier["country"]
        if country in ["China", "Russia", "Iran"]:
            issues.append("Country with weak environmental regulations")
            compliant = False
        
        return {
            "compliant": compliant,
            "issues": issues,
            "score": esg_score,
            "framework": "ISO_14001"
        }
    
    def _assess_social_compliance(self, supplier: Dict[str, Any], external_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess social compliance."""
        issues = []
        compliant = True
        
        # Check for labor violations
        violation_db = external_data.get("violation_database", {})
        if supplier["name"] in violation_db:
            violations = violation_db[supplier["name"]]
            if "Labor violations" in violations:
                issues.append("Labor rights violations detected")
                compliant = False
        
        # Check country labor standards
        country = supplier["country"]
        if country in ["Bangladesh", "Vietnam", "China"]:
            issues.append("Country with labor rights concerns")
            compliant = False
        
        # Check supplier type
        supplier_type = supplier.get("supplier_type", "")
        if supplier_type == "Tier 2":
            issues.append("Tier 2 supplier - limited visibility into labor practices")
            compliant = False
        
        return {
            "compliant": compliant,
            "issues": issues,
            "score": 0.7 if compliant else 0.3,
            "framework": "SA8000"
        }
    
    def _assess_governance_compliance(self, supplier: Dict[str, Any], external_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess governance compliance."""
        issues = []
        compliant = True
        
        # Check for sanctions
        sanction_lists = external_data.get("sanction_lists", [])
        for sanction in sanction_lists:
            if (sanction["entity"] == supplier["name"] or 
                sanction["country"] == supplier["country"]):
                issues.append(f"Sanctioned entity: {sanction['reason']}")
                compliant = False
        
        # Check financial stability
        financial_stability = supplier.get("financial_stability", 0.5)
        if financial_stability < 0.4:
            issues.append("Financial instability - governance concerns")
            compliant = False
        
        # Check transparency
        if supplier.get("esg_score", 0.5) < 0.3:
            issues.append("Low transparency in ESG reporting")
            compliant = False
        
        return {
            "compliant": compliant,
            "issues": issues,
            "score": financial_stability,
            "framework": "EU_CSDDD"
        }
    
    def _calculate_compliance_score(self, environmental: Dict[str, Any], social: Dict[str, Any], governance: Dict[str, Any]) -> float:
        """Calculate overall compliance score."""
        return (environmental["score"] + social["score"] + governance["score"]) / 3.0
    
    def _generate_compliance_recommendations(self, environmental: Dict[str, Any], social: Dict[str, Any], governance: Dict[str, Any]) -> List[str]:
        """Generate compliance recommendations."""
        recommendations = []
        
        if not environmental["compliant"]:
            recommendations.append("Implement environmental management system (ISO 14001)")
            recommendations.append("Conduct environmental impact assessment")
        
        if not social["compliant"]:
            recommendations.append("Implement social responsibility program (SA8000)")
            recommendations.append("Conduct labor rights audit")
        
        if not governance["compliant"]:
            recommendations.append("Implement corporate governance framework")
            recommendations.append("Conduct due diligence assessment")
        
        if not recommendations:
            recommendations.append("Maintain current compliance standards")
        
        return recommendations 