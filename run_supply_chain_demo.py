#!/usr/bin/env python3
"""
Supply Chain Risk Audit Demo
Demonstrates the multi-agent platform adapted for ESG/Supply-Chain risk assessment.
"""

import asyncio
import json
import pandas as pd
from datetime import datetime
from pathlib import Path

from orchestrator.utils.supplier_parser import SupplierDataParser
from orchestrator.agents.supply_chain_agents import (
    InternalRetrieverAgent, ExternalRetrieverAgent, 
    RiskAnalysisAgent, ESGComplianceAgent
)


async def run_supply_chain_demo():
    """Run the supply chain risk audit demonstration."""
    print("🔍 Supply Chain Risk Audit - Multi-Agent Demo")
    print("=" * 60)
    
    try:
        # 1. Load and parse supplier data
        print("\n📊 Step 1: Loading Supplier Data")
        print("-" * 40)
        
        parser = SupplierDataParser()
        suppliers = parser.parse_suppliers("data/suppliers.csv")
        
        print(f"✅ Loaded {len(suppliers)} suppliers")
        
        # Validate data
        validation = parser.validate_supplier_data(suppliers)
        print(f"📋 Data validation: {'✅ Valid' if validation['valid'] else '❌ Invalid'}")
        print(f"🌍 Countries: {len(validation['countries'])}")
        print(f"🏭 Industries: {len(validation['industries'])}")
        print(f"📦 Supplier types: {len(validation['supplier_types'])}")
        
        if validation['errors']:
            print(f"⚠️  Validation errors: {len(validation['errors'])}")
            for error in validation['errors'][:3]:  # Show first 3 errors
                print(f"   - {error}")
        
        # 2. Initialize agents
        print("\n🤖 Step 2: Initializing Agents")
        print("-" * 40)
        
        # Internal retriever configuration
        internal_config = {
            "data_sources": ["data/suppliers.csv"],
            "top_k": 20,
            "similarity_threshold": 0.7
        }
        
        # External retriever configuration
        external_config = {
            "data_sources": ["data/external/sanction_lists/"],
            "api_endpoints": ["country_esg_ratings", "violation_database"],
            "top_k": 15,
            "similarity_threshold": 0.6
        }
        
        # Risk analysis configuration
        risk_config = {
            "risk_factors": {
                "country_esg_rating": {"weight": 0.25, "threshold": 0.6},
                "prior_violations": {"weight": 0.30, "threshold": 0.7},
                "supply_category_risk": {"weight": 0.20, "threshold": 0.5},
                "financial_stability": {"weight": 0.25, "threshold": 0.6}
            },
            "composite_risk_threshold": 0.65
        }
        
        # ESG compliance configuration
        compliance_config = {
            "compliance_frameworks": ["EU_CSDDD", "ISO_14001", "SA8000"],
            "risk_categories": {
                "environmental": ["carbon_emissions", "water_usage", "waste_management"],
                "social": ["labor_rights", "human_rights", "health_safety"],
                "governance": ["corruption", "transparency", "board_diversity"]
            }
        }
        
        # Create agents
        internal_retriever = InternalRetrieverAgent(internal_config)
        external_retriever = ExternalRetrieverAgent(external_config)
        risk_analyzer = RiskAnalysisAgent(risk_config)
        esg_compliance = ESGComplianceAgent(compliance_config)
        
        print("✅ Internal Retriever Agent initialized")
        print("✅ External Retriever Agent initialized")
        print("✅ Risk Analysis Agent initialized")
        print("✅ ESG Compliance Agent initialized")
        
        # 3. Execute analysis pipeline
        print("\n🔍 Step 3: Executing Analysis Pipeline")
        print("-" * 40)
        
        # Step 3.1: Internal data retrieval
        print("\n3.1 Internal Data Retrieval")
        internal_task = type('Task', (), {
            'id': 'internal_retrieve',
            'payload': {'query': 'Assess ESG and compliance risks for suppliers'}
        })()
        
        internal_result = await internal_retriever.process_task(internal_task)
        if internal_result.success:
            print(f"✅ Retrieved {internal_result.data['filtered_count']} suppliers")
        else:
            print(f"❌ Internal retrieval failed: {internal_result.error}")
            return
        
        # Step 3.2: External data retrieval
        print("\n3.2 External Data Retrieval")
        external_task = type('Task', (), {
            'id': 'external_retrieve',
            'payload': {'query': 'Retrieve ESG and compliance data'}
        })()
        
        external_result = await external_retriever.process_task(external_task)
        if external_result.success:
            print(f"✅ Retrieved external data from {len(external_result.data['data_sources'])} sources")
        else:
            print(f"❌ External retrieval failed: {external_result.error}")
            return
        
        # Step 3.3: Risk analysis
        print("\n3.3 Risk Analysis")
        risk_task = type('Task', (), {
            'id': 'risk_analysis',
            'payload': {
                'suppliers': internal_result.data['suppliers'],
                'external_data': external_result.data['external_data']
            }
        })()
        
        risk_result = await risk_analyzer.process_task(risk_task)
        if risk_result.success:
            risk_analysis = risk_result.data['risk_analysis']
            high_risk_suppliers = risk_result.data['high_risk_suppliers']
            print(f"✅ Analyzed {len(risk_analysis)} suppliers")
            print(f"🚨 Found {len(high_risk_suppliers)} high-risk suppliers")
        else:
            print(f"❌ Risk analysis failed: {risk_result.error}")
            return
        
        # Step 3.4: ESG compliance assessment
        print("\n3.4 ESG Compliance Assessment")
        compliance_task = type('Task', (), {
            'id': 'esg_compliance',
            'payload': {
                'suppliers': internal_result.data['suppliers'],
                'external_data': external_result.data['external_data']
            }
        })()
        
        compliance_result = await esg_compliance.process_task(compliance_task)
        if compliance_result.success:
            compliance_assessment = compliance_result.data['compliance_assessment']
            non_compliant = compliance_result.data['non_compliant_suppliers']
            print(f"✅ Assessed {len(compliance_assessment)} suppliers")
            print(f"⚠️  Found {len(non_compliant)} non-compliant suppliers")
        else:
            print(f"❌ Compliance assessment failed: {compliance_result.error}")
            return
        
        # 4. Generate comprehensive report
        print("\n📋 Step 4: Generating Report")
        print("-" * 40)
        
        report = generate_supply_chain_report(
            suppliers=internal_result.data['suppliers'],
            risk_analysis=risk_analysis,
            compliance_assessment=compliance_assessment,
            external_data=external_result.data['external_data']
        )
        
        # 5. Display results
        print("\n📊 Analysis Results")
        print("=" * 40)
        
        # Risk distribution
        risk_levels = {}
        for analysis in risk_analysis:
            risk_level = analysis['risk_level']
            risk_levels[risk_level] = risk_levels.get(risk_level, 0) + 1
        
        print(f"Risk Level Distribution:")
        for level, count in sorted(risk_levels.items()):
            print(f"  {level.capitalize()}: {count} suppliers")
        
        # High-risk suppliers
        print(f"\n🚨 High-Risk Suppliers ({len(high_risk_suppliers)}):")
        for supplier in high_risk_suppliers[:5]:  # Show top 5
            print(f"  - {supplier['supplier_name']} ({supplier['country']})")
            print(f"    Risk Score: {supplier['composite_risk_score']:.2f}")
            print(f"    Risk Level: {supplier['risk_level']}")
            if supplier['flags']:
                print(f"    Flags: {', '.join(supplier['flags'])}")
            print()
        
        # Compliance summary
        compliant_count = len([s for s in compliance_assessment if s['overall_compliant']])
        print(f"📋 Compliance Summary:")
        print(f"  Compliant: {compliant_count} suppliers")
        print(f"  Non-compliant: {len(non_compliant)} suppliers")
        print(f"  Compliance rate: {compliant_count/len(compliance_assessment)*100:.1f}%")
        
        # 6. Save report
        print("\n💾 Step 5: Saving Report")
        print("-" * 40)
        
        # Create reports directory
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        
        # Save detailed report
        report_file = reports_dir / f"supply_chain_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"✅ Report saved to: {report_file}")
        
        # 7. Recommendations
        print("\n💡 Recommendations")
        print("-" * 40)
        
        recommendations = generate_recommendations(high_risk_suppliers, non_compliant_suppliers)
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
        
        print("\n" + "=" * 60)
        print("✅ Supply Chain Risk Audit completed successfully!")
        print(f"📊 Analyzed {len(suppliers)} suppliers")
        print(f"🚨 Identified {len(high_risk_suppliers)} high-risk suppliers")
        print(f"⚠️  Found {len(non_compliant)} compliance issues")
        print(f"📋 Report saved to: {report_file}")
        
    except Exception as e:
        print(f"\n❌ Error during supply chain audit: {e}")
        import traceback
        traceback.print_exc()


