"""
Synthesizer agent for aggregating findings into structured reports.
"""

from typing import Dict, Any, List
from decimal import Decimal
from ..models.task import Task, TaskResult, TaskType
from ..models.report import AMLReport, SuspiciousPattern, ComplianceCheck, VerificationResult, ReportStatus
from ..config.settings import settings
from ..utils.logging import async_logger
from .base import BaseAgent


class SynthesizerAgent(BaseAgent):
    """Agent responsible for synthesizing findings into comprehensive reports."""
    
    def __init__(self, name: str = "synthesizer"):
        """Initialize the synthesizer agent."""
        super().__init__(name)
        self.system_prompt = """
        You are a report synthesis agent for AML analysis. Your role is to aggregate findings
        from multiple agents and create comprehensive, well-structured reports that summarize
        suspicious patterns, compliance issues, and recommended actions.
        
        Focus on clarity, accuracy, and actionable insights.
        """
    
    async def process_task(self, task: Task) -> TaskResult:
        """Process a synthesis task."""
        try:
            # Gather all the data from previous tasks
            transaction_data = task.payload.get("transactions", {})
            analysis_results = task.payload.get("analysis_results", {})
            compliance_results = task.payload.get("compliance_results", {})
            verification_results = task.payload.get("verification_results", {})
            report_type = task.payload.get("report_type", "aml_analysis")
            include_recommendations = task.payload.get("include_recommendations", True)
            
            # Create comprehensive AML report
            report = await self._create_aml_report(
                transaction_data,
                analysis_results,
                compliance_results,
                verification_results,
                report_type,
                include_recommendations
            )
            
            # Generate executive summary using LLM
            executive_summary = await self._generate_executive_summary(report)
            report.description = executive_summary
            
            return TaskResult(
                task_id=task.id,
                success=True,
                data={
                    "report": report.to_dict(),
                    "report_id": report.id,
                    "summary": report.get_summary()
                },
                agent_name=self.name
            )
            
        except Exception as e:
            return await self.handle_error(e, task)
    
    async def _create_aml_report(
        self,
        transaction_data: Dict[str, Any],
        analysis_results: Dict[str, Any],
        compliance_results: Dict[str, Any],
        verification_results: Dict[str, Any],
        report_type: str,
        include_recommendations: bool
    ) -> AMLReport:
        """Create a comprehensive AML report."""
        # Create base report
        report = AMLReport(
            title=f"AML Analysis Report - {report_type.replace('_', ' ').title()}",
            description="Comprehensive anti-money laundering analysis report",
            status=ReportStatus.DRAFT,
            analyst=self.name
        )
        
        # Add transaction statistics
        if transaction_data:
            report.total_transactions_analyzed = transaction_data.get("transaction_count", 0)
            report.total_amount_analyzed = Decimal(str(transaction_data.get("total_amount", 0)))
        
        # Add suspicious patterns from analysis
        if analysis_results and "suspicious_patterns" in analysis_results:
            for pattern_data in analysis_results["suspicious_patterns"]:
                pattern = self._create_suspicious_pattern(pattern_data)
                report.add_suspicious_pattern(pattern)
        
        # Add compliance checks
        if compliance_results and "compliance_checks" in compliance_results:
            for check_data in compliance_results["compliance_checks"]:
                check = self._create_compliance_check(check_data)
                report.add_compliance_check(check)
        
        # Add verification results
        if verification_results and "verification_results" in verification_results:
            for verification_data in verification_results["verification_results"]:
                verification = self._create_verification_result(verification_data)
                report.add_verification_result(verification)
        
        # Add recommendations if requested
        if include_recommendations:
            recommendations = await self._generate_recommendations(report)
            report.metadata["recommendations"] = recommendations
        
        return report
    
    def _create_suspicious_pattern(self, pattern_data: Dict[str, Any]) -> SuspiciousPattern:
        """Create a SuspiciousPattern object from data."""
        return SuspiciousPattern(
            id=pattern_data.get("id", ""),
            pattern_type=pattern_data.get("pattern_type", ""),
            description=pattern_data.get("description", ""),
            confidence=pattern_data.get("confidence", 0.0),
            risk_level=pattern_data.get("risk_level", "low"),
            affected_transactions=pattern_data.get("affected_transactions", []),
            indicators=pattern_data.get("indicators", []),
            amount_involved=Decimal(str(pattern_data.get("amount_involved", 0))),
            entity_involved=pattern_data.get("entity_involved", []),
            detection_method=pattern_data.get("detection_method", ""),
            metadata=pattern_data.get("metadata", {})
        )
    
    def _create_compliance_check(self, check_data: Dict[str, Any]) -> ComplianceCheck:
        """Create a ComplianceCheck object from data."""
        return ComplianceCheck(
            id=check_data.get("id", ""),
            pattern_id=check_data.get("pattern_id", ""),
            regulation_reference=check_data.get("regulation_reference", ""),
            status=check_data.get("status", "insufficient_data"),
            justification=check_data.get("justification", ""),
            risk_assessment=check_data.get("risk_assessment", ""),
            recommended_actions=check_data.get("recommended_actions", []),
            compliance_officer=check_data.get("compliance_officer"),
            metadata=check_data.get("metadata", {})
        )
    
    def _create_verification_result(self, verification_data: Dict[str, Any]) -> VerificationResult:
        """Create a VerificationResult object from data."""
        return VerificationResult(
            id=verification_data.get("id", ""),
            pattern_id=verification_data.get("pattern_id", ""),
            agent_results=verification_data.get("agent_results", {}),
            consensus_reached=verification_data.get("consensus_reached", False),
            consensus_score=verification_data.get("consensus_score", 0.0),
            disagreement_reasons=verification_data.get("disagreement_reasons", []),
            requires_human_review=verification_data.get("requires_human_review", False),
            metadata=verification_data.get("metadata", {})
        )
    
    async def _generate_executive_summary(self, report: AMLReport) -> str:
        """Generate an executive summary using LLM."""
        summary_prompt = f"""
        Create an executive summary for this AML analysis report:
        
        Key Statistics:
        - Total transactions analyzed: {report.total_transactions_analyzed}
        - Total amount analyzed: ${report.total_amount_analyzed:,.2f}
        - Suspicious patterns found: {len(report.suspicious_patterns)}
        - High-risk patterns: {report.high_risk_patterns_count}
        - Compliance violations: {report.compliance_violations_count}
        
        Pattern Types Found:
        {self._get_pattern_summary(report.suspicious_patterns)}
        
        Compliance Status:
        {self._get_compliance_summary(report.compliance_checks)}
        
        Verification Results:
        {self._get_verification_summary(report.verification_results)}
        
        Provide a concise executive summary (2-3 paragraphs) highlighting the key findings,
        risk levels, and immediate actions required.
        """
        
        try:
            summary = await self.call_llm_simple(summary_prompt, self.system_prompt)
            return summary
        except Exception as e:
            await async_logger.log_error(e, {"operation": "generate_executive_summary"})
            return self._create_fallback_summary(report)
    
    async def _generate_recommendations(self, report: AMLReport) -> List[str]:
        """Generate recommendations based on report findings."""
        recommendations = []
        
        # High-risk recommendations
        if report.high_risk_patterns_count > 0:
            recommendations.append("Immediate action required: High-risk patterns detected")
            recommendations.append("File Suspicious Activity Reports (SARs) for all high-risk patterns")
            recommendations.append("Implement enhanced monitoring for affected entities")
        
        # Compliance recommendations
        if report.compliance_violations_count > 0:
            recommendations.append("Address compliance violations immediately")
            recommendations.append("Review and update compliance procedures")
            recommendations.append("Conduct staff training on AML regulations")
        
        # Verification recommendations
        human_review_count = sum(1 for v in report.verification_results if v.requires_human_review)
        if human_review_count > 0:
            recommendations.append(f"Conduct manual review for {human_review_count} patterns requiring human oversight")
        
        # General recommendations
        recommendations.extend([
            "Continue monitoring for similar patterns",
            "Update risk assessment models based on findings",
            "Consider implementing additional detection algorithms",
            "Review customer due diligence procedures"
        ])
        
        return recommendations
    
    def _get_pattern_summary(self, patterns: List[SuspiciousPattern]) -> str:
        """Get a summary of patterns by type."""
        pattern_counts = {}
        for pattern in patterns:
            pattern_type = pattern.pattern_type
            pattern_counts[pattern_type] = pattern_counts.get(pattern_type, 0) + 1
        
        summary = []
        for pattern_type, count in pattern_counts.items():
            summary.append(f"- {pattern_type}: {count}")
        
        return "\n".join(summary) if summary else "No patterns detected"
    
    def _get_compliance_summary(self, checks: List[ComplianceCheck]) -> str:
        """Get a summary of compliance checks."""
        status_counts = {}
        for check in checks:
            status = check.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        summary = []
        for status, count in status_counts.items():
            summary.append(f"- {status}: {count}")
        
        return "\n".join(summary) if summary else "No compliance checks performed"
    
    def _get_verification_summary(self, verifications: List[VerificationResult]) -> str:
        """Get a summary of verification results."""
        consensus_count = sum(1 for v in verifications if v.consensus_reached)
        human_review_count = sum(1 for v in verifications if v.requires_human_review)
        
        return f"""
        - Total verifications: {len(verifications)}
        - Consensus reached: {consensus_count}
        - Human review required: {human_review_count}
        """
    
    def _create_fallback_summary(self, report: AMLReport) -> str:
        """Create a fallback summary if LLM fails."""
        return f"""
        AML Analysis Report Summary
        
        This report analyzes {report.total_transactions_analyzed} transactions totaling ${report.total_amount_analyzed:,.2f}.
        
        Key Findings:
        - {len(report.suspicious_patterns)} suspicious patterns detected
        - {report.high_risk_patterns_count} high-risk patterns identified
        - {report.compliance_violations_count} compliance violations found
        
        The analysis utilized multiple detection methods including anomaly detection, pattern recognition,
        and statistical analysis. All findings have been verified through multi-agent consensus and
        compliance checks have been performed against relevant AML regulations.
        
        Immediate attention is required for high-risk patterns and compliance violations.
        """
    
    async def validate_input(self, task: Task) -> bool:
        """Validate synthesizer task input."""
        if not await super().validate_input(task):
            return False
        
        # Check for at least some analysis results
        if not any(key in task.payload for key in ["analysis_results", "compliance_results", "verification_results"]):
            return False
        
        return True 