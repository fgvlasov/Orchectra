"""
Streamlit dashboard for the AML Orchestrator.
"""

import streamlit as st
import asyncio
import json
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Mock data for demonstration
def get_mock_data():
    """Get mock data for the dashboard."""
    return {
        "agents": {
            "planner": {"status": "running", "processed_tasks": 15, "success_rate": 0.93},
            "retriever": {"status": "running", "processed_tasks": 42, "success_rate": 0.98},
            "analysis": {"status": "running", "processed_tasks": 38, "success_rate": 0.95},
            "compliance": {"status": "running", "processed_tasks": 35, "success_rate": 0.97},
            "verifier": {"status": "running", "processed_tasks": 32, "success_rate": 0.94},
            "synthesizer": {"status": "running", "processed_tasks": 28, "success_rate": 0.96}
        },
        "reports": [
            {
                "id": "report_001",
                "title": "AML Analysis Report - Q1 2024",
                "status": "completed",
                "created_at": "2024-01-15T10:00:00",
                "total_patterns": 12,
                "high_risk_patterns": 3,
                "compliance_violations": 2
            },
            {
                "id": "report_002", 
                "title": "Suspicious Activity Analysis",
                "status": "pending_review",
                "created_at": "2024-01-16T14:30:00",
                "total_patterns": 8,
                "high_risk_patterns": 1,
                "compliance_violations": 0
            }
        ],
        "patterns": [
            {"type": "structuring", "count": 5, "risk_level": "high"},
            {"type": "layering", "count": 3, "risk_level": "critical"},
            {"type": "integration", "count": 2, "risk_level": "medium"},
            {"type": "rapid_movement", "count": 4, "risk_level": "high"},
            {"type": "unusual_amounts", "count": 6, "risk_level": "medium"}
        ]
    }

def main():
    """Main dashboard function."""
    st.set_page_config(
        page_title="AML Orchestrator Dashboard",
        page_icon="🔍",
        layout="wide"
    )
    
    st.title("🔍 AML Orchestrator Dashboard")
    st.markdown("Multi-Agent Anti-Money Laundering Analysis Platform")
    
    # Sidebar
    st.sidebar.header("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Overview", "Agents", "Reports", "Patterns", "Settings"]
    )
    
    # Get mock data
    data = get_mock_data()
    
    if page == "Overview":
        show_overview(data)
    elif page == "Agents":
        show_agents(data)
    elif page == "Reports":
        show_reports(data)
    elif page == "Patterns":
        show_patterns(data)
    elif page == "Settings":
        show_settings()

