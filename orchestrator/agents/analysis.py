"""
Analysis agent for anomaly detection and pattern analysis.
"""

from typing import Dict, Any, List
from decimal import Decimal

from ..models.task import Task, TaskResult, TaskType
from ..models.transaction import Transaction, RiskLevel
from ..models.report import SuspiciousPattern
from ..utils.anomaly_detection import AnomalyDetector, StatisticalAnomalyDetector, PatternDetector
from ..config.settings import settings
from ..utils.logging import async_logger
from .base import BaseAgent


class AnalysisAgent(BaseAgent):
    """Agent responsible for anomaly detection and pattern analysis."""
    
    def __init__(self, name: str = "analysis"):
        """Initialize the analysis agent."""
        super().__init__(name)
        self.anomaly_detector = AnomalyDetector(contamination=settings.agents.analysis_anomaly_threshold)
        self.statistical_detector = StatisticalAnomalyDetector()
        self.pattern_detector = PatternDetector()
        self.system_prompt = """
        You are an AML analysis agent specializing in detecting suspicious patterns in financial transactions.
        Analyze the provided transaction data and identify potential money laundering indicators.
        Focus on patterns like structuring, layering, integration, and unusual transaction behaviors.
        """
    
    async def process_task(self, task: Task) -> TaskResult:
        """Process an analysis task."""
        try:
            # Get transaction data from previous tasks
            transaction_data = task.payload.get("transactions", {})
            analysis_types = task.payload.get("analysis_types", ["anomaly_detection", "pattern_detection"])
            thresholds = task.payload.get("thresholds", {"anomaly": 0.05, "pattern": 0.7})
            
            # Convert transaction data back to Transaction objects
            transactions = self._dict_to_transactions(transaction_data.get("transactions", []))
            
            if not transactions:
                raise ValueError("No transaction data provided for analysis")
            
            results = {}
            
            # Perform anomaly detection
            if "anomaly_detection" in analysis_types:
                anomaly_results = await self._detect_anomalies(transactions, thresholds["anomaly"])
                results["anomalies"] = anomaly_results
            
            # Perform pattern detection
            if "pattern_detection" in analysis_types:
                pattern_results = await self._detect_patterns(transactions, thresholds["pattern"])
                results["patterns"] = pattern_results
            
            # Create suspicious patterns
            suspicious_patterns = await self._create_suspicious_patterns(transactions, results)
            results["suspicious_patterns"] = suspicious_patterns
            
            return TaskResult(
                task_id=task.id,
                success=True,
                data=results,
                agent_name=self.name
            )
            
        except Exception as e:
            return await self.handle_error(e, task)
    
    async def _detect_anomalies(self, transactions: List[Transaction], threshold: float) -> Dict[str, Any]:
        """Detect anomalies in transactions."""
        # Fit anomaly detection models
        self.anomaly_detector.fit(transactions)
        self.statistical_detector.fit(transactions)
        
        # Get anomaly predictions
        isolation_anomalies = self.anomaly_detector.detect_anomalies(transactions)
        amount_anomalies = self.statistical_detector.detect_amount_anomalies(transactions)
        frequency_anomalies = self.statistical_detector.detect_frequency_anomalies(transactions)
        
        # Get anomaly scores
        anomaly_scores = self.anomaly_detector.get_anomaly_scores(transactions)
        
        # Combine results
        combined_anomalies = []
        for i, tx in enumerate(transactions):
            is_anomalous = (
                isolation_anomalies[i] or 
                amount_anomalies[i] or 
                frequency_anomalies[i]
            )
            
            if is_anomalous:
                combined_anomalies.append({
                    "transaction_id": tx.id,
                    "anomaly_score": anomaly_scores[i],
                    "isolation_forest": isolation_anomalies[i],
                    "amount_anomaly": amount_anomalies[i],
                    "frequency_anomaly": frequency_anomalies[i],
                    "amount": float(tx.amount),
                    "entity": tx.sender_id,
                    "timestamp": tx.timestamp.isoformat()
                })
        
        return {
            "total_anomalies": len(combined_anomalies),
            "anomaly_rate": len(combined_anomalies) / len(transactions) if transactions else 0,
            "anomalies": combined_anomalies
        }
    
    async def _detect_patterns(self, transactions: List[Transaction], threshold: float) -> Dict[str, Any]:
        """Detect specific patterns in transactions."""
        patterns = self.pattern_detector.detect_patterns(transactions)
        
        # Filter patterns by confidence threshold
        filtered_patterns = {}
        for pattern_type, pattern_list in patterns.items():
            filtered_patterns[pattern_type] = [
                p for p in pattern_list if p.get("confidence", 0) >= threshold
            ]
        
        return {
            "total_patterns": sum(len(p) for p in filtered_patterns.values()),
            "patterns_by_type": filtered_patterns
        }
    
    async def _create_suspicious_patterns(self, transactions: List[Transaction], analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create suspicious pattern objects from analysis results."""
        suspicious_patterns = []
        
        # Create patterns from anomalies
        anomalies = analysis_results.get("anomalies", {}).get("anomalies", [])
        for anomaly in anomalies:
            pattern = {
                "pattern_type": "anomaly_detection",
                "description": f"Anomalous transaction detected with score {anomaly['anomaly_score']:.3f}",
                "confidence": min(anomaly["anomaly_score"], 1.0),
                "risk_level": RiskLevel.HIGH if anomaly["anomaly_score"] > 0.7 else RiskLevel.MEDIUM,
                "affected_transactions": [anomaly["transaction_id"]],
                "indicators": self._get_anomaly_indicators(anomaly),
                "amount_involved": anomaly["amount"],
                "entity_involved": [anomaly["entity"]],
                "detection_method": "isolation_forest"
            }
            suspicious_patterns.append(pattern)
        
        # Create patterns from pattern detection
        patterns = analysis_results.get("patterns", {}).get("patterns_by_type", {})
        for pattern_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                pattern_obj = {
                    "pattern_type": pattern_type,
                    "description": f"{pattern_type.replace('_', ' ').title()} pattern detected",
                    "confidence": pattern.get("confidence", 0.5),
                    "risk_level": RiskLevel.HIGH if pattern.get("confidence", 0) > 0.8 else RiskLevel.MEDIUM,
                    "affected_transactions": [],  # Would need to map back to transaction IDs
                    "indicators": self._get_pattern_indicators(pattern_type, pattern),
                    "amount_involved": pattern.get("total_amount", 0),
                    "entity_involved": pattern.get("entities", []),
                    "detection_method": "statistical_analysis"
                }
                suspicious_patterns.append(pattern_obj)
        
        return suspicious_patterns
    
    def _get_anomaly_indicators(self, anomaly: Dict[str, Any]) -> List[str]:
        """Get indicators for an anomaly."""
        indicators = []
        
        if anomaly.get("isolation_forest"):
            indicators.append("Isolation Forest anomaly")
        
        if anomaly.get("amount_anomaly"):
            indicators.append("Unusual transaction amount")
        
        if anomaly.get("frequency_anomaly"):
            indicators.append("Unusual transaction frequency")
        
        if anomaly.get("anomaly_score", 0) > 0.8:
            indicators.append("High anomaly score")
        
        return indicators
    
    def _get_pattern_indicators(self, pattern_type: str, pattern: Dict[str, Any]) -> List[str]:
        """Get indicators for a pattern."""
        indicators = []
        
        if pattern_type == "structuring":
            indicators.extend([
                "Multiple transactions under reporting threshold",
                "Same entity involved",
                "Same day transactions"
            ])
        elif pattern_type == "layering":
            indicators.extend([
                "Complex transaction chain",
                "Multiple entities involved",
                "Rapid movement of funds"
            ])
        elif pattern_type == "integration":
            indicators.extend([
                "Large deposit from unknown source",
                "Unusual transaction amount"
            ])
        elif pattern_type == "rapid_movement":
            indicators.extend([
                "Quick successive transactions",
                "Same entity involved"
            ])
        elif pattern_type == "unusual_amounts":
            indicators.extend([
                "Statistically significant amount",
                "High z-score"
            ])
        
        return indicators
    
    def _dict_to_transactions(self, transaction_dicts: List[Dict[str, Any]]) -> List[Transaction]:
        """Convert transaction dictionaries back to Transaction objects."""
        transactions = []
        
        for tx_dict in transaction_dicts:
            try:
                tx = Transaction(
                    id=tx_dict["id"],
                    timestamp=tx_dict["timestamp"],
                    amount=Decimal(str(tx_dict["amount"])),
                    currency=tx_dict["currency"],
                    transaction_type=tx_dict["transaction_type"],
                    sender_id=tx_dict["sender_id"],
                    recipient_id=tx_dict["recipient_id"],
                    sender_name=tx_dict.get("sender_name"),
                    recipient_name=tx_dict.get("recipient_name"),
                    description=tx_dict.get("description"),
                    reference=tx_dict.get("reference"),
                    risk_level=RiskLevel(tx_dict["risk_level"]),
                    metadata=tx_dict.get("metadata", {})
                )
                transactions.append(tx)
            except Exception as e:
                # Log error and continue with other transactions
                await async_logger.log_error(e, {
                    "operation": "dict_to_transaction",
                    "transaction_id": tx_dict.get("id", "unknown")
                })
        
        return transactions
    
    async def validate_input(self, task: Task) -> bool:
        """Validate analysis task input."""
        if not await super().validate_input(task):
            return False
        
        # Check for transaction data
        if "transactions" not in task.payload:
            return False
        
        return True 