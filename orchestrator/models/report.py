"""
Report data models for AML analysis results.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import uuid4

from .transaction import RiskLevel, TransactionPattern


class ReportStatus(str, Enum):
    """Status of a report."""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUBMITTED = "submitted"


class ComplianceStatus(str, Enum):
    """Compliance status for patterns."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    REQUIRES_REVIEW = "requires_review"
    INSUFFICIENT_DATA = "insufficient_data"


@dataclass
class SuspiciousPattern:
    """Represents a suspicious pattern detected in transactions."""
    id: str = field(default_factory=lambda: str(uuid4()))
    pattern_type: str = ""
    description: str = ""
    risk_level: RiskLevel = RiskLevel.LOW
    confidence: float = 0.0
    affected_transactions: List[str] = field(default_factory=list)
    indicators: List[str] = field(default_factory=list)
    amount_involved: Decimal = Decimal('0')
    entity_involved: List[str] = field(default_factory=list)
    detection_method: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.amount_involved, (int, float)):
            self.amount_involved = Decimal(str(self.amount_involved))


@dataclass
class ComplianceCheck:
    """Represents a compliance check result."""
    id: str = field(default_factory=lambda: str(uuid4()))
    pattern_id: str = ""
    regulation_reference: str = ""
    status: ComplianceStatus = ComplianceStatus.INSUFFICIENT_DATA
    justification: str = ""
    risk_assessment: str = ""
    recommended_actions: List[str] = field(default_factory=list)
    compliance_officer: Optional[str] = None
    checked_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if isinstance(self.checked_at, str):
            self.checked_at = datetime.fromisoformat(self.checked_at)


@dataclass
class VerificationResult:
    """Result of multi-agent verification."""
    id: str = field(default_factory=lambda: str(uuid4()))
    pattern_id: str = ""
    agent_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    consensus_reached: bool = False
    consensus_score: float = 0.0
    disagreement_reasons: List[str] = field(default_factory=list)
    requires_human_review: bool = False
    verified_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if isinstance(self.verified_at, str):
            self.verified_at = datetime.fromisoformat(self.verified_at)


@dataclass
class AMLReport:
    """Complete AML analysis report."""
    id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    description: str = ""
    status: ReportStatus = ReportStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    # Analysis results
    suspicious_patterns: List[SuspiciousPattern] = field(default_factory=list)
    compliance_checks: List[ComplianceCheck] = field(default_factory=list)
    verification_results: List[VerificationResult] = field(default_factory=list)
    
    # Summary statistics
    total_transactions_analyzed: int = 0
    total_amount_analyzed: Decimal = Decimal('0')
    high_risk_patterns_count: int = 0
    compliance_violations_count: int = 0
    
    # Metadata
    analyst: Optional[str] = None
    reviewer: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.fromisoformat(self.updated_at)
        if isinstance(self.total_amount_analyzed, (int, float)):
            self.total_amount_analyzed = Decimal(str(self.total_amount_analyzed))
    
    def add_suspicious_pattern(self, pattern: SuspiciousPattern) -> None:
        """Add a suspicious pattern to the report."""
        self.suspicious_patterns.append(pattern)
        if pattern.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            self.high_risk_patterns_count += 1
    
    def add_compliance_check(self, check: ComplianceCheck) -> None:
        """Add a compliance check to the report."""
        self.compliance_checks.append(check)
        if check.status == ComplianceStatus.NON_COMPLIANT:
            self.compliance_violations_count += 1
    
    def add_verification_result(self, result: VerificationResult) -> None:
        """Add a verification result to the report."""
        self.verification_results.append(result)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the report."""
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "total_patterns": len(self.suspicious_patterns),
            "high_risk_patterns": self.high_risk_patterns_count,
            "compliance_violations": self.compliance_violations_count,
            "total_amount": float(self.total_amount_analyzed),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary for serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "suspicious_patterns": [self._pattern_to_dict(p) for p in self.suspicious_patterns],
            "compliance_checks": [self._check_to_dict(c) for c in self.compliance_checks],
            "verification_results": [self._verification_to_dict(v) for v in self.verification_results],
            "total_transactions_analyzed": self.total_transactions_analyzed,
            "total_amount_analyzed": float(self.total_amount_analyzed),
            "high_risk_patterns_count": self.high_risk_patterns_count,
            "compliance_violations_count": self.compliance_violations_count,
            "analyst": self.analyst,
            "reviewer": self.reviewer,
            "tags": self.tags,
            "metadata": self.metadata
        }
    
    def _pattern_to_dict(self, pattern: SuspiciousPattern) -> Dict[str, Any]:
        """Convert suspicious pattern to dictionary."""
        return {
            "id": pattern.id,
            "pattern_type": pattern.pattern_type,
            "description": pattern.description,
            "risk_level": pattern.risk_level,
            "confidence": pattern.confidence,
            "affected_transactions": pattern.affected_transactions,
            "indicators": pattern.indicators,
            "amount_involved": float(pattern.amount_involved),
            "entity_involved": pattern.entity_involved,
            "detection_method": pattern.detection_method,
            "created_at": pattern.created_at.isoformat(),
            "metadata": pattern.metadata
        }
    
    def _check_to_dict(self, check: ComplianceCheck) -> Dict[str, Any]:
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
    
    def _verification_to_dict(self, result: VerificationResult) -> Dict[str, Any]:
        """Convert verification result to dictionary."""
        return {
            "id": result.id,
            "pattern_id": result.pattern_id,
            "agent_results": result.agent_results,
            "consensus_reached": result.consensus_reached,
            "consensus_score": result.consensus_score,
            "disagreement_reasons": result.disagreement_reasons,
            "requires_human_review": result.requires_human_review,
            "verified_at": result.verified_at.isoformat(),
            "metadata": result.metadata
        } 