def show_overview(data):
    """Show overview dashboard."""
    st.header("System Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Active Agents",
            value=len([a for a in data["agents"].values() if a["status"] == "running"]),
            delta="6/6"
        )
    
    with col2:
        total_tasks = sum(a["processed_tasks"] for a in data["agents"].values())
        st.metric(
            label="Total Tasks Processed",
            value=total_tasks,
            delta="+15 today"
        )
    
    with col3:
        avg_success = sum(a["success_rate"] for a in data["agents"].values()) / len(data["agents"])
        st.metric(
            label="Average Success Rate",
            value=f"{avg_success:.1%}",
            delta="+2.3%"
        )
    
    with col4:
        total_patterns = sum(r["total_patterns"] for r in data["reports"])
        st.metric(
            label="Patterns Detected",
            value=total_patterns,
            delta="+8 this week"
        )
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Agent Performance")
        agent_df = pd.DataFrame([
            {
                "Agent": name,
                "Tasks Processed": info["processed_tasks"],
                "Success Rate": info["success_rate"]
            }
            for name, info in data["agents"].items()
        ])
        
        fig = px.bar(
            agent_df,
            x="Agent",
            y="Tasks Processed",
            color="Success Rate",
            color_continuous_scale="RdYlGn"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Pattern Distribution")
        pattern_df = pd.DataFrame(data["patterns"])
        
        fig = px.pie(
            pattern_df,
            values="count",
            names="type",
            title="Detected Pattern Types"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent activity
    st.subheader("Recent Activity")
    activity_data = [
        {"time": "10:30 AM", "agent": "planner", "action": "Created task graph for new query"},
        {"time": "10:32 AM", "agent": "retriever", "action": "Retrieved 150 transactions"},
        {"time": "10:35 AM", "agent": "analysis", "action": "Detected 3 suspicious patterns"},
        {"time": "10:38 AM", "agent": "compliance", "action": "Completed compliance checks"},
        {"time": "10:40 AM", "agent": "verifier", "action": "Verified patterns with consensus"},
        {"time": "10:42 AM", "agent": "synthesizer", "action": "Generated final report"}
    ]
    
    activity_df = pd.DataFrame(activity_data)
    st.dataframe(activity_df, use_container_width=True)

def show_agents(data):
    """Show agents status and details."""
    st.header("Agent Status")
    
    # Agent status cards
    for agent_name, agent_info in data["agents"].items():
        with st.expander(f"🤖 {agent_name.title()} Agent"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Status", agent_info["status"].title())
            
            with col2:
                st.metric("Tasks Processed", agent_info["processed_tasks"])
            
            with col3:
                st.metric("Success Rate", f"{agent_info['success_rate']:.1%}")
            
            # Agent-specific details
            if agent_name == "planner":
                st.info("Responsible for parsing user queries and creating task graphs")
            elif agent_name == "retriever":
                st.info("Fetches transaction data and regulatory documents via RAG")
            elif agent_name == "analysis":
                st.info("Runs anomaly detection and pattern analysis algorithms")
            elif agent_name == "compliance":
                st.info("Checks patterns against AML regulations")
            elif agent_name == "verifier":
                st.info("Performs multi-agent verification and consensus")
            elif agent_name == "synthesizer":
                st.info("Aggregates findings into comprehensive reports")

def show_reports(data):
    """Show reports and analysis results."""
    st.header("Reports & Analysis")
    
    # Report list
    for report in data["reports"]:
        with st.expander(f"📊 {report['title']}"):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Status", report["status"].replace("_", " ").title())
            
            with col2:
                st.metric("Total Patterns", report["total_patterns"])
            
            with col3:
                st.metric("High Risk", report["high_risk_patterns"])
            
            with col4:
                st.metric("Violations", report["compliance_violations"])
            
            st.text(f"Created: {report['created_at']}")
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("View Details", key=f"view_{report['id']}"):
                    st.info("Detailed report view would be shown here")
            
            with col2:
                if st.button("Export", key=f"export_{report['id']}"):
                    st.success("Report exported successfully!")
            
            with col3:
                if st.button("Download", key=f"download_{report['id']}"):
                    st.success("Report downloaded!")

def show_patterns(data):
    """Show detected patterns and analysis."""
    st.header("Detected Patterns")
    
    # Pattern summary
    pattern_df = pd.DataFrame(data["patterns"])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Pattern Distribution")
        fig = px.bar(
            pattern_df,
            x="type",
            y="count",
            color="risk_level",
            title="Pattern Types by Risk Level"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Risk Level Breakdown")
        risk_counts = pattern_df.groupby("risk_level")["count"].sum()
        fig = px.pie(
            values=risk_counts.values,
            names=risk_counts.index,
            title="Patterns by Risk Level"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Pattern details
    st.subheader("Pattern Details")
    for pattern in data["patterns"]:
        with st.expander(f"🔍 {pattern['type'].title()} Pattern"):
            st.write(f"**Count:** {pattern['count']}")
            st.write(f"**Risk Level:** {pattern['risk_level']}")
            
            # Pattern-specific information
            if pattern["type"] == "structuring":
                st.warning("Multiple transactions just under reporting thresholds detected")
            elif pattern["type"] == "layering":
                st.error("Complex transaction chains suggesting money laundering")
            elif pattern["type"] == "integration":
                st.info("Large deposits from unknown sources")
            elif pattern["type"] == "rapid_movement":
                st.warning("Quick successive transactions by same entity")
            elif pattern["type"] == "unusual_amounts":
                st.info("Statistically significant transaction amounts")

def show_settings():
    """Show system settings and configuration."""
    st.header("System Settings")
    
    # Configuration sections
    with st.expander("🔧 Agent Configuration"):
        st.number_input("Planner Max Tasks", value=10, min_value=1, max_value=100)
        st.number_input("Retriever Top K", value=5, min_value=1, max_value=20)
        st.slider("Similarity Threshold", value=0.7, min_value=0.0, max_value=1.0, step=0.1)
        st.slider("Anomaly Threshold", value=0.05, min_value=0.0, max_value=1.0, step=0.01)
        st.slider("Consensus Threshold", value=0.8, min_value=0.0, max_value=1.0, step=0.1)
    
    with st.expander("📊 Model Configuration"):
        st.selectbox("OpenAI Model", ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"])
        st.slider("Temperature", value=0.1, min_value=0.0, max_value=2.0, step=0.1)
        st.number_input("Max Tokens", value=2000, min_value=100, max_value=8000)
    
    with st.expander("📝 Logging Configuration"):
        st.selectbox("Log Level", ["DEBUG", "INFO", "WARNING", "ERROR"])
        st.text_input("Log File Path", value="logs/orchestrator.log")
        st.checkbox("Enable Audit Logging", value=True)
    
    # Save button
    if st.button("💾 Save Settings"):
        st.success("Settings saved successfully!")

if __name__ == "__main__":
    main() 