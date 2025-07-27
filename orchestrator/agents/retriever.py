"""
Retriever agent for fetching transaction data and regulatory documents.
"""

import pandas as pd
from typing import Dict, Any, List, Optional
from pathlib import Path

from ..models.task import Task, TaskResult, TaskType
from ..models.transaction import Transaction, TransactionBatch, TransactionType, RiskLevel
from ..utils.vector_store import VectorStore, DocumentRetriever
from ..config.settings import settings
from .base import BaseAgent


class RetrieverAgent(BaseAgent):
    """Agent responsible for retrieving transaction data and documents."""
    
    def __init__(self, name: str = "retriever"):
        """Initialize the retriever agent."""
        super().__init__(name)
        self.vector_store = VectorStore()
        self.document_retriever = DocumentRetriever(self.vector_store)
        self._load_sample_data()
    
    def _load_sample_data(self):
        """Load sample transaction data and regulatory documents."""
        # Load sample transactions
        self.sample_transactions = self._create_sample_transactions()
        
        # Load sample regulatory documents
        self.sample_documents = self._create_sample_documents()
        
        # Add documents to vector store
        self.vector_store.add_texts(
            [doc["content"] for doc in self.sample_documents],
            [{"source": doc["source"], "title": doc["title"]} for doc in self.sample_documents]
        )
    
    def _create_sample_transactions(self) -> List[Transaction]:
        """Create sample transaction data for testing."""
        import random
        from datetime import datetime, timedelta
        
        transactions = []
        entities = ["entity_001", "entity_002", "entity_003", "entity_004", "entity_005"]
        amounts = [100, 500, 1000, 5000, 10000, 50000, 100000]
        
        # Create some normal transactions
        for i in range(50):
            tx = Transaction(
                timestamp=datetime.now() - timedelta(days=random.randint(1, 30)),
                amount=random.choice(amounts),
                transaction_type=random.choice(list(TransactionType)),
                sender_id=random.choice(entities),
                recipient_id=random.choice(entities),
                description=f"Sample transaction {i}",
                risk_level=RiskLevel.LOW
            )
            transactions.append(tx)
        
        # Create some suspicious transactions
        suspicious_patterns = [
            # Structuring pattern
            {"amount": 9500, "count": 5, "entity": "entity_001"},
            # Large amounts
            {"amount": 75000, "count": 2, "entity": "entity_002"},
            # Rapid movements
            {"amount": 5000, "count": 3, "entity": "entity_003"}
        ]
        
        for pattern in suspicious_patterns:
            for j in range(pattern["count"]):
                tx = Transaction(
                    timestamp=datetime.now() - timedelta(hours=j),
                    amount=pattern["amount"],
                    transaction_type=TransactionType.TRANSFER,
                    sender_id=pattern["entity"],
                    recipient_id=f"entity_{random.randint(100, 999)}",
                    description=f"Suspicious transaction {j}",
                    risk_level=RiskLevel.HIGH
                )
                transactions.append(tx)
        
        return transactions
    
    def _create_sample_documents(self) -> List[Dict[str, str]]:
        """Create sample regulatory documents."""
        return [
            {
                "title": "Bank Secrecy Act (BSA)",
                "source": "regulatory_docs/bsa.txt",
                "content": """
                The Bank Secrecy Act (BSA) requires financial institutions to assist U.S. government agencies 
                in detecting and preventing money laundering. Key requirements include:
                - Currency Transaction Reports (CTRs) for transactions over $10,000
                - Suspicious Activity Reports (SARs) for suspicious transactions
                - Customer identification and verification
                - Record keeping requirements
                - Reporting of international transactions
                """
            },
            {
                "title": "USA PATRIOT Act",
                "source": "regulatory_docs/patriot_act.txt",
                "content": """
                The USA PATRIOT Act enhances the BSA and includes provisions for:
                - Customer Due Diligence (CDD) requirements
                - Enhanced Due Diligence (EDD) for high-risk customers
                - Information sharing between financial institutions
                - Correspondent account requirements
                - Special measures for jurisdictions of primary money laundering concern
                """
            },
            {
                "title": "OFAC Sanctions",
                "source": "regulatory_docs/ofac.txt",
                "content": """
                Office of Foreign Assets Control (OFAC) sanctions prohibit transactions with:
                - Specially Designated Nationals (SDNs)
                - Blocked persons and entities
                - Sanctioned countries and regions
                - Terrorist organizations
                Financial institutions must screen transactions and customers against OFAC lists.
                """
            },
            {
                "title": "Structuring Detection",
                "source": "regulatory_docs/structuring.txt",
                "content": """
                Structuring is the practice of breaking large transactions into smaller amounts to avoid 
                reporting requirements. Indicators include:
                - Multiple transactions just under reporting thresholds
                - Transactions by same person on same day
                - Unusual patterns of deposits or withdrawals
                - Coordination between multiple accounts
                - Use of multiple financial institutions
                """
            },
            {
                "title": "Layering Detection",
                "source": "regulatory_docs/layering.txt",
                "content": """
                Layering involves creating complex transaction chains to obscure the source of funds:
                - Multiple transfers between accounts
                - Use of shell companies
                - International wire transfers
                - Currency exchanges
                - Investment in complex financial products
                - Use of nominees or intermediaries
                """
            }
        ]
    
    async def process_task(self, task: Task) -> TaskResult:
        """Process a retrieval task."""
        try:
            query = task.payload.get("query", "")
            data_sources = task.payload.get("data_sources", ["transactions", "regulatory_docs"])
            time_range = task.payload.get("time_range", "last_30_days")
            
            results = {}
            
            # Retrieve transaction data
            if "transactions" in data_sources:
                transactions = await self._retrieve_transactions(query, time_range)
                results["transactions"] = transactions
            
            # Retrieve regulatory documents
            if "regulatory_docs" in data_sources:
                documents = await self._retrieve_documents(query)
                results["documents"] = documents
            
            return TaskResult(
                task_id=task.id,
                success=True,
                data=results,
                agent_name=self.name
            )
            
        except Exception as e:
            return await self.handle_error(e, task)
    
    async def _retrieve_transactions(self, query: str, time_range: str) -> Dict[str, Any]:
        """Retrieve transaction data based on query."""
        # Filter transactions based on query and time range
        filtered_transactions = []
        
        for tx in self.sample_transactions:
            # Simple filtering logic - in a real system, this would be more sophisticated
            if self._matches_query(tx, query):
                filtered_transactions.append(tx)
        
        # Create transaction batch
        batch = TransactionBatch(
            transactions=filtered_transactions,
            source="retriever_agent",
            metadata={"query": query, "time_range": time_range}
        )
        
        return {
            "batch_id": batch.id,
            "transaction_count": len(filtered_transactions),
            "total_amount": float(batch.get_total_amount()),
            "high_risk_count": len(batch.get_high_risk_transactions()),
            "transactions": [self._transaction_to_dict(tx) for tx in filtered_transactions]
        }
    
    async def _retrieve_documents(self, query: str) -> Dict[str, Any]:
        """Retrieve relevant regulatory documents."""
        # Use vector search to find relevant documents
        results = self.document_retriever.retrieve_with_rewriting(
            query, 
            k=settings.agents.retriever_top_k,
            threshold=settings.agents.retriever_similarity_threshold
        )
        
        documents = []
        for doc, score in results:
            documents.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "relevance_score": score
            })
        
        return {
            "document_count": len(documents),
            "documents": documents
        }
    
    def _matches_query(self, transaction: Transaction, query: str) -> bool:
        """Check if transaction matches the query."""
        query_lower = query.lower()
        
        # Check for suspicious keywords
        suspicious_keywords = ["suspicious", "anomalous", "unusual", "high risk", "structuring", "layering"]
        if any(keyword in query_lower for keyword in suspicious_keywords):
            return transaction.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        
        # Check for amount-based queries
        if "large" in query_lower or "high value" in query_lower:
            return float(transaction.amount) > 10000
        
        # Check for frequency-based queries
        if "frequent" in query_lower or "multiple" in query_lower:
            return True  # Would need more sophisticated logic in real system
        
        # Default: return all transactions
        return True
    
    def _transaction_to_dict(self, transaction: Transaction) -> Dict[str, Any]:
        """Convert transaction to dictionary for serialization."""
        return {
            "id": transaction.id,
            "timestamp": transaction.timestamp.isoformat(),
            "amount": float(transaction.amount),
            "currency": transaction.currency,
            "transaction_type": transaction.transaction_type.value,
            "sender_id": transaction.sender_id,
            "recipient_id": transaction.recipient_id,
            "sender_name": transaction.sender_name,
            "recipient_name": transaction.recipient_name,
            "description": transaction.description,
            "reference": transaction.reference,
            "risk_level": transaction.risk_level.value,
            "metadata": transaction.metadata
        }
    
    async def validate_input(self, task: Task) -> bool:
        """Validate retriever task input."""
        if not await super().validate_input(task):
            return False
        
        # Check for required fields
        if "query" not in task.payload:
            return False
        
        return True 