def generate_supply_chain_report(suppliers, risk_analysis, compliance_assessment, external_data):
    """Generate a comprehensive supply chain audit report."""
    report = {
        "metadata": {
            "report_type": "supply_chain_risk_audit",
            "generated_at": datetime.now().isoformat(),
            "total_suppliers": len(suppliers),
            "analysis_version": "1.0.0"
        },
        "executive_summary": {
            "total_suppliers_analyzed": len(suppliers),
            "high_risk_suppliers": len([s for s in risk_analysis if s['risk_level'] in ['high', 'critical']]),
            "non_compliant_suppliers": len([s for s in compliance_assessment if not s['overall_compliant']]),
            "overall_risk_score": sum(s['composite_risk_score'] for s in risk_analysis) / len(risk_analysis),
            "compliance_rate": len([s for s in compliance_assessment if s['overall_compliant']]) / len(compliance_assessment)
        },
        "risk_assessment": {
            "risk_distribution": {},
            "high_risk_suppliers": [],
            "risk_factors_analysis": {
                "country_esg_rating": {"avg_score": 0, "high_risk_count": 0},
                "prior_violations": {"avg_score": 0, "high_risk_count": 0},
                "supply_category_risk": {"avg_score": 0, "high_risk_count": 0},
                "financial_stability": {"avg_score": 0, "high_risk_count": 0}
            }
        },
        "compliance_analysis": {
            "compliance_summary": {
                "environmental": {"compliant": 0, "non_compliant": 0},
                "social": {"compliant": 0, "non_compliant": 0},
                "governance": {"compliant": 0, "non_compliant": 0}
            },
            "non_compliant_suppliers": [],
            "compliance_gaps": []
        },
        "supplier_details": [],
        "recommendations": [],
        "action_items": []
    }
    
    # Risk distribution
    for analysis in risk_analysis:
        risk_level = analysis['risk_level']
        report["risk_assessment"]["risk_distribution"][risk_level] = \
            report["risk_assessment"]["risk_distribution"].get(risk_level, 0) + 1
    
    # High-risk suppliers
    high_risk = [s for s in risk_analysis if s['risk_level'] in ['high', 'critical']]
    report["risk_assessment"]["high_risk_suppliers"] = [
        {
            "supplier_id": s['supplier_id'],
            "supplier_name": s['supplier_name'],
            "country": s['country'],
            "risk_score": s['composite_risk_score'],
            "risk_level": s['risk_level'],
            "flags": s['flags']
        }
        for s in high_risk
    ]
    
    # Risk factors analysis
    for factor in ["country_esg_rating", "prior_violations", "supply_category_risk", "financial_stability"]:
        scores = [s['risk_factors'][factor] for s in risk_analysis]
        report["risk_assessment"]["risk_factors_analysis"][factor] = {
            "avg_score": sum(scores) / len(scores),
            "high_risk_count": len([s for s in scores if s > 0.7])
        }
    
    # Compliance summary
    for assessment in compliance_assessment:
        for category in ["environmental", "social", "governance"]:
            if assessment[category]["compliant"]:
                report["compliance_analysis"]["compliance_summary"][category]["compliant"] += 1
            else:
                report["compliance_analysis"]["compliance_summary"][category]["non_compliant"] += 1
    
    # Non-compliant suppliers
    non_compliant = [s for s in compliance_assessment if not s['overall_compliant']]
    report["compliance_analysis"]["non_compliant_suppliers"] = [
        {
            "supplier_id": s['supplier_id'],
            "supplier_name": s['supplier_name'],
            "country": s['country'],
            "compliance_score": s['compliance_score'],
            "issues": {
                "environmental": s['environmental']['issues'],
                "social": s['social']['issues'],
                "governance": s['governance']['issues']
            },
            "recommendations": s['recommendations']
        }
        for s in non_compliant
    ]
    
    # Supplier details
    for i, supplier in enumerate(suppliers):
        risk_info = next((r for r in risk_analysis if r['supplier_id'] == supplier['id']), None)
        compliance_info = next((c for c in compliance_assessment if c['supplier_id'] == supplier['id']), None)
        
        report["supplier_details"].append({
            "supplier_id": supplier['id'],
            "supplier_name": supplier['name'],
            "country": supplier['country'],
            "industry": supplier['industry'],
            "supplier_type": supplier['supplier_type'],
            "esg_score": supplier['esg_score'],
            "financial_stability": supplier['financial_stability'],
            "prior_violations": supplier['prior_violations'],
            "risk_analysis": risk_info,
            "compliance_assessment": compliance_info
        })
    
    return report


