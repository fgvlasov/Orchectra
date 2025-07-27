#!/usr/bin/env python3
"""
Simplified demo script for the AML Orchestrator.
This script demonstrates the basic functionality without complex configuration.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
import pandas as pd

def load_transaction_data():
    """Load sample transaction data."""
    try:
        df = pd.read_csv('data/transactions.csv')
        print(f"✅ Loaded {len(df)} transactions from data/transactions.csv")
        return df
    except Exception as e:
        print(f"❌ Error loading transaction data: {e}")
        return None

def analyze_transactions(df):
    """Simple transaction analysis."""
    if df is None:
        return None
    
    print("\n📊 Transaction Analysis")
    print("-" * 40)
    
    # Basic statistics
    total_transactions = len(df)
    total_amount = df['amount'].sum()
    avg_amount = df['amount'].mean()
    
    print(f"Total transactions: {total_transactions}")
    print(f"Total amount: ${total_amount:,.2f}")
    print(f"Average amount: ${avg_amount:,.2f}")
    
    # Risk level analysis
    risk_counts = df['risk_level'].value_counts()
    print(f"\nRisk Level Distribution:")
    for risk, count in risk_counts.items():
        print(f"  {risk}: {count} transactions")
    
    # High-risk transactions
    high_risk = df[df['risk_level'].isin(['high', 'critical'])]
    print(f"\n🚨 High-risk transactions: {len(high_risk)}")
    
    if len(high_risk) > 0:
        print("High-risk transaction details:")
        for _, tx in high_risk.head(5).iterrows():
            print(f"  - {tx['sender_name']} → {tx['recipient_name']}: ${tx['amount']:,.2f} ({tx['risk_level']})")
    
    return {
        'total_transactions': total_transactions,
        'total_amount': total_amount,
        'high_risk_count': len(high_risk),
        'risk_distribution': risk_counts.to_dict()
    }

def detect_patterns(df):
    """Detect suspicious patterns."""
    if df is None:
        return None
    
    print("\n🔍 Pattern Detection")
    print("-" * 40)
    
    patterns = []
    
    # Structuring detection (multiple transactions under $10,000)
    structuring_suspects = df[df['amount'] < 10000].groupby('sender_id').agg({
        'amount': ['count', 'sum'],
        'timestamp': 'nunique'
    }).reset_index()
    
    structuring_suspects = structuring_suspects[
        (structuring_suspects[('amount', 'count')] >= 3) &
        (structuring_suspects[('amount', 'sum')] >= 10000)
    ]
    
    if len(structuring_suspects) > 0:
        print(f"🚨 Potential structuring detected: {len(structuring_suspects)} entities")
        patterns.append({
            'type': 'structuring',
            'count': len(structuring_suspects),
            'description': 'Multiple transactions under $10,000'
        })
    
    # Large transactions
    large_tx = df[df['amount'] > 50000]
    if len(large_tx) > 0:
        print(f"💰 Large transactions (>$50k): {len(large_tx)}")
        patterns.append({
            'type': 'large_transactions',
            'count': len(large_tx),
            'description': 'Transactions over $50,000'
        })
    
    # Rapid movement (same day multiple transactions)
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    rapid_movement = df.groupby(['sender_id', 'date']).size().reset_index(name='count')
    rapid_movement = rapid_movement[rapid_movement['count'] >= 3]
    
    if len(rapid_movement) > 0:
        print(f"⚡ Rapid movement detected: {len(rapid_movement)} instances")
        patterns.append({
            'type': 'rapid_movement',
            'count': len(rapid_movement),
            'description': 'Multiple transactions on same day'
        })
    
    return patterns

def generate_report(analysis_data, patterns):
    """Generate a simple report."""
    print("\n📋 AML Analysis Report")
    print("=" * 50)
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': analysis_data,
        'patterns': patterns,
        'recommendations': []
    }
    
    # Add recommendations based on findings
    if analysis_data['high_risk_count'] > 0:
        report['recommendations'].append(
            f"Review {analysis_data['high_risk_count']} high-risk transactions"
        )
    
    if patterns:
        for pattern in patterns:
            if pattern['type'] == 'structuring':
                report['recommendations'].append(
                    "File Suspicious Activity Report (SAR) for structuring patterns"
                )
            elif pattern['type'] == 'large_transactions':
                report['recommendations'].append(
                    "Conduct enhanced due diligence on large transaction entities"
                )
    
    # Print report
    print(f"Report generated: {report['timestamp']}")
    print(f"Total transactions analyzed: {report['summary']['total_transactions']}")
    print(f"Total amount analyzed: ${report['summary']['total_amount']:,.2f}")
    print(f"High-risk transactions: {report['summary']['high_risk_count']}")
    print(f"Patterns detected: {len(report['patterns'])}")
    
    if report['recommendations']:
        print("\nRecommendations:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"  {i}. {rec}")
    
    return report

def save_report(report, filename="aml_report.json"):
    """Save report to file."""
    try:
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\n✅ Report saved to {filename}")
    except Exception as e:
        print(f"❌ Error saving report: {e}")

async def main():
    """Main demo function."""
    print("🚀 AML Orchestrator - Simplified Demo")
    print("=" * 50)
    
    # Load data
    df = load_transaction_data()
    
    if df is None:
        print("❌ Cannot proceed without transaction data")
        return
    
    # Analyze transactions
    analysis_data = analyze_transactions(df)
    
    # Detect patterns
    patterns = detect_patterns(df)
    
    # Generate report
    report = generate_report(analysis_data, patterns)
    
    # Save report
    save_report(report)
    
    print("\n" + "=" * 50)
    print("✅ Demo completed successfully!")
    print("\nNext steps:")
    print("1. Set up your OpenAI API key in .env file")
    print("2. Run the full orchestrator: python -m orchestrator.main")
    print("3. Start the dashboard: streamlit run dashboard/app.py")

if __name__ == "__main__":
    asyncio.run(main()) 