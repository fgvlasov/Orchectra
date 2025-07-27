"""
Transaction data models for AML analysis.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import uuid4


class TransactionType(str, Enum):
    """Types of financial transactions."""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    PAYMENT = "payment"
    EXCHANGE = "exchange"
    WIRE = "wire"
    ACH = "ach"
    CARD = "card"


class RiskLevel(str, Enum):
    """Risk levels for transactions."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Transaction:
    """Represents a financial transaction."""
    id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    amount: Decimal = Decimal('0')
    currency: str = "USD"
    transaction_type: TransactionType = TransactionType.TRANSFER
    sender_id: str = ""
    recipient_id: str = ""
    sender_name: Optional[str] = None
    recipient_name: Optional[str] = None
    description: Optional[str] = None
    reference: Optional[str] = None
    risk_level: RiskLevel = RiskLevel.LOW
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)
        if isinstance(self.amount, (int, float)):
            self.amount = Decimal(str(self.amount))


@dataclass
class TransactionBatch:
    """A batch of transactions for processing."""
    id: str = field(default_factory=lambda: str(uuid4()))
    transactions: List[Transaction] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    source: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
    
    def add_transaction(self, transaction: Transaction) -> None:
        """Add a transaction to the batch."""
        self.transactions.append(transaction)
    
    def get_total_amount(self) -> Decimal:
        """Get the total amount of all transactions in the batch."""
        return sum(t.amount for t in self.transactions)
    
    def get_high_risk_transactions(self) -> List[Transaction]:
        """Get transactions with high or critical risk levels."""
        return [t for t in self.transactions if t.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]]


@dataclass
class TransactionPattern:
    """Represents a pattern detected in transactions."""
    id: str = field(default_factory=lambda: str(uuid4()))
    pattern_type: str = ""
    description: str = ""
    confidence: float = 0.0
    risk_level: RiskLevel = RiskLevel.LOW
    affected_transactions: List[str] = field(default_factory=list)  # Transaction IDs
    indicators: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)


@dataclass
class Entity:
    """Represents an entity (person, organization) involved in transactions."""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    entity_type: str = "individual"  # individual, organization
    risk_score: float = 0.0
    kyc_status: str = "unknown"  # verified, pending, rejected
    country: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at) 