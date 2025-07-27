#!/usr/bin/env python3
"""
Simplified Supply Chain Risk Audit Demo
Demonstrates the multi-agent platform adapted for ESG/Supply-Chain risk assessment.
"""

import asyncio
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List


def load_supplier_data(file_path: str) -> List[Dict[str, Any]]:
    """Load supplier data from CSV file."""
    try:
        df = pd.read_csv(file_path)
        suppliers = df.to_dict('records')
        print(f"✅ Loaded {len(suppliers)} suppliers from {file_path}")
        return suppliers
    except Exception as e:
        print(f"❌ Error loading supplier data: {e}")
        return []


def validate_supplier_data(suppliers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Validate supplier data and return statistics."""
    if not suppliers:
        return {
            'valid': False,
            'total_suppliers': 0,
            'errors': ['No suppliers found']
        }
    
    validation_results = {
        'valid': True,
        'total_suppliers': len(suppliers),
        'countries': set(),
        'industries': set(),
        'supplier_types': set(),
        'risk_levels': set(),
        'errors': [],
        'warnings': []
    }
    
    for supplier in suppliers:
        # Collect statistics
        validation_results['countries'].add(supplier.get('country', ''))
        validation_results['industries'].add(supplier.get('industry', ''))
        validation_results['supplier_types'].add(supplier.get('supplier_type', ''))
        validation_results['risk_levels'].add(supplier.get('risk_level', ''))
    
    # Convert sets to lists for JSON serialization
    validation_results['countries'] = list(validation_results['countries'])
    validation_results['industries'] = list(validation_results['industries'])
    validation_results['supplier_types'] = list(validation_results['supplier_types'])
    validation_results['risk_levels'] = list(validation_results['risk_levels'])
    
    return validation_results


def get_external_data() -> Dict[str, Any]:
    """Get mock external ESG and compliance data."""
    return {
        "country_esg_ratings": {
            "Germany": 0.85,
            "Denmark": 0.90,
            "Canada": 0.80,
            "USA": 0.75,
            "Israel": 0.80,
            "Thailand": 0.60,
            "Mexico": 0.65,
            "India": 0.55,
            "Malaysia": 0.65,
            "Turkey": 0.50,
            "Argentina": 0.45,
            "Brazil": 0.40,
            "Vietnam": 0.45,
            "China": 0.35,
            "Russia": 0.25,
            "Ukraine": 0.20,
            "Iran": 0.15,
            "Bangladesh": 0.30
        },
        "sanction_lists": [
            {"entity": "Chemical Manufacturing", "country": "Iran", "reason": "Trade sanctions"},
            {"entity": "Steel Dynamics", "country": "Ukraine", "reason": "Conflict zone"},
            {"entity": "MetalCorp Industries", "country": "Russia", "reason": "Trade restrictions"}
        ],
        "violation_database": {
            "Chemical Solutions Ltd": ["Environmental violations", "Safety violations"],
            "Textile Mills Ltd": ["Labor violations", "Safety violations"],
            "Chemical Manufacturing": ["Sanctions violations", "Environmental violations"],
            "Steel Dynamics": ["Trade violations", "Safety violations"]
        },
        "sustainability_reports": {
            "GreenTech Solutions": {"rating": 0.85, "certifications": ["ISO_14001", "GRI_Standards"]},
            "Clean Energy Systems": {"rating": 0.90, "certifications": ["ISO_14001", "SA8000"]},
            "Organic Foods Co": {"rating": 0.80, "certifications": ["Organic", "Fair Trade"]}
        }
    }


def analyze_supplier_risks(suppliers: List[Dict[str, Any]], external_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Analyze risks for each supplier."""
    risk_analysis = []
    
    # Risk factor weights
    risk_factors = {
        "country_esg_rating": {"weight": 0.25, "threshold": 0.6},
        "prior_violations": {"weight": 0.30, "threshold": 0.7},
        "supply_category_risk": {"weight": 0.20, "threshold": 0.5},
        "financial_stability": {"weight": 0.25, "threshold": 0.6}
    }
    
    for supplier in suppliers:
        # Calculate individual risk factors
        country_esg_risk = calculate_country_esg_risk(supplier, external_data)
        violation_risk = calculate_violation_risk(supplier, external_data)
        category_risk = calculate_category_risk(supplier)
        financial_risk = calculate_financial_risk(supplier)
        
        # Calculate composite risk score
        composite_score = (
            country_esg_risk * risk_factors["country_esg_rating"]["weight"] +
            violation_risk * risk_factors["prior_violations"]["weight"] +
            category_risk * risk_factors["supply_category_risk"]["weight"] +
            financial_risk * risk_factors["financial_stability"]["weight"]
        )
        
        # Determine risk level
        risk_level = determine_risk_level(composite_score)
        
        # Generate risk flags
        flags = generate_risk_flags(supplier, external_data)
        
        risk_analysis.append({
            "supplier_id": supplier["id"],
            "supplier_name": supplier["name"],
            "country": supplier["country"],
            "industry": supplier["industry"],
            "risk_factors": {
                "country_esg_rating": country_esg_risk,
                "prior_violations": violation_risk,
                "supply_category_risk": category_risk,
                "financial_stability": financial_risk
            },
            "composite_risk_score": composite_score,
            "risk_level": risk_level,
            "flags": flags
        })
    
    return risk_analysis


def calculate_country_esg_risk(supplier: Dict[str, Any], external_data: Dict[str, Any]) -> float:
    """Calculate country ESG risk score."""
    country = supplier["country"]
    country_ratings = external_data.get("country_esg_ratings", {})
    
    # Get country rating, default to 0.5 if not found
    country_rating = country_ratings.get(country, 0.5)
    
    # Convert to risk score (higher rating = lower risk)
    return 1.0 - country_rating


def calculate_violation_risk(supplier: Dict[str, Any], external_data: Dict[str, Any]) -> float:
    """Calculate violation risk score."""
    supplier_name = supplier["name"]
    prior_violations = supplier.get("prior_violations", 0)
    violation_db = external_data.get("violation_database", {})
    
    # Base risk from prior violations
    base_risk = min(prior_violations / 10.0, 1.0)
    
    # Additional risk from violation database
    db_violations = violation_db.get(supplier_name, [])
    db_risk = len(db_violations) * 0.2
    
    return min(base_risk + db_risk, 1.0)


def calculate_category_risk(supplier: Dict[str, Any]) -> float:
    """Calculate supply category risk score."""
    category = supplier.get("supply_category", "")
    
    # Risk categories (higher risk categories)
    high_risk_categories = ["Chemicals", "Mining", "Steel", "Metals"]
    medium_risk_categories = ["Textiles", "Plastics", "Construction", "Forestry"]
    
    if category in high_risk_categories:
        return 0.8
    elif category in medium_risk_categories:
        return 0.5
    else:
        return 0.3


def calculate_financial_risk(supplier: Dict[str, Any]) -> float:
    """Calculate financial stability risk score."""
    financial_stability = supplier.get("financial_stability", 0.5)
    
    # Convert to risk score (higher stability = lower risk)
    return 1.0 - financial_stability


def determine_risk_level(composite_score: float) -> str:
    """Determine risk level based on composite score."""
    if composite_score >= 0.8:
        return "critical"
    elif composite_score >= 0.6:
        return "high"
    elif composite_score >= 0.3:
        return "medium"
    else:
        return "low"


def generate_risk_flags(supplier: Dict[str, Any], external_data: Dict[str, Any]) -> List[str]:
    """Generate risk flags for the supplier."""
    flags = []
    
    # Check sanctions
    sanction_lists = external_data.get("sanction_lists", [])
    for sanction in sanction_lists:
        if (sanction["entity"] == supplier["name"] or 
            sanction["country"] == supplier["country"]):
            flags.append(f"Sanctioned: {sanction['reason']}")
    
    # Check violations
    violation_db = external_data.get("violation_database", {})
    if supplier["name"] in violation_db:
        flags.append(f"Violations: {', '.join(violation_db[supplier['name']])}")
    
    # Check ESG score
    if supplier.get("esg_score", 1.0) < 0.3:
        flags.append("Low ESG Score")
    
    # Check financial stability
    if supplier.get("financial_stability", 1.0) < 0.4:
        flags.append("Financial Instability")
    
    return flags


def assess_esg_compliance(suppliers: List[Dict[str, Any]], external_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Assess ESG compliance for each supplier."""
    compliance_assessment = []
    
    for supplier in suppliers:
        # Assess each ESG category
        environmental_compliance = assess_environmental_compliance(supplier, external_data)
        social_compliance = assess_social_compliance(supplier, external_data)
        governance_compliance = assess_governance_compliance(supplier, external_data)
        
        # Overall compliance assessment
        overall_compliant = (
            environmental_compliance["compliant"] and
            social_compliance["compliant"] and
            governance_compliance["compliant"]
        )
        
        # Calculate compliance score
        compliance_score = (
            environmental_compliance["score"] + 
            social_compliance["score"] + 
            governance_compliance["score"]
        ) / 3.0
        
        # Generate recommendations
        recommendations = generate_compliance_recommendations(
            environmental_compliance, social_compliance, governance_compliance
        )
        
        compliance_assessment.append({
            "supplier_id": supplier["id"],
            "supplier_name": supplier["name"],
            "country": supplier["country"],
            "industry": supplier["industry"],
            "environmental": environmental_compliance,
            "social": social_compliance,
            "governance": governance_compliance,
            "overall_compliant": overall_compliant,
            "compliance_score": compliance_score,
            "recommendations": recommendations
        })
    
    return compliance_assessment


def assess_environmental_compliance(supplier: Dict[str, Any], external_data: Dict[str, Any]) -> Dict[str, Any]:
    """Assess environmental compliance."""
    issues = []
    compliant = True
    
    # Check ESG score
    esg_score = supplier.get("esg_score", 0.5)
    if esg_score < 0.4:
        issues.append("Low environmental performance score")
        compliant = False
    
    # Check industry-specific risks
    industry = supplier.get("industry", "")
    if industry in ["Chemicals", "Mining", "Steel"]:
        issues.append("High environmental impact industry")
        compliant = False
    
    # Check country environmental regulations
    country = supplier["country"]
    if country in ["China", "Russia", "Iran"]:
        issues.append("Country with weak environmental regulations")
        compliant = False
    
    return {
        "compliant": compliant,
        "issues": issues,
        "score": esg_score,
        "framework": "ISO_14001"
    }


def assess_social_compliance(supplier: Dict[str, Any], external_data: Dict[str, Any]) -> Dict[str, Any]:
    """Assess social compliance."""
    issues = []
    compliant = True
    
    # Check for labor violations
    violation_db = external_data.get("violation_database", {})
    if supplier["name"] in violation_db:
        violations = violation_db[supplier["name"]]
        if "Labor violations" in violations:
            issues.append("Labor rights violations detected")
            compliant = False
    
    # Check country labor standards
    country = supplier["country"]
    if country in ["Bangladesh", "Vietnam", "China"]:
        issues.append("Country with labor rights concerns")
        compliant = False
    
    # Check supplier type
    supplier_type = supplier.get("supplier_type", "")
    if supplier_type == "Tier 2":
        issues.append("Tier 2 supplier - limited visibility into labor practices")
        compliant = False
    
    return {
        "compliant": compliant,
        "issues": issues,
        "score": 0.7 if compliant else 0.3,
        "framework": "SA8000"
    }


def assess_governance_compliance(supplier: Dict[str, Any], external_data: Dict[str, Any]) -> Dict[str, Any]:
    """Assess governance compliance."""
    issues = []
    compliant = True
    
    # Check for sanctions
    sanction_lists = external_data.get("sanction_lists", [])
    for sanction in sanction_lists:
        if (sanction["entity"] == supplier["name"] or 
            sanction["country"] == supplier["country"]):
            issues.append(f"Sanctioned entity: {sanction['reason']}")
            compliant = False
    
    # Check financial stability
    financial_stability = supplier.get("financial_stability", 0.5)
    if financial_stability < 0.4:
        issues.append("Financial instability - governance concerns")
        compliant = False
    
    # Check transparency
    if supplier.get("esg_score", 0.5) < 0.3:
        issues.append("Low transparency in ESG reporting")
        compliant = False
    
    return {
        "compliant": compliant,
        "issues": issues,
        "score": financial_stability,
        "framework": "EU_CSDDD"
    }


def generate_compliance_recommendations(environmental: Dict[str, Any], social: Dict[str, Any], governance: Dict[str, Any]) -> List[str]:
    """Generate compliance recommendations."""
    recommendations = []
    
    if not environmental["compliant"]:
        recommendations.append("Implement environmental management system (ISO 14001)")
        recommendations.append("Conduct environmental impact assessment")
    
    if not social["compliant"]:
        recommendations.append("Implement social responsibility program (SA8000)")
        recommendations.append("Conduct labor rights audit")
    
    if not governance["compliant"]:
        recommendations.append("Implement corporate governance framework")
        recommendations.append("Conduct due diligence assessment")
    
    if not recommendations:
        recommendations.append("Maintain current compliance standards")
    
    return recommendations


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
            "non_compliant_suppliers": []
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


async def run_supply_chain_demo():
    """Run the supply chain risk audit demonstration."""
    print("🔍 Supply Chain Risk Audit - Multi-Agent Demo")
    print("=" * 60)
    
    try:
        # 1. Load and parse supplier data
        print("\n📊 Step 1: Loading Supplier Data")
        print("-" * 40)
        
        suppliers = load_supplier_data("data/suppliers.csv")
        if not suppliers:
            print("❌ No supplier data loaded. Exiting.")
            return
        
        # Validate data
        validation = validate_supplier_data(suppliers)
        print(f"📋 Data validation: {'✅ Valid' if validation['valid'] else '❌ Invalid'}")
        print(f"🌍 Countries: {len(validation['countries'])}")
        print(f"🏭 Industries: {len(validation['industries'])}")
        print(f"📦 Supplier types: {len(validation['supplier_types'])}")
        
        # 2. Get external data
        print("\n🌐 Step 2: Loading External Data")
        print("-" * 40)
        
        external_data = get_external_data()
        print(f"✅ Loaded external data:")
        print(f"   - Country ESG ratings: {len(external_data['country_esg_ratings'])} countries")
        print(f"   - Sanction lists: {len(external_data['sanction_lists'])} entries")
        print(f"   - Violation database: {len(external_data['violation_database'])} suppliers")
        print(f"   - Sustainability reports: {len(external_data['sustainability_reports'])} suppliers")
        
        # 3. Execute analysis pipeline
        print("\n🔍 Step 3: Executing Analysis Pipeline")
        print("-" * 40)
        
        # 3.1 Risk analysis
        print("\n3.1 Risk Analysis")
        risk_analysis = analyze_supplier_risks(suppliers, external_data)
        high_risk_suppliers = [s for s in risk_analysis if s['risk_level'] in ['high', 'critical']]
        
        print(f"✅ Analyzed {len(risk_analysis)} suppliers")
        print(f"🚨 Found {len(high_risk_suppliers)} high-risk suppliers")
        
        # 3.2 ESG compliance assessment
        print("\n3.2 ESG Compliance Assessment")
        compliance_assessment = assess_esg_compliance(suppliers, external_data)
        non_compliant_suppliers = [s for s in compliance_assessment if not s['overall_compliant']]
        
        print(f"✅ Assessed {len(compliance_assessment)} suppliers")
        print(f"⚠️  Found {len(non_compliant_suppliers)} non-compliant suppliers")
        
        # 4. Generate comprehensive report
        print("\n📋 Step 4: Generating Report")
        print("-" * 40)
        
        report = generate_supply_chain_report(
            suppliers=suppliers,
            risk_analysis=risk_analysis,
            compliance_assessment=compliance_assessment,
            external_data=external_data
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
        print(f"  Non-compliant: {len(non_compliant_suppliers)} suppliers")
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
        print(f"⚠️  Found {len(non_compliant_suppliers)} compliance issues")
        print(f"📋 Report saved to: {report_file}")
        
    except Exception as e:
        print(f"\n❌ Error during supply chain audit: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_supply_chain_demo()) 