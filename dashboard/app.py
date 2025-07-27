"""
Multi-Agent Analysis Platform Dashboard
Supports both AML and Supply Chain Risk Audit modes.
"""

import streamlit as st
import asyncio
import json
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Mock data for demonstration
def get_mock_aml_data():
    """Get mock AML data for the dashboard."""
    return {
        "mode": "aml",
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

def get_mock_supply_chain_data():
    """Get mock Supply Chain data for the dashboard."""
    return {
        "mode": "supply_chain",
        "agents": {
            "internal_retriever": {"status": "running", "processed_tasks": 20, "success_rate": 0.95},
            "external_retriever": {"status": "running", "processed_tasks": 18, "success_rate": 0.92},
            "risk_analysis": {"status": "running", "processed_tasks": 20, "success_rate": 0.94},
            "esg_compliance": {"status": "running", "processed_tasks": 20, "success_rate": 0.96},
            "verifier": {"status": "running", "processed_tasks": 20, "success_rate": 0.93},
            "synthesizer": {"status": "running", "processed_tasks": 20, "success_rate": 0.97}
        },
        "reports": [
            {
                "id": "sc_report_001",
                "title": "Supply Chain Risk Audit - Q1 2024",
                "status": "completed",
                "created_at": "2024-01-15T10:00:00",
                "total_suppliers": 20,
                "high_risk_suppliers": 4,
                "non_compliant_suppliers": 11
            },
            {
                "id": "sc_report_002", 
                "title": "ESG Compliance Assessment",
                "status": "pending_review",
                "created_at": "2024-01-16T14:30:00",
                "total_suppliers": 15,
                "high_risk_suppliers": 3,
                "non_compliant_suppliers": 8
            }
        ],
        "suppliers": [
            {"risk_level": "low", "count": 7, "compliance_rate": 0.85},
            {"risk_level": "medium", "count": 9, "compliance_rate": 0.67},
            {"risk_level": "high", "count": 2, "compliance_rate": 0.25},
            {"risk_level": "critical", "count": 2, "compliance_rate": 0.10}
        ],
        "compliance_categories": [
            {"category": "Environmental", "compliant": 10, "non_compliant": 10},
            {"category": "Social", "compliant": 10, "non_compliant": 10},
            {"category": "Governance", "compliant": 9, "non_compliant": 11}
        ]
    }

def load_latest_report(mode):
    """Load the latest report from files."""
    try:
        reports_dir = Path("reports")
        if not reports_dir.exists():
            return None
        
        if mode == "supply_chain":
            # Look for supply chain reports
            report_files = list(reports_dir.glob("supply_chain_audit_*.json"))
        else:
            # Look for AML reports
            report_files = list(reports_dir.glob("aml_report*.json"))
        
        if not report_files:
            return None
        
        # Get the most recent file
        latest_file = max(report_files, key=lambda x: x.stat().st_mtime)
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    except Exception as e:
        st.error(f"Error loading report: {e}")
        return None

def main():
    """Main dashboard function."""
    st.set_page_config(
        page_title="Multi-Agent Analysis Platform",
        page_icon="🔍",
        layout="wide"
    )
    
    # Mode selection in sidebar
    st.sidebar.header("🔧 Platform Mode")
    mode = st.sidebar.selectbox(
        "Select Analysis Mode",
        ["AML Analysis", "Supply Chain Risk Audit"],
        index=1  # Default to Supply Chain
    )
    
    # Set mode
    if mode == "AML Analysis":
        current_mode = "aml"
        st.title("🔍 AML Orchestrator Dashboard")
        st.markdown("Multi-Agent Anti-Money Laundering Analysis Platform")
    else:
        current_mode = "supply_chain"
        st.title("🔍 Supply Chain Risk Audit Dashboard")
        st.markdown("Multi-Agent ESG & Compliance Risk Assessment Platform")
    
    # Get data based on mode
    if current_mode == "aml":
        data = get_mock_aml_data()
    else:
        data = get_mock_supply_chain_data()
    
    # Navigation
    st.sidebar.header("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Overview", "Agents", "Reports", "Analysis", "Settings"]
    )
    
    if page == "Overview":
        show_overview(data, current_mode)
    elif page == "Agents":
        show_agents(data, current_mode)
    elif page == "Reports":
        show_reports(data, current_mode)
    elif page == "Analysis":
        if current_mode == "aml":
            show_aml_patterns(data)
        else:
            show_supply_chain_analysis(data)
    elif page == "Settings":
        show_settings(current_mode)

