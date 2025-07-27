#!/usr/bin/env python3
"""
Example script demonstrating the AML Orchestrator functionality.

This script shows how to use the multi-agent orchestration platform
for anti-money laundering analysis.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

from orchestrator.main import Orchestrator
from orchestrator.models.task import Task, TaskType
from orchestrator.agents import (
    PlannerAgent, RetrieverAgent, AnalysisAgent,
    ComplianceAgent, VerifierAgent, SynthesizerAgent
)


async def example_basic_usage():
    """Example of basic orchestrator usage."""
    print("🔍 AML Orchestrator - Basic Usage Example")
    print("=" * 50)
    
    # Initialize orchestrator
    orchestrator = Orchestrator()
    
    # Example query
    query = "Analyze transactions for suspicious patterns in the last 30 days"
    print(f"Query: {query}")
    
    try:
        # Process the query (this would normally run the full pipeline)
        print("\n📋 Processing query through multi-agent pipeline...")
        
        # For demonstration, we'll show the individual agent steps
        await demonstrate_agent_workflow(query)
        
        print("\n✅ Analysis completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during processing: {e}")


async def demonstrate_agent_workflow(query: str):
    """Demonstrate the workflow of individual agents."""
    print("\n🤖 Agent Workflow Demonstration")
    print("-" * 40)
    
    # 1. Planner Agent
    print("\n1. 📝 Planner Agent")
    planner = PlannerAgent()
    plan_task = Task(type=TaskType.PLAN, payload={"query": query})
    plan_result = await planner.process_task(plan_task)
    
    if plan_result.success:
        print(f"   ✅ Created task graph with {plan_result.data.get('total_tasks', 0)} tasks")
    else:
        print(f"   ❌ Planning failed: {plan_result.error}")
        return
    
    # 2. Retriever Agent
    print("\n2. 🔍 Retriever Agent")
    retriever = RetrieverAgent()
    retrieve_task = Task(type=TaskType.RETRIEVE, payload={"query": query})
    retrieve_result = await retriever.process_task(retrieve_task)
    
    if retrieve_result.success:
        transaction_data = retrieve_result.data.get("transactions", {})
        print(f"   ✅ Retrieved {transaction_data.get('transaction_count', 0)} transactions")
        print(f"   ✅ Found {transaction_data.get('high_risk_count', 0)} high-risk transactions")
    else:
        print(f"   ❌ Retrieval failed: {retrieve_result.error}")
        return
    
    # 3. Analysis Agent
    print("\n3. 📊 Analysis Agent")
    analysis = AnalysisAgent()
    analysis_task = Task(
        type=TaskType.ANALYZE,
        payload={
            "transactions": retrieve_result.data.get("transactions", {}),
            "analysis_types": ["anomaly_detection", "pattern_detection"]
        }
    )
    analysis_result = await analysis.process_task(analysis_task)
    
    if analysis_result.success:
        anomalies = analysis_result.data.get("anomalies", {})
        patterns = analysis_result.data.get("patterns", {})
        suspicious_patterns = analysis_result.data.get("suspicious_patterns", [])
        
        print(f"   ✅ Detected {anomalies.get('total_anomalies', 0)} anomalies")
        print(f"   ✅ Found {patterns.get('total_patterns', 0)} patterns")
        print(f"   ✅ Identified {len(suspicious_patterns)} suspicious patterns")
    else:
        print(f"   ❌ Analysis failed: {analysis_result.error}")
        return
    
    # 4. Compliance Agent
    print("\n4. ⚖️ Compliance Agent")
    compliance = ComplianceAgent()
    compliance_task = Task(
        type=TaskType.COMPLIANCE_CHECK,
        payload={
            "suspicious_patterns": suspicious_patterns,
            "regulations": ["BSA", "PATRIOT_Act", "OFAC"]
        }
    )
    compliance_result = await compliance.process_task(compliance_task)
    
    if compliance_result.success:
        compliance_checks = compliance_result.data.get("compliance_checks", [])
        summary = compliance_result.data.get("summary", {})
        
        print(f"   ✅ Performed {len(compliance_checks)} compliance checks")
        print(f"   ✅ Found {summary.get('non_compliant', 0)} non-compliant patterns")
        print(f"   ✅ {summary.get('requires_review', 0)} patterns require review")
    else:
        print(f"   ❌ Compliance check failed: {compliance_result.error}")
        return
    
    # 5. Verifier Agent
    print("\n5. 🔐 Verifier Agent")
    verifier = VerifierAgent()
    verify_task = Task(
        type=TaskType.VERIFY,
        payload={
            "suspicious_patterns": suspicious_patterns,
            "verification_method": "multi_agent_consensus",
            "consensus_threshold": 0.8
        }
    )
    verify_result = await verifier.process_task(verify_task)
    
    if verify_result.success:
        verification_results = verify_result.data.get("verification_results", [])
        summary = verify_result.data.get("summary", {})
        
        print(f"   ✅ Verified {len(verification_results)} patterns")
        print(f"   ✅ Consensus reached on {summary.get('consensus_reached', 0)} patterns")
        print(f"   ✅ {summary.get('human_review_needed', 0)} patterns need human review")
    else:
        print(f"   ❌ Verification failed: {verify_result.error}")
        return
    
    # 6. Synthesizer Agent
    print("\n6. 📋 Synthesizer Agent")
    synthesizer = SynthesizerAgent()
    synthesize_task = Task(
        type=TaskType.SYNTHESIZE,
        payload={
            "transactions": retrieve_result.data.get("transactions", {}),
            "analysis_results": analysis_result.data,
            "compliance_results": compliance_result.data,
            "verification_results": verify_result.data,
            "report_type": "aml_analysis",
            "include_recommendations": True
        }
    )
    synthesize_result = await synthesizer.process_task(synthesize_task)
    
    if synthesize_result.success:
        report_data = synthesize_result.data.get("report", {})
        summary = synthesize_result.data.get("summary", {})
        
        print(f"   ✅ Generated comprehensive report")
        print(f"   📊 Report ID: {synthesize_result.data.get('report_id', 'N/A')}")
        print(f"   📊 Total patterns: {summary.get('total_patterns', 0)}")
        print(f"   📊 High-risk patterns: {summary.get('high_risk_patterns', 0)}")
        print(f"   📊 Compliance violations: {summary.get('compliance_violations', 0)}")
    else:
        print(f"   ❌ Synthesis failed: {synthesize_result.error}")


async def example_advanced_features():
    """Example of advanced orchestrator features."""
    print("\n🔧 AML Orchestrator - Advanced Features Example")
    print("=" * 50)
    
    orchestrator = Orchestrator()
    
    # Example 1: Custom query with specific focus
    print("\n📝 Example 1: Structuring Detection")
    structuring_query = "Detect potential structuring patterns in transactions under $10,000"
    
    # Example 2: Layering detection
    print("\n📝 Example 2: Layering Detection")
    layering_query = "Identify complex transaction chains that might indicate layering"
    
    # Example 3: Integration detection
    print("\n📝 Example 3: Integration Detection")
    integration_query = "Find large deposits from unknown sources that might indicate integration"
    
    print("\nThese queries would be processed through the full multi-agent pipeline:")
    print("1. Planner creates task graph")
    print("2. Retriever fetches relevant data")
    print("3. Analysis detects patterns")
    print("4. Compliance checks regulations")
    print("5. Verifier ensures consensus")
    print("6. Synthesizer generates report")


def example_configuration():
    """Example of configuration options."""
    print("\n⚙️ Configuration Examples")
    print("=" * 30)
    
    config_examples = {
        "Agent Settings": {
            "planner_max_tasks": 10,
            "retriever_top_k": 5,
            "retriever_similarity_threshold": 0.7,
            "analysis_anomaly_threshold": 0.05,
            "verifier_consensus_threshold": 0.8
        },
        "Model Settings": {
            "openai_model": "gpt-4",
            "temperature": 0.1,
            "max_tokens": 2000
        },
        "Detection Patterns": [
            "structuring",
            "layering", 
            "integration",
            "rapid_movement",
            "unusual_amounts"
        ],
        "Regulations": [
            "Bank Secrecy Act (BSA)",
            "USA PATRIOT Act",
            "OFAC Sanctions"
        ]
    }
    
    for category, settings in config_examples.items():
        print(f"\n{category}:")
        if isinstance(settings, dict):
            for key, value in settings.items():
                print(f"  {key}: {value}")
        else:
            for item in settings:
                print(f"  - {item}")


def example_output_formats():
    """Example of output formats and reports."""
    print("\n📊 Output Format Examples")
    print("=" * 30)
    
    # Example report structure
    example_report = {
        "id": "report_2024_001",
        "title": "AML Analysis Report - Q1 2024",
        "status": "completed",
        "created_at": "2024-01-15T10:00:00Z",
        "summary": {
            "total_transactions_analyzed": 1500,
            "total_amount_analyzed": 2500000.00,
            "suspicious_patterns_found": 12,
            "high_risk_patterns": 3,
            "compliance_violations": 2,
            "patterns_requiring_review": 1
        },
        "patterns": [
            {
                "type": "structuring",
                "confidence": 0.85,
                "risk_level": "high",
                "affected_transactions": 5,
                "total_amount": 47500.00,
                "indicators": [
                    "Multiple transactions under $10,000",
                    "Same entity involved",
                    "Same day transactions"
                ]
            }
        ],
        "recommendations": [
            "File Suspicious Activity Report (SAR)",
            "Implement enhanced monitoring",
            "Conduct customer due diligence review"
        ]
    }
    
    print("Example Report Structure:")
    print(json.dumps(example_report, indent=2))


async def main():
    """Main example function."""
    print("🚀 AML Orchestrator Platform - Example Usage")
    print("=" * 60)
    
    # Basic usage example
    await example_basic_usage()
    
    # Advanced features example
    await example_advanced_features()
    
    # Configuration examples
    example_configuration()
    
    # Output format examples
    example_output_formats()
    
    print("\n" + "=" * 60)
    print("✅ Example completed successfully!")
    print("\nTo run the actual orchestrator:")
    print("1. Set up your .env file with OpenAI API key")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Run: python -m orchestrator.main")
    print("4. Or start the dashboard: streamlit run dashboard/app.py")


if __name__ == "__main__":
    asyncio.run(main()) 