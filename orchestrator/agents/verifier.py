"""
Verifier agent for multi-agent verification and consensus.
"""

import random
from typing import Dict, Any, List
from ..models.task import Task, TaskResult, TaskType
from ..models.report import VerificationResult
from ..config.settings import settings
from ..utils.logging import async_logger
from .base import BaseAgent


class VerifierAgent(BaseAgent):
    """Agent responsible for multi-agent verification and consensus."""
    
    def __init__(self, name: str = "verifier"):
        """Initialize the verifier agent."""
        super().__init__(name)
        self.system_prompt = """
        You are a verification agent for AML analysis. Your role is to independently verify
        suspicious patterns and provide consensus with other agents. Be thorough and objective
        in your analysis, considering multiple perspectives and evidence.
        """
        self.verification_methods = ["statistical", "rule_based", "behavioral"]
    
    async def process_task(self, task: Task) -> TaskResult:
        """Process a verification task."""
        try:
            suspicious_patterns = task.payload.get("suspicious_patterns", [])
            verification_method = task.payload.get("verification_method", "multi_agent_consensus")
            consensus_threshold = task.payload.get("consensus_threshold", settings.agents.verifier_consensus_threshold)
            
            if not suspicious_patterns:
                return TaskResult(
                    task_id=task.id,
                    success=True,
                    data={"verification_results": [], "summary": "No patterns to verify"},
                    agent_name=self.name
                )
            
            verification_results = []
            
            for pattern in suspicious_patterns:
                result = await self._verify_pattern(pattern, verification_method, consensus_threshold)
                verification_results.append(result)
            
            # Create summary
            summary = self._create_verification_summary(verification_results)
            
            return TaskResult(
                task_id=task.id,
                success=True,
                data={
                    "verification_results": [self._verification_result_to_dict(result) for result in verification_results],
                    "summary": summary
                },
                agent_name=self.name
            )
            
        except Exception as e:
            return await self.handle_error(e, task)
    
    async def _verify_pattern(self, pattern: Dict[str, Any], method: str, consensus_threshold: float) -> VerificationResult:
        """Verify a specific pattern using multiple methods."""
        pattern_id = pattern.get("id", "unknown")
        pattern_type = pattern.get("pattern_type", "unknown")
        confidence = pattern.get("confidence", 0.0)
        
        # Simulate multiple agent verifications
        agent_results = {}
        
        # Agent 1: Statistical verification
        agent_results["statistical_agent"] = await self._statistical_verification(pattern)
        
        # Agent 2: Rule-based verification
        agent_results["rule_based_agent"] = await self._rule_based_verification(pattern)
        
        # Agent 3: Behavioral verification
        agent_results["behavioral_agent"] = await self._behavioral_verification(pattern)
        
        # Calculate consensus
        consensus_reached, consensus_score, disagreement_reasons = self._calculate_consensus(
            agent_results, consensus_threshold
        )
        
        # Determine if human review is needed
        requires_human_review = self._determine_human_review_needed(
            consensus_reached, consensus_score, pattern_type, confidence
        )
        
        return VerificationResult(
            pattern_id=pattern_id,
            agent_results=agent_results,
            consensus_reached=consensus_reached,
            consensus_score=consensus_score,
            disagreement_reasons=disagreement_reasons,
            requires_human_review=requires_human_review
        )
    
    async def _statistical_verification(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Statistical verification of a pattern."""
        pattern_type = pattern.get("pattern_type", "unknown")
        confidence = pattern.get("confidence", 0.0)
        amount_involved = pattern.get("amount_involved", 0)
        
        # Simulate statistical analysis
        statistical_score = confidence * 0.8  # Base score
        
        # Adjust based on pattern type
        if "structuring" in pattern_type.lower():
            statistical_score *= 1.2  # Higher confidence for structuring
        elif "layering" in pattern_type.lower():
            statistical_score *= 0.9  # Lower confidence for layering
        
        # Adjust based on amount
        if amount_involved > 100000:
            statistical_score *= 1.1
        elif amount_involved < 1000:
            statistical_score *= 0.8
        
        # Add some randomness to simulate real-world variation
        statistical_score += random.uniform(-0.1, 0.1)
        statistical_score = max(0.0, min(1.0, statistical_score))
        
        return {
            "verification_method": "statistical",
            "confidence": statistical_score,
            "verified": statistical_score > 0.6,
            "reasoning": f"Statistical analysis indicates {statistical_score:.2f} confidence in {pattern_type} pattern",
            "factors": ["amount_analysis", "frequency_analysis", "pattern_recognition"]
        }
    
    async def _rule_based_verification(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Rule-based verification of a pattern."""
        pattern_type = pattern.get("pattern_type", "unknown")
        indicators = pattern.get("indicators", [])
        risk_level = pattern.get("risk_level", "medium")
        
        # Apply rule-based logic
        rule_score = 0.5  # Base score
        
        # Check indicators
        if len(indicators) >= 3:
            rule_score += 0.2
        elif len(indicators) >= 2:
            rule_score += 0.1
        
        # Check risk level
        if risk_level == "high":
            rule_score += 0.2
        elif risk_level == "critical":
            rule_score += 0.3
        
        # Pattern-specific rules
        if "structuring" in pattern_type.lower():
            if any("threshold" in indicator.lower() for indicator in indicators):
                rule_score += 0.2
        
        if "layering" in pattern_type.lower():
            if any("chain" in indicator.lower() for indicator in indicators):
                rule_score += 0.2
        
        # Add randomness
        rule_score += random.uniform(-0.05, 0.05)
        rule_score = max(0.0, min(1.0, rule_score))
        
        return {
            "verification_method": "rule_based",
            "confidence": rule_score,
            "verified": rule_score > 0.6,
            "reasoning": f"Rule-based analysis shows {rule_score:.2f} confidence based on {len(indicators)} indicators",
            "factors": ["indicator_count", "risk_level", "pattern_rules"]
        }
    
    async def _behavioral_verification(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Behavioral verification of a pattern."""
        pattern_type = pattern.get("pattern_type", "unknown")
        entity_involved = pattern.get("entity_involved", [])
        detection_method = pattern.get("detection_method", "unknown")
        
        # Simulate behavioral analysis
        behavioral_score = 0.6  # Base score
        
        # Entity analysis
        if len(entity_involved) > 1:
            behavioral_score += 0.1  # Multiple entities involved
        
        # Detection method analysis
        if "isolation_forest" in detection_method.lower():
            behavioral_score += 0.1
        elif "statistical_analysis" in detection_method.lower():
            behavioral_score += 0.05
        
        # Pattern-specific behavioral factors
        if "structuring" in pattern_type.lower():
            behavioral_score += 0.1  # Structuring is behaviorally suspicious
        
        if "layering" in pattern_type.lower():
            behavioral_score += 0.15  # Layering is highly suspicious
        
        # Add randomness
        behavioral_score += random.uniform(-0.08, 0.08)
        behavioral_score = max(0.0, min(1.0, behavioral_score))
        
        return {
            "verification_method": "behavioral",
            "confidence": behavioral_score,
            "verified": behavioral_score > 0.6,
            "reasoning": f"Behavioral analysis indicates {behavioral_score:.2f} confidence in suspicious behavior",
            "factors": ["entity_behavior", "transaction_patterns", "temporal_analysis"]
        }
    
    def _calculate_consensus(self, agent_results: Dict[str, Dict[str, Any]], threshold: float) -> tuple[bool, float, List[str]]:
        """Calculate consensus among agents."""
        verifications = [result["verified"] for result in agent_results.values()]
        confidences = [result["confidence"] for result in agent_results.values()]
        
        # Calculate consensus score
        consensus_score = sum(confidences) / len(confidences)
        
        # Check if consensus is reached
        consensus_reached = consensus_score >= threshold
        
        # Identify disagreements
        disagreement_reasons = []
        if not consensus_reached:
            disagreement_reasons.append(f"Consensus score {consensus_score:.2f} below threshold {threshold}")
        
        # Check for agent disagreements
        if len(set(verifications)) > 1:
            disagreement_reasons.append("Agents disagree on verification result")
        
        return consensus_reached, consensus_score, disagreement_reasons
    
    def _determine_human_review_needed(self, consensus_reached: bool, consensus_score: float, pattern_type: str, original_confidence: float) -> bool:
        """Determine if human review is needed."""
        # High confidence patterns with consensus don't need review
        if consensus_reached and consensus_score > 0.8:
            return False
        
        # Low consensus or high-risk patterns need review
        if not consensus_reached:
            return True
        
        # High-risk pattern types need review
        high_risk_patterns = ["structuring", "layering", "integration"]
        if any(risk_pattern in pattern_type.lower() for risk_pattern in high_risk_patterns):
            return True
        
        # High original confidence with low consensus needs review
        if original_confidence > 0.8 and consensus_score < 0.7:
            return True
        
        return False
    
    def _create_verification_summary(self, verification_results: List[VerificationResult]) -> Dict[str, Any]:
        """Create a summary of verification results."""
        total_verifications = len(verification_results)
        consensus_reached = sum(1 for result in verification_results if result.consensus_reached)
        human_review_needed = sum(1 for result in verification_results if result.requires_human_review)
        
        avg_consensus_score = sum(result.consensus_score for result in verification_results) / total_verifications if total_verifications > 0 else 0.0
        
        return {
            "total_verifications": total_verifications,
            "consensus_reached": consensus_reached,
            "human_review_needed": human_review_needed,
            "average_consensus_score": avg_consensus_score,
            "consensus_rate": consensus_reached / total_verifications if total_verifications > 0 else 0.0
        }
    
    def _verification_result_to_dict(self, result: VerificationResult) -> Dict[str, Any]:
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
    
    async def validate_input(self, task: Task) -> bool:
        """Validate verifier task input."""
        if not await super().validate_input(task):
            return False
        
        # Check for suspicious patterns
        if "suspicious_patterns" not in task.payload:
            return False
        
        return True 