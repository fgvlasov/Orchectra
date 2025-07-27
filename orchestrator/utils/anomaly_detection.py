"""
Anomaly detection utilities for transaction analysis.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from datetime import datetime, timedelta

from ..models.transaction import Transaction, TransactionBatch, RiskLevel
from ..config.settings import settings


class AnomalyDetector:
    """Anomaly detection for financial transactions."""
    
    def __init__(self, contamination: float = 0.1):
        """Initialize the anomaly detector."""
        self.contamination = contamination
        self.isolation_forest = IsolationForest(
            contamination=contamination,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_fitted = False
    
    def extract_features(self, transactions: List[Transaction]) -> np.ndarray:
        """Extract numerical features from transactions."""
        features = []
        
        for tx in transactions:
            # Basic transaction features
            amount = float(tx.amount)
            hour = tx.timestamp.hour
            day_of_week = tx.timestamp.weekday()
            month = tx.timestamp.month
            
            # Risk level encoding
            risk_level_map = {
                RiskLevel.LOW: 0,
                RiskLevel.MEDIUM: 1,
                RiskLevel.HIGH: 2,
                RiskLevel.CRITICAL: 3
            }
            risk_score = risk_level_map.get(tx.risk_level, 0)
            
            # Transaction type encoding
            tx_type_map = {
                "deposit": 0,
                "withdrawal": 1,
                "transfer": 2,
                "payment": 3,
                "exchange": 4,
                "wire": 5,
                "ach": 6,
                "card": 7
            }
            tx_type = tx_type_map.get(tx.transaction_type.value, 0)
            
            feature_vector = [
                amount,
                hour,
                day_of_week,
                month,
                risk_score,
                tx_type
            ]
            features.append(feature_vector)
        
        return np.array(features)
    
    def fit(self, transactions: List[Transaction]) -> None:
        """Fit the anomaly detection model."""
        if not transactions:
            return
        
        features = self.extract_features(transactions)
        features_scaled = self.scaler.fit_transform(features)
        self.isolation_forest.fit(features_scaled)
        self.is_fitted = True
    
    def detect_anomalies(self, transactions: List[Transaction]) -> List[bool]:
        """Detect anomalies in transactions."""
        if not transactions or not self.is_fitted:
            return [False] * len(transactions)
        
        features = self.extract_features(transactions)
        features_scaled = self.scaler.transform(features)
        predictions = self.isolation_forest.predict(features_scaled)
        
        # Convert -1 (anomaly) to True, 1 (normal) to False
        return [pred == -1 for pred in predictions]
    
    def get_anomaly_scores(self, transactions: List[Transaction]) -> List[float]:
        """Get anomaly scores for transactions."""
        if not transactions or not self.is_fitted:
            return [0.0] * len(transactions)
        
        features = self.extract_features(transactions)
        features_scaled = self.scaler.transform(features)
        scores = self.isolation_forest.decision_function(features_scaled)
        
        # Convert to positive scores where lower = more anomalous
        return [-score for score in scores]


class StatisticalAnomalyDetector:
    """Statistical anomaly detection using simple statistical methods."""
    
    def __init__(self, threshold_multiplier: float = 2.0):
        """Initialize the statistical detector."""
        self.threshold_multiplier = threshold_multiplier
        self.amount_stats = None
        self.frequency_stats = None
    
    def fit(self, transactions: List[Transaction]) -> None:
        """Fit the statistical model."""
        if not transactions:
            return
        
        # Calculate amount statistics
        amounts = [float(tx.amount) for tx in transactions]
        self.amount_stats = {
            'mean': np.mean(amounts),
            'std': np.std(amounts),
            'median': np.median(amounts),
            'q25': np.percentile(amounts, 25),
            'q75': np.percentile(amounts, 75)
        }
        
        # Calculate frequency statistics by entity
        entity_frequencies = {}
        for tx in transactions:
            sender = tx.sender_id
            if sender not in entity_frequencies:
                entity_frequencies[sender] = 0
            entity_frequencies[sender] += 1
        
        frequencies = list(entity_frequencies.values())
        self.frequency_stats = {
            'mean': np.mean(frequencies),
            'std': np.std(frequencies),
            'median': np.median(frequencies)
        }
    
    def detect_amount_anomalies(self, transactions: List[Transaction]) -> List[bool]:
        """Detect anomalies based on transaction amounts."""
        if not transactions or self.amount_stats is None:
            return [False] * len(transactions)
        
        anomalies = []
        for tx in transactions:
            amount = float(tx.amount)
            
            # Check if amount is outside normal range
            lower_bound = self.amount_stats['mean'] - self.threshold_multiplier * self.amount_stats['std']
            upper_bound = self.amount_stats['mean'] + self.threshold_multiplier * self.amount_stats['std']
            
            is_anomalous = amount < lower_bound or amount > upper_bound
            anomalies.append(is_anomalous)
        
        return anomalies
    
    def detect_frequency_anomalies(self, transactions: List[Transaction]) -> List[bool]:
        """Detect anomalies based on transaction frequency."""
        if not transactions or self.frequency_stats is None:
            return [False] * len(transactions)
        
        # Group transactions by sender
        sender_transactions = {}
        for i, tx in enumerate(transactions):
            sender = tx.sender_id
            if sender not in sender_transactions:
                sender_transactions[sender] = []
            sender_transactions[sender].append(i)
        
        anomalies = [False] * len(transactions)
        
        for sender, tx_indices in sender_transactions.items():
            frequency = len(tx_indices)
            
            # Check if frequency is anomalous
            threshold = self.frequency_stats['mean'] + self.threshold_multiplier * self.frequency_stats['std']
            
            if frequency > threshold:
                for idx in tx_indices:
                    anomalies[idx] = True
        
        return anomalies


class PatternDetector:
    """Detect specific patterns in transactions."""
    
    def __init__(self):
        """Initialize the pattern detector."""
        self.patterns = {
            'structuring': self._detect_structuring,
            'layering': self._detect_layering,
            'integration': self._detect_integration,
            'rapid_movement': self._detect_rapid_movement,
            'unusual_amounts': self._detect_unusual_amounts
        }
    
    def detect_patterns(self, transactions: List[Transaction]) -> Dict[str, List[Dict[str, Any]]]:
        """Detect all patterns in transactions."""
        results = {}
        
        for pattern_name, detector_func in self.patterns.items():
            results[pattern_name] = detector_func(transactions)
        
        return results
    
    def _detect_structuring(self, transactions: List[Transaction]) -> List[Dict[str, Any]]:
        """Detect structuring (breaking large amounts into smaller ones)."""
        patterns = []
        
        # Group by sender and date
        sender_date_groups = {}
        for tx in transactions:
            sender = tx.sender_id
            date = tx.timestamp.date()
            key = (sender, date)
            
            if key not in sender_date_groups:
                sender_date_groups[key] = []
            sender_date_groups[key].append(tx)
        
        # Check for structuring patterns
        for (sender, date), txs in sender_date_groups.items():
            if len(txs) < 3:  # Need multiple transactions
                continue
            
            total_amount = sum(float(tx.amount) for tx in txs)
            amounts = [float(tx.amount) for tx in txs]
            
            # Check if total is large but individual amounts are small
            if total_amount > 10000 and all(amount < 10000 for amount in amounts):
                patterns.append({
                    'sender': sender,
                    'date': date.isoformat(),
                    'total_amount': total_amount,
                    'transaction_count': len(txs),
                    'amounts': amounts,
                    'confidence': 0.8
                })
        
        return patterns
    
    def _detect_layering(self, transactions: List[Transaction]) -> List[Dict[str, Any]]:
        """Detect layering (complex transaction chains)."""
        patterns = []
        
        # Look for chains of transactions
        transaction_map = {tx.id: tx for tx in transactions}
        
        for tx in transactions:
            if not tx.reference:  # Skip if no reference
                continue
            
            # Follow transaction chain
            chain = [tx]
            current_tx = tx
            
            for _ in range(10):  # Limit chain length
                # Find next transaction in chain
                next_txs = [t for t in transactions if t.sender_id == current_tx.recipient_id]
                if not next_txs:
                    break
                
                # Find the one that happens soon after
                current_time = current_tx.timestamp
                next_tx = None
                for nt in next_txs:
                    if (nt.timestamp - current_time).total_seconds() < 3600:  # Within 1 hour
                        next_tx = nt
                        break
                
                if not next_tx or next_tx in chain:
                    break
                
                chain.append(next_tx)
                current_tx = next_tx
            
            # If chain is long enough, it might be layering
            if len(chain) >= 3:
                patterns.append({
                    'chain_length': len(chain),
                    'total_amount': sum(float(t.amount) for t in chain),
                    'entities_involved': len(set(t.sender_id for t in chain) | set(t.recipient_id for t in chain)),
                    'time_span': (chain[-1].timestamp - chain[0].timestamp).total_seconds() / 3600,
                    'confidence': min(0.9, len(chain) * 0.2)
                })
        
        return patterns
    
    def _detect_integration(self, transactions: List[Transaction]) -> List[Dict[str, Any]]:
        """Detect integration (bringing funds into legitimate system)."""
        patterns = []
        
        # Look for large deposits from unknown sources
        for tx in transactions:
            if tx.transaction_type.value == "deposit" and float(tx.amount) > 50000:
                patterns.append({
                    'transaction_id': tx.id,
                    'amount': float(tx.amount),
                    'recipient': tx.recipient_id,
                    'confidence': 0.7
                })
        
        return patterns
    
    def _detect_rapid_movement(self, transactions: List[Transaction]) -> List[Dict[str, Any]]:
        """Detect rapid movement of funds."""
        patterns = []
        
        # Group by entity
        entity_transactions = {}
        for tx in transactions:
            sender = tx.sender_id
            if sender not in entity_transactions:
                entity_transactions[sender] = []
            entity_transactions[sender].append(tx)
        
        for entity, txs in entity_transactions.items():
            if len(txs) < 2:
                continue
            
            # Sort by timestamp
            txs.sort(key=lambda x: x.timestamp)
            
            # Check for rapid movements
            for i in range(len(txs) - 1):
                time_diff = (txs[i+1].timestamp - txs[i].timestamp).total_seconds()
                if time_diff < 300:  # Less than 5 minutes
                    patterns.append({
                        'entity': entity,
                        'time_diff_seconds': time_diff,
                        'amount1': float(txs[i].amount),
                        'amount2': float(txs[i+1].amount),
                        'confidence': 0.8
                    })
        
        return patterns
    
    def _detect_unusual_amounts(self, transactions: List[Transaction]) -> List[Dict[str, Any]]:
        """Detect unusual transaction amounts."""
        patterns = []
        
        amounts = [float(tx.amount) for tx in transactions]
        if not amounts:
            return patterns
        
        # Calculate statistics
        mean_amount = np.mean(amounts)
        std_amount = np.std(amounts)
        
        for tx in transactions:
            amount = float(tx.amount)
            
            # Check for amounts that are significantly different
            z_score = abs(amount - mean_amount) / std_amount if std_amount > 0 else 0
            
            if z_score > 3:  # More than 3 standard deviations
                patterns.append({
                    'transaction_id': tx.id,
                    'amount': amount,
                    'z_score': z_score,
                    'entity': tx.sender_id,
                    'confidence': min(0.9, z_score * 0.2)
                })
        
        return patterns 