"""
Compliance agent for checking patterns against AML regulations.
"""

from typing import Dict, Any, List
from ..models.task import Task, TaskResult, TaskType
from ..models.report import ComplianceCheck, ComplianceStatus
from ..config.settings import settings
from ..utils.logging import async_logger
from .base import BaseAgent


class ComplianceAgent(BaseAgent):
    """Agent responsible for compliance checking against AML regulations."""
    
    def __init__(self, name: str = "compliance"):
        """Initialize the compliance agent."""
        super().__init__(name)
        self.system_prompt = """
        You are a compliance officer specializing in anti-money laundering (AML) regulations.
        Your role is to evaluate suspicious patterns against relevant regulations and provide
        compliance assessments with justifications and recommended actions.
        
        Key regulations to consider:
        - Bank Secrecy Act (BSA)
        - USA PATRIOT Act
        - OFAC Sanctions
        - Local AML regulations
        
        Always provide clear justifications for your compliance decisions.
        """
    
    async def process_task(self, task: Task) -> TaskResult:
        """Process a compliance check task."""
        try:
            suspicious_patterns = task.payload.get("suspicious_patterns", [])
            regulations = task.payload.get("regulations", ["BSA", "PATRIOT_Act", "OFAC"])
            risk_assessment = task.payload.get("risk_assessment", True)
            
            if not suspicious_patterns:
                return TaskResult(
                    task_id=task.id,
                    success=True,
                    data={"compliance_checks": [], "summary": "No suspicious patterns to check"},
                    agent_name=self.name
                )
            
            compliance_checks = []
            
            for pattern in suspicious_patterns:
                check = await self._check_pattern_compliance(pattern, regulations, risk_assessment)
                compliance_checks.append(check)
            
            # Create summary
            summary = self._create_compliance_summary(compliance_checks)
            
            return TaskResult(
                task_id=task.id,
                success=True,
                data={
                    "compliance_checks": [self._compliance_check_to_dict(check) for check in compliance_checks],
                    "summary": summary
                },
                agent_name=self.name
            )
            
        except Exception as e:
            return await self.handle_error(e, task)
    
    async def _check_pattern_compliance(self, pattern: Dict[str, Any], regulations: List[str], risk_assessment: bool) -> ComplianceCheck:
        """Check compliance for a specific pattern."""
        pattern_type = pattern.get("pattern_type", "unknown")
        confidence = pattern.get("confidence", 0.0)
        risk_level = pattern.get("risk_level", "medium")
        indicators = pattern.get("indicators", [])
        
        # Determine which regulations are most relevant
        relevant_regulations = self._get_relevant_regulations(pattern_type, indicators)
        
        # Use LLM to assess compliance
        compliance_assessment = await self._assess_compliance_with_llm(
            pattern_type, indicators, confidence, risk_level, relevant_regulations
        )
        
        # Create compliance check
        check = ComplianceCheck(
            pattern_id=pattern.get("id", "unknown"),
            regulation_reference=", ".join(relevant_regulations),
            status=compliance_assessment["status"],
            justification=compliance_assessment["justification"],
            risk_assessment=compliance_assessment["risk_assessment"],
            recommended_actions=compliance_assessment["recommended_actions"]
        )
        
        return check
    
    async def _assess_compliance_with_llm(self, pattern_type: str, indicators: List[str], confidence: float, risk_level: str, regulations: List[str]) -> Dict[str, Any]:
        """Use LLM to assess compliance."""
        prompt = f"""
        Assess the compliance of this suspicious pattern against AML regulations:
        
        Pattern Type: {pattern_type}
        Confidence: {confidence:.2f}
        Risk Level: {risk_level}
        Indicators: {', '.join(indicators)}
        Relevant Regulations: {', '.join(regulations)}
        
        Provide a JSON response with:
        {{
            "status": "compliant|non_compliant|requires_review|insufficient_data",
            "justification": "detailed explanation",
            "risk_assessment": "risk level and reasoning",
            "recommended_actions": ["action1", "action2", "action3"]
        }}
        """
        
        try:
            response = await self.call_llm_simple(prompt, self.system_prompt)
            
            # Parse response (in a real system, you'd use proper JSON parsing)
            # For now, return a structured assessment based on pattern type
            return self._create_structured_assessment(pattern_type, confidence, risk_level, indicators, regulations)
            
        except Exception as e:
            await async_logger.log_error(e, {"operation": "llm_compliance_assessment"})
            return self._create_structured_assessment(pattern_type, confidence, risk_level, indicators, regulations)
    
    def _create_structured_assessment(self, pattern_type: str, confidence: float, risk_level: str, indicators: List[str], regulations: List[str]) -> Dict[str, Any]:
        """Create a structured compliance assessment."""
        # Determine status based on pattern type and confidence
        if confidence > 0.8:
            status = ComplianceStatus.NON_COMPLIANT
        elif confidence > 0.6:
            status = ComplianceStatus.REQUIRES_REVIEW
        else:
            status = ComplianceStatus.INSUFFICIENT_DATA
        
        # Create justification
        justification = f"Pattern type '{pattern_type}' detected with {confidence:.2f} confidence. "
        justification += f"Risk level: {risk_level}. "
        justification += f"Indicators: {', '.join(indicators)}. "
        justification += f"Relevant regulations: {', '.join(regulations)}."
        
        # Risk assessment
        risk_assessment = f"High risk due to {pattern_type} pattern with {confidence:.2f} confidence. "
        if "structuring" in pattern_type:
            risk_assessment += "Potential BSA violation for structuring transactions."
        elif "layering" in pattern_type:
            risk_assessment += "Complex transaction chain suggests money laundering attempt."
        elif "integration" in pattern_type:
            risk_assessment += "Large amounts from unknown sources require investigation."
        
        # Recommended actions
        recommended_actions = []
        if status == ComplianceStatus.NON_COMPLIANT:
            recommended_actions.extend([
                "File Suspicious Activity Report (SAR)",
                "Freeze affected accounts",
                "Conduct enhanced due diligence",
                "Report to regulatory authorities"
            ])
        elif status == ComplianceStatus.REQUIRES_REVIEW:
            recommended_actions.extend([
                "Conduct manual review",
                "Gather additional information",
                "Monitor account activity",
                "Consider enhanced monitoring"
            ])
        else:
            recommended_actions.extend([
                "Continue monitoring",
                "Document findings",
                "Update risk assessment"
            ])
        
        return {
            "status": status,
            "justification": justification,
            "risk_assessment": risk_assessment,
            "recommended_actions": recommended_actions
        }
    
    def _get_relevant_regulations(self, pattern_type: str, indicators: List[str]) -> List[str]:
        """Get relevant regulations for a pattern type."""
        regulations = []
        
        # BSA is always relevant for AML
        regulations.append("BSA")
        
        # Add specific regulations based on pattern type
        if "structuring" in pattern_type.lower():
            regulations.extend(["BSA", "PATRIOT_Act"])
        
        if "layering" in pattern_type.lower():
            regulations.extend(["BSA", "PATRIOT_Act", "OFAC"])
        
        if "integration" in pattern_type.lower():
            regulations.extend(["BSA", "PATRIOT_Act"])
        
        if any("international" in indicator.lower() for indicator in indicators):
            regulations.append("OFAC")
        
        if any("terrorist" in indicator.lower() for indicator in indicators):
            regulations.extend(["PATRIOT_Act", "OFAC"])
        
        return list(set(regulations))  # Remove duplicates
    
    def _create_compliance_summary(self, compliance_checks: List[ComplianceCheck]) -> Dict[str, Any]:
        """Create a summary of compliance checks."""
        total_checks = len(compliance_checks)
        non_compliant = sum(1 for check in compliance_checks if check.status == ComplianceStatus.NON_COMPLIANT)
        requires_review = sum(1 for check in compliance_checks if check.status == ComplianceStatus.REQUIRES_REVIEW)
        compliant = sum(1 for check in compliance_checks if check.status == ComplianceStatus.COMPLIANT)
        
        return {
            "total_checks": total_checks,
            "non_compliant": non_compliant,
            "requires_review": requires_review,
            "compliant": compliant,
            "compliance_rate": (compliant / total_checks) if total_checks > 0 else 0.0,
            "high_risk_count": non_compliant + requires_review
        }
    
    def _compliance_check_to_dict(self, check: ComplianceCheck) -> Dict[str, Any]:
        """Convert compliance check to dictionary."""
        return {
            "id": check.id,
            "pattern_id": check.pattern_id,
            "regulation_reference": check.regulation_reference,
            "status": check.status,
            "justification": check.justification,
            "risk_assessment": check.risk_assessment,
            "recommended_actions": check.recommended_actions,
            "compliance_officer": check.compliance_officer,
            "checked_at": check.checked_at.isoformat(),
            "metadata": check.metadata
        }
    
    async def validate_input(self, task: Task) -> bool:
        """Validate compliance task input."""
        if not await super().validate_input(task):
            return False
        
        # Check for suspicious patterns
        if "suspicious_patterns" not in task.payload:
            return False
        
        return True 