def show_overview(data, mode):
    """Show overview dashboard."""
    st.header("System Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        active_agents = len([a for a in data["agents"].values() if a["status"] == "running"])
        st.metric(
            label="Active Agents",
            value=active_agents,
            delta=f"{active_agents}/{len(data['agents'])}"
        )
    
    with col2:
        if mode == "aml":
            total_patterns = sum(p["count"] for p in data["patterns"])
            high_risk_patterns = sum(p["count"] for p in data["patterns"] if p["risk_level"] in ["high", "critical"])
            st.metric(
                label="Total Patterns",
                value=total_patterns,
                delta=f"{high_risk_patterns} high-risk"
            )
        else:
            total_suppliers = sum(s["count"] for s in data["suppliers"])
            high_risk_suppliers = sum(s["count"] for s in data["suppliers"] if s["risk_level"] in ["high", "critical"])
            st.metric(
                label="Total Suppliers",
                value=total_suppliers,
                delta=f"{high_risk_suppliers} high-risk"
            )
    
    with col3:
        if mode == "aml":
            avg_success_rate = sum(a["success_rate"] for a in data["agents"].values()) / len(data["agents"])
            st.metric(
                label="Avg Success Rate",
                value=f"{avg_success_rate:.1%}",
                delta="+2.3%"
            )
        else:
            avg_compliance_rate = sum(s["compliance_rate"] for s in data["suppliers"]) / len(data["suppliers"])
            st.metric(
                label="Avg Compliance Rate",
                value=f"{avg_compliance_rate:.1%}",
                delta="-5.2%"
            )
    
    with col4:
        if mode == "aml":
            total_reports = len(data["reports"])
            completed_reports = len([r for r in data["reports"] if r["status"] == "completed"])
            st.metric(
                label="Reports Generated",
                value=total_reports,
                delta=f"{completed_reports} completed"
            )
        else:
            non_compliant = sum(c["non_compliant"] for c in data["compliance_categories"])
            st.metric(
                label="Non-Compliant Suppliers",
                value=non_compliant,
                delta="Requires attention"
            )
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        if mode == "aml":
            # AML patterns chart
            patterns_df = pd.DataFrame(data["patterns"])
            fig = px.bar(
                patterns_df, 
                x="type", 
                y="count", 
                color="risk_level",
                title="AML Pattern Distribution",
                color_discrete_map={
                    "low": "green",
                    "medium": "yellow", 
                    "high": "orange",
                    "critical": "red"
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            # Supply chain risk distribution
            suppliers_df = pd.DataFrame(data["suppliers"])
            fig = px.bar(
                suppliers_df,
                x="risk_level",
                y="count",
                color="compliance_rate",
                title="Supplier Risk Distribution",
                color_continuous_scale="RdYlGn"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if mode == "aml":
            # Agent performance
            agents_df = pd.DataFrame([
                {"agent": name, "success_rate": agent["success_rate"]}
                for name, agent in data["agents"].items()
            ])
            fig = px.bar(
                agents_df,
                x="agent",
                y="success_rate",
                title="Agent Success Rates",
                color="success_rate",
                color_continuous_scale="RdYlGn"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            # Compliance categories
            compliance_df = pd.DataFrame(data["compliance_categories"])
            fig = px.bar(
                compliance_df,
                x="category",
                y=["compliant", "non_compliant"],
                title="Compliance by Category",
                barmode="group"
            )
            st.plotly_chart(fig, use_container_width=True)

def show_agents(data, mode):
    """Show agents status and performance."""
    st.header("Agent Status & Performance")
    
    # Agent status table
    agents_df = pd.DataFrame([
        {
            "Agent": name.replace("_", " ").title(),
            "Status": agent["status"].title(),
            "Tasks Processed": agent["processed_tasks"],
            "Success Rate": f"{agent['success_rate']:.1%}",
            "Performance": "🟢 Excellent" if agent["success_rate"] > 0.95 else 
                          "🟡 Good" if agent["success_rate"] > 0.90 else "🔴 Needs Attention"
        }
        for name, agent in data["agents"].items()
    ])
    
    st.dataframe(agents_df, use_container_width=True)
    
    # Agent performance chart
    fig = px.line(
        agents_df,
        x="Agent",
        y="Success Rate",
        title="Agent Performance Over Time",
        markers=True
    )
    st.plotly_chart(fig, use_container_width=True)

def show_reports(data, mode):
    """Show reports and analysis results."""
    st.header("Reports & Analysis")
    
    # Load latest report if available
    latest_report = load_latest_report(mode)
    
    if latest_report:
        st.success("✅ Latest report loaded successfully!")
        
        # Show report summary
        if mode == "aml":
            show_aml_report_summary(latest_report)
        else:
            show_supply_chain_report_summary(latest_report)
    else:
        st.info("📋 No recent reports found. Run an analysis to generate reports.")
    
    # Reports table
    reports_df = pd.DataFrame([
        {
            "ID": report["id"],
            "Title": report["title"],
            "Status": report["status"].replace("_", " ").title(),
            "Created": report["created_at"][:10],
            "Key Metrics": get_report_metrics(report, mode)
        }
        for report in data["reports"]
    ])
    
    st.dataframe(reports_df, use_container_width=True)

def get_report_metrics(report, mode):
    """Get key metrics for a report."""
    if mode == "aml":
        return f"{report.get('total_patterns', 0)} patterns, {report.get('high_risk_patterns', 0)} high-risk"
    else:
        return f"{report.get('total_suppliers', 0)} suppliers, {report.get('high_risk_suppliers', 0)} high-risk"

def show_aml_report_summary(report):
    """Show AML report summary."""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Patterns", report.get("total_patterns", 0))
    
    with col2:
        st.metric("High Risk Patterns", report.get("high_risk_patterns", 0))
    
    with col3:
        st.metric("Compliance Violations", report.get("compliance_violations", 0))

def show_supply_chain_report_summary(report):
    """Show Supply Chain report summary."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Suppliers", report.get("total_suppliers", 0))
    
    with col2:
        st.metric("High Risk Suppliers", report.get("high_risk_suppliers", 0))
    
    with col3:
        st.metric("Non-Compliant", report.get("non_compliant_suppliers", 0))
    
    with col4:
        compliance_rate = report.get("compliance_rate", 0)
        st.metric("Compliance Rate", f"{compliance_rate:.1%}")

def show_aml_patterns(data):
    """Show AML pattern analysis."""
    st.header("AML Pattern Analysis")
    
    # Pattern distribution
    patterns_df = pd.DataFrame(data["patterns"])
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(
            patterns_df,
            values="count",
            names="type",
            title="Pattern Type Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(
            patterns_df,
            x="type",
            y="count",
            color="risk_level",
            title="Pattern Risk Levels"
        )
        st.plotly_chart(fig, use_container_width=True)

def show_supply_chain_analysis(data):
    """Show Supply Chain analysis."""
    st.header("Supply Chain Risk Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Risk distribution
        suppliers_df = pd.DataFrame(data["suppliers"])
        fig = px.pie(
            suppliers_df,
            values="count",
            names="risk_level",
            title="Supplier Risk Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Compliance by category
        compliance_df = pd.DataFrame(data["compliance_categories"])
        fig = px.bar(
            compliance_df,
            x="category",
            y=["compliant", "non_compliant"],
            title="Compliance by ESG Category",
            barmode="group"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Risk factors analysis
    st.subheader("Risk Factors Analysis")
    
    # Mock risk factors data
    risk_factors = {
        "Country ESG Rating": {"avg_score": 0.475, "high_risk_count": 3},
        "Prior Violations": {"avg_score": 0.37, "high_risk_count": 4},
        "Supply Category Risk": {"avg_score": 0.395, "high_risk_count": 3},
        "Financial Stability": {"avg_score": 0.455, "high_risk_count": 2}
    }
    
    risk_df = pd.DataFrame([
        {
            "Risk Factor": factor,
            "Average Score": data["avg_score"],
            "High Risk Count": data["high_risk_count"]
        }
        for factor, data in risk_factors.items()
    ])
    
    fig = px.bar(
        risk_df,
        x="Risk Factor",
        y="Average Score",
        color="High Risk Count",
        title="Risk Factors Analysis",
        color_continuous_scale="Reds"
    )
    st.plotly_chart(fig, use_container_width=True)

def show_settings(mode):
    """Show system settings."""
    st.header("System Settings")
    
    st.subheader("Current Configuration")
    
    if mode == "aml":
        st.info("🔍 AML Analysis Mode")
        st.write("""
        - **Agents**: Planner, Retriever, Analysis, Compliance, Verifier, Synthesizer
        - **Data Sources**: Transaction databases, KYC systems, regulatory databases
        - **Analysis Focus**: Money laundering patterns, suspicious activities
        """)
    else:
        st.info("🔍 Supply Chain Risk Audit Mode")
        st.write("""
        - **Agents**: Internal Retriever, External Retriever, Risk Analysis, ESG Compliance, Verifier, Synthesizer
        - **Data Sources**: Supplier databases, ESG ratings, sanction lists, compliance databases
        - **Analysis Focus**: ESG risks, compliance violations, supply chain sustainability
        """)
    
    st.subheader("Configuration Files")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**AML Configuration**")
        st.code("configs/aml.yaml", language="yaml")
        
        st.write("**Supply Chain Configuration**")
        st.code("configs/supply_chain.yaml", language="yaml")
    
    with col2:
        st.write("**Data Sources**")
        if mode == "aml":
            st.code("""
data/
├── transactions.csv
├── kyc_data/
└── regulatory_data/
            """, language="text")
        else:
            st.code("""
data/
├── suppliers.csv
├── external/
│   ├── sanction_lists/
│   ├── sustainability_reports/
│   └── esg_guidelines/
            """, language="text")

if __name__ == "__main__":
    main() 