def generate_recommendations(high_risk_suppliers, non_compliant_suppliers):
    """Generate actionable recommendations based on analysis results."""
    recommendations = []
    
    if high_risk_suppliers:
        recommendations.append(
            f"Conduct immediate due diligence on {len(high_risk_suppliers)} high-risk suppliers"
        )
        
        # Country-specific recommendations
        countries = {}
        for supplier in high_risk_suppliers:
            country = supplier['country']
            countries[country] = countries.get(country, 0) + 1
        
        high_risk_countries = [c for c, count in countries.items() if count >= 2]
        if high_risk_countries:
            recommendations.append(
                f"Implement enhanced monitoring for suppliers in: {', '.join(high_risk_countries)}"
            )
    
    if non_compliant_suppliers:
        recommendations.append(
            f"Develop compliance improvement plans for {len(non_compliant_suppliers)} non-compliant suppliers"
        )
        
        # Compliance-specific recommendations
        environmental_issues = sum(1 for s in non_compliant_suppliers if s['environmental']['issues'])
        social_issues = sum(1 for s in non_compliant_suppliers if s['social']['issues'])
        governance_issues = sum(1 for s in non_compliant_suppliers if s['governance']['issues'])
        
        if environmental_issues > 0:
            recommendations.append("Implement environmental management system training")
        if social_issues > 0:
            recommendations.append("Establish labor rights monitoring program")
        if governance_issues > 0:
            recommendations.append("Enhance governance and transparency requirements")
    
    # General recommendations
    recommendations.extend([
        "Establish regular supplier risk assessment schedule (quarterly)",
        "Implement automated risk monitoring system",
        "Develop supplier onboarding ESG compliance checklist",
        "Create supplier improvement program with clear timelines",
        "Establish escalation procedures for critical risk suppliers"
    ])
    
    return recommendations


if __name__ == "__main__":
    asyncio.run(run_supply_chain_demo()) 