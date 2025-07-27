# Multi-Agent Orchestration Platform - AML MVP

A minimal viable product (MVP) of a multi-agent orchestration platform for anti-money laundering (AML) use cases. This platform uses LangChain to orchestrate multiple AI agents that work together to analyze transactions, detect suspicious patterns, and generate compliance reports.

## Features

- **Planner Agent**: Parses user queries and creates task graphs
- **Retriever Agent**: Fetches transaction data and external documents via RAG
- **Analysis Agent**: Runs anomaly detection algorithms on transactions
- **Compliance Agent**: Checks patterns against AML regulations
- **Synthesizer Agent**: Aggregates findings into structured reports
- **Verifier Agent**: Implements multi-agent verification with consensus
- **Orchestrator**: Manages task flow and agent communication

## Architecture

The platform uses LangChain's agent framework with:
- Asynchronous message bus for agent communication
- Vector store for document retrieval (RAG)
- OpenAI GPT models for natural language processing
- Statistical anomaly detection algorithms
- Multi-agent verification system

## Setup

### 1. Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd Orchectra

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
LOG_LEVEL=INFO
```

### 3. Data Setup

Place your transaction data in the `data/` directory:
- `transactions.csv` - Transaction data
- `regulatory_docs/` - Regulatory documents for RAG

## Usage

### Running the Platform

```bash
# Start the orchestrator
python -m orchestrator.main

# Or run with specific configuration
python -m orchestrator.main --config config.yaml
```

### API Usage

```python
from orchestrator.main import Orchestrator

# Initialize orchestrator
orchestrator = Orchestrator()

# Submit a query
result = await orchestrator.process_query(
    "Analyze transactions for suspicious patterns in the last 30 days"
)

print(result.report)
```

### Web Dashboard

```bash
# Start Streamlit dashboard
streamlit run dashboard/app.py
```

## Testing

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/test_agents.py
pytest tests/test_orchestrator.py
pytest tests/test_integration.py

# Run with coverage
pytest --cov=orchestrator tests/
```

## Project Structure

```
Orchectra/
├── orchestrator/
│   ├── __init__.py
│   ├── main.py              # Main orchestrator
│   ├── agents/              # Agent implementations
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── planner.py
│   │   ├── retriever.py
│   │   ├── analysis.py
│   │   ├── compliance.py
│   │   ├── synthesizer.py
│   │   └── verifier.py
│   ├── models/              # Data models
│   │   ├── __init__.py
│   │   ├── task.py
│   │   ├── report.py
│   │   └── transaction.py
│   ├── utils/               # Utilities
│   │   ├── __init__.py
│   │   ├── vector_store.py
│   │   ├── anomaly_detection.py
│   │   └── logging.py
│   └── config/              # Configuration
│       ├── __init__.py
│       └── settings.py
├── dashboard/               # Web dashboard
│   ├── app.py
│   └── components/
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── test_agents.py
│   ├── test_orchestrator.py
│   └── test_integration.py
├── data/                    # Sample data
│   ├── transactions.csv
│   └── regulatory_docs/
├── requirements.txt
├── README.md
└── .env.example
```

## API Reference

### Orchestrator

The main orchestrator class that manages the multi-agent system.

```python
class Orchestrator:
    async def process_query(self, query: str) -> Report
    async def get_agent_logs(self) -> List[LogEntry]
    async def get_task_status(self, task_id: str) -> TaskStatus
```

### Agents

Each agent implements the base Agent interface:

```python
class Agent:
    async def process(self, task: Task) -> TaskResult
    async def validate_input(self, task: Task) -> bool
    async def handle_error(self, error: Exception) -> None
```

## Configuration

The platform can be configured via environment variables or a YAML config file:

```yaml
# config.yaml
openai:
  model: gpt-4
  temperature: 0.1
  max_tokens: 2000

agents:
  planner:
    max_tasks: 10
  retriever:
    top_k: 5
    similarity_threshold: 0.7
  analysis:
    anomaly_threshold: 0.05
  verifier:
    consensus_threshold: 0.8

logging:
  level: INFO
  file: logs/orchestrator.log
```

## Security Considerations

- API keys are loaded from environment variables
- Sensitive data is not logged
- Input validation is performed on all user queries
- Rate limiting is implemented for API calls

## Performance

- Asynchronous processing for concurrent agent execution
- Vector store caching for document retrieval
- Model parameter sharing to reduce costs
- Efficient task scheduling and routing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details. 