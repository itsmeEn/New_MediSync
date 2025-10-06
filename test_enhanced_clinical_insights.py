#!/usr/bin/env python3
"""
Enhanced Clinical Insights Test Script
=====================================

This script demonstrates how the enhanced MediSync AI model converts statistical findings
(like "p < 0.05") into actionable clinical insights that doctors and nurses can understand
and act upon immediately.

Key Features Tested:
- Clinical interpretation of statistical results
- Risk stratification with clear categories
- Specific clinical recommendations
- Alert system for critical findings
- Evidence-based protocols
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.analytics.ai_insights_model import MediSyncAIInsights, generate_synthetic_data
import json
from datetime import datetime

def print_section_header(title):
    """Print a formatted section header."""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def print_subsection(title):
    """Print a formatted subsection header."""
    print(f"\n--- {title} ---")

def demonstrate_clinical_interpretation():
    """Demonstrate how statistical results are converted to clinical insights."""
    print_section_header("CLINICAL INTERPRETATION DEMONSTRATION")
    
    # Initialize the AI model
    ai_model = MediSyncAIInsights()
    
    # Generate sample data with known risk factors
    print("🔬 Generating sample healthcare data with known risk factors...")
    sample_data = generate_synthetic_data(
        num_patients=500,
        num_diseases=100,
        num_admissions=200
    )
    
    # Get AI insights
    print("🤖 Generating AI insights...")
    insights = ai_model.generate_insights(sample_data)
    
    print_subsection("BEFORE: Traditional Statistical Output")
    print("❌ What doctors/nurses typically see:")
    print("   • Age (p < 0.05)")
    print("   • Family history (p < 0.01)")
    print("   • Lifestyle factors (p < 0.05)")
    print("   ⚠️  Problem: Healthcare professionals don't know what to do with this!")
    
    print_subsection("AFTER: Enhanced Clinical Insights")
    print("✅ What doctors/nurses now see with our enhanced model:")
    
    # Display actionable insights
    if 'actionable_insights' in insights:
        actionable_insights = insights['actionable_insights']
        
        print("\n📊 DEMOGRAPHIC INSIGHTS:")
        for insight in actionable_insights.get('demographic_insights', []):
            print(f"   • {insight}")
        
        print("\n📈 HEALTH TREND INSIGHTS:")
        for insight in actionable_insights.get('health_trends', []):
            print(f"   • {insight}")
        
        print("\n🎯 PREDICTIVE INSIGHTS:")
        for insight in actionable_insights.get('illness_predictions', []):
            print(f"   • {insight}")
        
        print("\n⚡ SURGE PREDICTIONS:")
        for insight in actionable_insights.get('surge_predictions', []):
            print(f"   • {insight}")

def demonstrate_risk_stratification():
    """Demonstrate the enhanced risk stratification system."""
    print_section_header("RISK STRATIFICATION SYSTEM")
    
    ai_model = MediSyncAIInsights()
    sample_data = generate_synthetic_data(num_patients=300, num_diseases=80, num_admissions=150)
    
    # Get detailed risk assessment
    print("🎯 Performing detailed risk assessment...")
    insights = ai_model.generate_insights(sample_data)
    
    # Get detailed risk assessment
    risk_assessment = ai_model.get_detailed_risk_assessment(sample_data)
    
    print_subsection("RISK CATEGORIES & SCORES")
    risk_scores = risk_assessment.get('risk_scores', {})
    
    print(f"📊 Overall Risk Score: {risk_scores.get('overall_score', 0):.1f}%")
    print(f"👥 Demographic Risk: {risk_scores.get('demographic_risk', 0):.1f}%")
    print(f"🏥 Clinical Risk: {risk_scores.get('clinical_risk', 0):.1f}%")
    print(f"📈 Trend Risk: {risk_scores.get('trend_risk', 0):.1f}%")
    
    print_subsection("RISK LEVEL CLASSIFICATION")
    overall_risk = risk_assessment.get('overall_risk_level', 'unknown')
    print(f"🎯 Risk Level: {overall_risk.upper().replace('_', ' ')}")
    
    print_subsection("CLINICAL INDICATORS")
    clinical_indicators = risk_assessment.get('clinical_indicators', {})
    
    red_flags = clinical_indicators.get('red_flags', [])
    if red_flags:
        print("🚨 RED FLAGS (Immediate Attention Required):")
        for flag in red_flags:
            print(f"   • {flag}")
    
    warning_signs = clinical_indicators.get('warning_signs', [])
    if warning_signs:
        print("\n⚠️  WARNING SIGNS (Enhanced Monitoring):")
        for warning in warning_signs:
            print(f"   • {warning}")
    
    protective_factors = clinical_indicators.get('protective_factors', [])
    if protective_factors:
        print("\n✅ PROTECTIVE FACTORS (Positive Indicators):")
        for factor in protective_factors:
            print(f"   • {factor}")

def demonstrate_clinical_recommendations():
    """Demonstrate specific clinical recommendations based on risk factors."""
    print_section_header("CLINICAL RECOMMENDATIONS SYSTEM")
    
    ai_model = MediSyncAIInsights()
    sample_data = generate_synthetic_data(num_patients=400, num_diseases=90, num_admissions=180)
    
    print("💡 Generating evidence-based clinical recommendations...")
    
    # Get risk factor specific recommendations
    recommendations = ai_model.get_risk_factor_specific_recommendations(sample_data)
    
    print_subsection("AGE-RELATED RECOMMENDATIONS")
    age_recs = recommendations.get('age_related', {})
    if age_recs:
        print("👴 For Elderly Patients:")
        for category, actions in age_recs.items():
            if actions:
                print(f"   {category.replace('_', ' ').title()}:")
                for action in actions:
                    print(f"     • {action}")
    
    print_subsection("FAMILY HISTORY RECOMMENDATIONS")
    family_recs = recommendations.get('family_history', {})
    if family_recs:
        print("👨‍👩‍👧‍👦 For Patients with Family History:")
        for category, actions in family_recs.items():
            if actions:
                print(f"   {category.replace('_', ' ').title()}:")
                for action in actions:
                    print(f"     • {action}")
    
    print_subsection("LIFESTYLE RECOMMENDATIONS")
    lifestyle_recs = recommendations.get('lifestyle_factors', {})
    if lifestyle_recs:
        print("🏃‍♀️ Lifestyle Interventions:")
        for category, actions in lifestyle_recs.items():
            if actions:
                print(f"   {category.replace('_', ' ').title()}:")
                for action in actions:
                    print(f"     • {action}")
    
    # Get evidence-based protocols
    print_subsection("EVIDENCE-BASED PROTOCOLS")
    protocols = ai_model.generate_evidence_based_protocols(sample_data)
    
    if 'clinical_protocols' in protocols:
        print("📋 Clinical Protocols:")
        for protocol in protocols['clinical_protocols']:
            print(f"   • {protocol}")
    
    if 'nursing_protocols' in protocols:
        print("\n👩‍⚕️ Nursing Protocols:")
        for protocol in protocols['nursing_protocols']:
            print(f"   • {protocol}")

def demonstrate_alert_system():
    """Demonstrate the comprehensive alert system."""
    print_section_header("CLINICAL ALERT SYSTEM")
    
    ai_model = MediSyncAIInsights()
    sample_data = generate_synthetic_data(num_patients=600, num_diseases=120, num_admissions=250)
    
    print("🚨 Generating clinical alerts based on risk assessment...")
    
    # Get risk assessment first
    risk_assessment = ai_model.get_detailed_risk_assessment(sample_data)
    
    # Generate clinical alerts
    alerts = ai_model.generate_clinical_alerts(risk_assessment, sample_data)
    
    print_subsection("ALERT SUMMARY")
    alert_summary = alerts.get('alert_summary', {})
    print(f"📊 Total Alerts: {alert_summary.get('total_alerts', 0)}")
    print(f"🚨 Critical: {alert_summary.get('critical_count', 0)}")
    print(f"🔴 Urgent: {alert_summary.get('urgent_count', 0)}")
    print(f"🟡 Warning: {alert_summary.get('warning_count', 0)}")
    print(f"🟢 Informational: {alert_summary.get('informational_count', 0)}")
    print(f"⚡ Requires Immediate Action: {alert_summary.get('requires_immediate_action', False)}")
    
    # Display critical alerts
    critical_alerts = alerts.get('critical_alerts', [])
    if critical_alerts:
        print_subsection("🚨 CRITICAL ALERTS (Immediate Action Required)")
        for alert in critical_alerts:
            print(f"   ID: {alert['id']}")
            print(f"   Title: {alert['title']}")
            print(f"   Message: {alert['message']}")
            print(f"   Action Required: {alert['action_required']}")
            print(f"   Timeframe: {alert['timeframe']}")
            print(f"   Responsible: {alert['responsible_party']}")
            print(f"   Escalation: {alert['escalation_path']}")
            print()
    
    # Display urgent alerts
    urgent_alerts = alerts.get('urgent_alerts', [])
    if urgent_alerts:
        print_subsection("🔴 URGENT ALERTS (Prompt Attention)")
        for alert in urgent_alerts[:2]:  # Show first 2 to save space
            print(f"   ID: {alert['id']}")
            print(f"   Title: {alert['title']}")
            print(f"   Message: {alert['message']}")
            print(f"   Action Required: {alert['action_required']}")
            print(f"   Timeframe: {alert['timeframe']}")
            print()
    
    # Display immediate actions
    immediate_actions = alerts.get('immediate_actions', [])
    if immediate_actions:
        print_subsection("⚡ IMMEDIATE ACTIONS REQUIRED")
        for action in immediate_actions:
            print(f"   • {action['action']} ({action['timeframe']})")
            print(f"     Responsible: {action['responsible']}")
            print(f"     Priority: {action['priority']}")
            print()

def demonstrate_doctor_nurse_recommendations():
    """Demonstrate specific recommendations for doctors and nurses."""
    print_section_header("ROLE-SPECIFIC RECOMMENDATIONS")
    
    ai_model = MediSyncAIInsights()
    sample_data = generate_synthetic_data(num_patients=350, num_diseases=85, num_admissions=160)
    
    insights = ai_model.generate_insights(sample_data)
    
    print_subsection("👨‍⚕️ DOCTOR RECOMMENDATIONS")
    doctor_recs = insights.get('doctor_recommendations', [])
    for i, rec in enumerate(doctor_recs, 1):
        print(f"   {i}. {rec}")
    
    print_subsection("👩‍⚕️ NURSE RECOMMENDATIONS")
    nurse_recs = insights.get('nurse_recommendations', [])
    for i, rec in enumerate(nurse_recs, 1):
        print(f"   {i}. {rec}")

def main():
    """Main function to run all demonstrations."""
    print("🏥 MediSync Enhanced Clinical Insights Demonstration")
    print("=" * 80)
    print("This demonstration shows how our enhanced AI model converts")
    print("statistical findings into actionable clinical insights.")
    print(f"Test run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Run all demonstrations
        demonstrate_clinical_interpretation()
        demonstrate_risk_stratification()
        demonstrate_clinical_recommendations()
        demonstrate_alert_system()
        demonstrate_doctor_nurse_recommendations()
        
        print_section_header("SUMMARY")
        print("✅ Enhanced AI Model Successfully Tested!")
        print("\n🎯 Key Improvements:")
        print("   • Statistical results (p < 0.05) converted to actionable insights")
        print("   • Clear risk stratification with specific thresholds")
        print("   • Evidence-based clinical recommendations")
        print("   • Comprehensive alert system with priority levels")
        print("   • Role-specific guidance for doctors and nurses")
        print("   • Immediate action protocols for critical findings")
        
        print("\n💡 Impact for Healthcare Professionals:")
        print("   • Doctors know exactly what interventions to implement")
        print("   • Nurses receive specific monitoring and care protocols")
        print("   • Critical findings trigger immediate alerts with clear actions")
        print("   • Risk factors are translated into preventive measures")
        print("   • Evidence-based protocols guide clinical decision-making")
        
        print("\n🚀 Next Steps:")
        print("   • Deploy enhanced model to production environment")
        print("   • Train healthcare staff on new clinical insights interface")
        print("   • Monitor clinical outcomes and adjust recommendations")
        print("   • Integrate with existing hospital information systems")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {str(e)}")
        print("Please check the AI model implementation and try again.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)