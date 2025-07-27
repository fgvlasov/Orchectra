"""
Configuration settings for the orchestrator platform.
"""

import os
from typing import Optional
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class OpenAISettings(BaseSettings):
    """OpenAI API configuration."""
    api_key: str = Field(..., env="OPENAI_API_KEY")
    model: str = Field(default="gpt-4", env="OPENAI_MODEL")
    temperature: float = Field(default=0.1, env="OPENAI_TEMPERATURE")
    max_tokens: int = Field(default=2000, env="OPENAI_MAX_TOKENS")
    
    class Config:
        env_prefix = "OPENAI_"


class AgentSettings(BaseSettings):
    """Agent-specific configuration."""
    planner_max_tasks: int = Field(default=10, env="PLANNER_MAX_TASKS")
    retriever_top_k: int = Field(default=5, env="RETRIEVER_TOP_K")
    retriever_similarity_threshold: float = Field(default=0.7, env="RETRIEVER_SIMILARITY_THRESHOLD")
    analysis_anomaly_threshold: float = Field(default=0.05, env="ANALYSIS_ANOMALY_THRESHOLD")
    verifier_consensus_threshold: float = Field(default=0.8, env="VERIFIER_CONSENSUS_THRESHOLD")
    
    class Config:
        env_prefix = "AGENT_"


class LoggingSettings(BaseSettings):
    """Logging configuration."""
    level: str = Field(default="INFO", env="LOG_LEVEL")
    file: Optional[str] = Field(default=None, env="LOG_FILE")
    
    class Config:
        env_prefix = "LOG_"


class Settings(BaseSettings):
    """Main application settings."""
    openai: OpenAISettings = OpenAISettings()
    agents: AgentSettings = AgentSettings()
    logging: LoggingSettings = LoggingSettings()
    
    # Data paths
    data_dir: str = Field(default="data", env="DATA_DIR")
    transactions_file: str = Field(default="transactions.csv", env="TRANSACTIONS_FILE")
    regulatory_docs_dir: str = Field(default="regulatory_docs", env="REGULATORY_DOCS_DIR")
    
    # Vector store settings
    vector_store_path: str = Field(default="vector_store", env="VECTOR_STORE_PATH")
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    
    # API settings
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings() 