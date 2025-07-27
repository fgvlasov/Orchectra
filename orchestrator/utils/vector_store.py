"""
Vector store utility for document retrieval and RAG functionality.
"""

import os
import pickle
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from ..config.settings import settings


class VectorStore:
    """In-memory vector store for document retrieval."""
    
    def __init__(self, embedding_model_name: Optional[str] = None):
        """Initialize the vector store."""
        self.embedding_model_name = embedding_model_name or settings.embedding_model
        self.embedding_model = SentenceTransformer(self.embedding_model_name)
        self.index = None
        self.documents: List[Document] = []
        self.metadata: List[Dict[str, Any]] = []
        
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the vector store."""
        if not documents:
            return
            
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        split_docs = []
        for doc in documents:
            splits = text_splitter.split_documents([doc])
            split_docs.extend(splits)
        
        # Generate embeddings
        texts = [doc.page_content for doc in split_docs]
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
        
        # Initialize or update FAISS index
        if self.index is None:
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings.astype('float32'))
        
        # Store documents and metadata
        self.documents.extend(split_docs)
        for doc in split_docs:
            self.metadata.append(doc.metadata)
    
    def similarity_search(
        self, 
        query: str, 
        k: int = 5, 
        threshold: float = 0.7
    ) -> List[Tuple[Document, float]]:
        """Search for similar documents."""
        if self.index is None or len(self.documents) == 0:
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(
            query_embedding.astype('float32'), 
            min(k, len(self.documents))
        )
        
        # Filter by threshold and return results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if score >= threshold and idx < len(self.documents):
                results.append((self.documents[idx], float(score)))
        
        return results
    
    def add_texts(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> None:
        """Add raw texts to the vector store."""
        if metadatas is None:
            metadatas = [{} for _ in texts]
        
        documents = [
            Document(page_content=text, metadata=metadata)
            for text, metadata in zip(texts, metadatas)
        ]
        self.add_documents(documents)
    
    def save(self, path: str) -> None:
        """Save the vector store to disk."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, f"{path}.index")
        
        # Save documents and metadata
        with open(f"{path}.pkl", "wb") as f:
            pickle.dump({
                "documents": self.documents,
                "metadata": self.metadata,
                "embedding_model_name": self.embedding_model_name
            }, f)
    
    def load(self, path: str) -> None:
        """Load the vector store from disk."""
        # Load FAISS index
        self.index = faiss.read_index(f"{path}.index")
        
        # Load documents and metadata
        with open(f"{path}.pkl", "rb") as f:
            data = pickle.load(f)
            self.documents = data["documents"]
            self.metadata = data["metadata"]
            self.embedding_model_name = data["embedding_model_name"]
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        return {
            "total_documents": len(self.documents),
            "index_size": self.index.ntotal if self.index else 0,
            "embedding_model": self.embedding_model_name,
            "dimension": self.index.d if self.index else 0
        }


class DocumentRetriever:
    """Document retriever with query rewriting capabilities."""
    
    def __init__(self, vector_store: VectorStore):
        """Initialize the document retriever."""
        self.vector_store = vector_store
        self.query_cache: Dict[str, List[Tuple[Document, float]]] = {}
    
    def retrieve(
        self, 
        query: str, 
        k: int = 5, 
        threshold: float = 0.7,
        use_cache: bool = True
    ) -> List[Tuple[Document, float]]:
        """Retrieve documents for a query."""
        if use_cache and query in self.query_cache:
            return self.query_cache[query]
        
        # Perform similarity search
        results = self.vector_store.similarity_search(query, k, threshold)
        
        # Cache results
        if use_cache:
            self.query_cache[query] = results
        
        return results
    
    def retrieve_with_rewriting(
        self, 
        query: str, 
        k: int = 5, 
        threshold: float = 0.7
    ) -> List[Tuple[Document, float]]:
        """Retrieve documents with query rewriting."""
        # Simple query rewriting - expand with synonyms
        expanded_queries = self._expand_query(query)
        
        all_results = []
        for expanded_query in expanded_queries:
            results = self.retrieve(expanded_query, k, threshold, use_cache=False)
            all_results.extend(results)
        
        # Remove duplicates and sort by score
        unique_results = {}
        for doc, score in all_results:
            doc_id = doc.page_content[:100]  # Simple deduplication
            if doc_id not in unique_results or score > unique_results[doc_id][1]:
                unique_results[doc_id] = (doc, score)
        
        # Sort by score and return top k
        sorted_results = sorted(unique_results.values(), key=lambda x: x[1], reverse=True)
        return sorted_results[:k]
    
    def _expand_query(self, query: str) -> List[str]:
        """Expand query with synonyms and related terms."""
        # Simple expansion - in a real system, this would use a thesaurus or LLM
        expansions = [query]
        
        # Add common AML-related terms
        aml_terms = {
            "suspicious": ["suspicious", "unusual", "anomalous", "strange"],
            "transaction": ["transaction", "transfer", "payment", "movement"],
            "money": ["money", "funds", "cash", "currency"],
            "laundering": ["laundering", "washing", "cleaning", "concealing"]
        }
        
        for term, synonyms in aml_terms.items():
            if term.lower() in query.lower():
                for synonym in synonyms:
                    if synonym != term:
                        expanded = query.lower().replace(term.lower(), synonym)
                        if expanded != query.lower():
                            expansions.append(expanded)
        
        return list(set(expansions))
    
    def clear_cache(self) -> None:
        """Clear the query cache."""
        self.query_cache.clear() 