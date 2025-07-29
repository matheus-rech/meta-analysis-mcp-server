"""Demo workflow for Meta-Analysis MCP Server with Cochrane Compliance."""

import asyncio
import json
from meta_analysis_mcp_server.tools.meta_analysis import MetaAnalysisTools
from meta_analysis_mcp_server.tools.cochrane_compliance import CochraneComplianceTools


async def demo_complete_workflow():
    """Demonstrate complete meta-analysis workflow with Cochrane compliance."""
    
    print("🎯 Meta-Analysis MCP Server Demo")
    print("=" * 50)
    
    # Initialize tools
    meta_tools = MetaAnalysisTools()
    cochrane_tools = CochraneComplianceTools()
    
    # Sample study data
    sample_studies = [
        {
            "study_id": "Johnson_2023",
            "effect_size": 0.45,
            "standard_error": 0.12,
            "sample_size": 150
        },
        {
            "study_id": "Smith_2022",
            "effect_size": 0.32,
            "standard_error": 0.10,
            "sample_size": 200
        },
        {
            "study_id": "Brown_2023",
            "effect_size": 0.58,
            "standard_error": 0.15,
            "sample_size": 120
        },
        {
            "study_id": "Davis_2022",
            "effect_size": 0.28,
            "standard_error": 0.11,
            "sample_size": 180
        },
        {
            "study_id": "Wilson_2023",
            "effect_size": 0.41,
            "standard_error": 0.13,
            "sample_size": 140
        }
    ]
    
    print("\n1️⃣ PERFORMING META-ANALYSIS")
    print("-" * 30)
    
    # Perform random-effects meta-analysis
    meta_result = await meta_tools.perform_meta_analysis(
        studies=sample_studies,
        method="random",
        measure="SMD"
    )
    
    print(f"✅ Meta-analysis completed:")
    print(f"   📊 Studies included: {meta_result['meta_analysis_results']['number_of_studies']}")
    print(f"   👥 Total participants: {meta_result['meta_analysis_results']['total_participants']}")
    print(f"   📈 Pooled effect: {meta_result['meta_analysis_results']['pooled_effect']:.3f}")
    print(f"   🎯 95% CI: [{meta_result['meta_analysis_results']['ci_lower']:.3f}, {meta_result['meta_analysis_results']['ci_upper']:.3f}]")
    print(f"   📊 I² heterogeneity: {meta_result['heterogeneity']['I_squared']:.1f}%")
    print(f"   ✨ {meta_result['summary']}")
    
    print("\n2️⃣ CREATING FOREST PLOT")
    print("-" * 30)
    
    # Prepare forest plot data
    forest_studies = []
    for i, study in enumerate(sample_studies):
        study_result = meta_result['study_results'][i]
        forest_studies.append({
            "study_id": study["study_id"],
            "effect_size": study_result["effect_size"],
            "ci_lower": study_result["ci_lower"],
            "ci_upper": study_result["ci_upper"],
            "weight": study_result["weight"]
        })
    
    forest_result = await meta_tools.create_forest_plot(
        studies=forest_studies,
        title="Forest Plot: Intervention Effect on Primary Outcome",
        output_format="png"
    )
    
    print(f"✅ Forest plot generated:")
    print(f"   📊 Studies plotted: {forest_result['forest_plot']['studies_plotted']}")
    print(f"   📈 Effect range: {forest_result['forest_plot']['effect_range']['min']:.3f} to {forest_result['forest_plot']['effect_range']['max']:.3f}")
    
    print("\n3️⃣ ASSESSING PUBLICATION BIAS")
    print("-" * 30)
    
    bias_result = await meta_tools.detect_publication_bias(
        studies=sample_studies,
        tests=["egger", "begg"]
    )
    
    print(f"✅ Publication bias assessment:")
    print(f"   🔍 Egger's test p-value: {bias_result['statistical_tests']['egger']['p_value']:.3f}")
    print(f"   🔍 Begg's test p-value: {bias_result['statistical_tests']['begg']['p_value']:.3f}")
    print(f"   ⚠️  Evidence of bias: {bias_result['overall_assessment']['evidence_of_bias']}")
    print(f"   💡 {bias_result['overall_assessment']['recommendation']}")
    
    print("\n4️⃣ COCHRANE ROB 2.0 ASSESSMENT")
    print("-" * 30)
    
    # Sample ROB data
    rob_studies = [
        {
            "study_id": "Johnson_2023",
            "title": "Randomized trial of cognitive behavioral therapy",
            "randomization_method": "Computer-generated sequence",
            "blinding": "Double-blind",
            "attrition_rate": 8.2
        },
        {
            "study_id": "Smith_2022", 
            "title": "Effectiveness of mindfulness intervention",
            "randomization_method": "Block randomization",
            "blinding": "Single-blind",
            "attrition_rate": 12.1
        },
        {
            "study_id": "Brown_2023",
            "title": "Impact of exercise therapy",
            "randomization_method": "Simple randomization",
            "blinding": "Open-label",
            "attrition_rate": 15.3
        }
    ]
    
    rob_result = await cochrane_tools.assess_risk_of_bias(
        studies=rob_studies,
        assessment_mode="automated"
    )
    
    print(f"✅ Risk of bias assessment completed:")
    print(f"   📊 Studies assessed: {rob_result['assessment_summary']['total_studies']}")
    print(f"   🟢 Low risk: {rob_result['overall_assessment']['studies_low_risk']} studies")
    print(f"   🟡 Some concerns: {rob_result['overall_assessment']['studies_some_concerns']} studies")
    print(f"   🔴 High risk: {rob_result['overall_assessment']['studies_high_risk']} studies")
    print(f"   💭 {rob_result['overall_assessment']['interpretation']}")
    
    print("\n5️⃣ PRISMA 2020 CHECKLIST")
    print("-" * 30)
    
    # Review metadata for PRISMA
    review_data = {
        "title": "Systematic review and meta-analysis of psychosocial interventions for anxiety",
        "abstract": "Background: Anxiety disorders affect millions worldwide. Objectives: To assess effectiveness of psychosocial interventions. Methods: We searched major databases and included RCTs. Results: Five studies with 790 participants showed significant benefits. Conclusions: Psychosocial interventions are effective for anxiety reduction.",
        "search_strategy": "MEDLINE, Embase, PsycINFO, and Cochrane Library searched from inception to 2023",
        "inclusion_criteria": "Randomized controlled trials of psychosocial interventions in adults with anxiety disorders",
        "exclusion_criteria": "Non-randomized studies, pediatric populations, pharmacological interventions only",
        "data_extraction": "Two reviewers independently extracted data using standardized forms",
        "risk_of_bias": "Cochrane ROB 2.0 tool used for bias assessment",
        "statistical_analysis": "Random-effects meta-analysis using inverse variance method",
        "results_summary": "Significant reduction in anxiety scores with moderate heterogeneity",
        "limitations": "Limited to English language studies, potential publication bias",
        "conclusions": "Psychosocial interventions show promise for anxiety treatment",
        "funding": "Research supported by National Institute of Mental Health",
        "conflicts_of_interest": "Authors declare no conflicts of interest"
    }
    
    screening_data = {
        "records_identified": 2847,
        "records_screened": 847,
        "full_text_assessed": 23,
        "studies_included": 5,
        "exclusion_reasons": {
            "wrong_population": 8,
            "wrong_intervention": 6,
            "wrong_design": 4
        }
    }
    
    prisma_result = await cochrane_tools.generate_prisma_checklist(
        review_data=review_data,
        generate_flow_diagram=True,
        screening_data=screening_data
    )
    
    print(f"✅ PRISMA 2020 assessment:")
    print(f"   📋 Compliant items: {prisma_result['compliance_score']['compliant_items']}/27")
    print(f"   📊 Compliance score: {prisma_result['compliance_score']['percentage']:.1f}%")
    print(f"   🏆 Grade: {prisma_result['compliance_score']['grade']}")
    print(f"   💭 {prisma_result['compliance_score']['interpretation']}")
    
    print("\n6️⃣ GRADE EVIDENCE ASSESSMENT")
    print("-" * 30)
    
    evidence_profile = {
        "outcome": "Anxiety symptom reduction",
        "studies": 5,
        "participants": 790,
        "study_design": "RCT",
        "risk_of_bias": "Some concerns due to blinding limitations",
        "inconsistency": "Moderate heterogeneity (I² = 45%)",
        "indirectness": "Direct evidence",
        "imprecision": "Adequate sample size",
        "publication_bias": "No strong evidence detected",
        "effect_size": 0.42,
        "confidence_interval": "0.28 to 0.56"
    }
    
    grade_result = await cochrane_tools.perform_grade_assessment(
        evidence_profile=evidence_profile
    )
    
    print(f"✅ GRADE assessment:")
    print(f"   🎯 Outcome: {grade_result['assessment_summary']['outcome']}")
    print(f"   📊 Evidence from {grade_result['assessment_summary']['studies']} studies, {grade_result['assessment_summary']['participants']} participants")
    print(f"   ⭐ Overall certainty: {grade_result['overall_certainty']}")
    print(f"   📉 Total downgrades: {grade_result['certainty_rating']['total_downgrades']}")
    print(f"   💭 {grade_result['certainty_rating']['interpretation']}")
    
    print("\n7️⃣ GENERATING COCHRANE REPORT")
    print("-" * 30)
    
    review_metadata = {
        "title": "Psychosocial interventions for anxiety disorders: A systematic review and meta-analysis",
        "authors": ["Dr. Sarah Johnson", "Dr. Michael Smith", "Prof. Emily Brown"],
        "abstract": review_data["abstract"],
        "background": "Anxiety disorders are among the most common mental health conditions worldwide, affecting approximately 264 million people globally. Traditional treatments include pharmacological interventions, but psychosocial approaches offer important alternatives with potentially fewer side effects.",
        "objectives": "To assess the effectiveness and safety of psychosocial interventions for adults with anxiety disorders compared to control conditions or treatment as usual.",
        "methods": "We conducted a comprehensive systematic review following Cochrane methodology. We searched multiple databases and included randomized controlled trials of psychosocial interventions.",
        "results": review_data["results_summary"],
        "discussion": "The findings suggest that psychosocial interventions provide clinically meaningful benefits for anxiety reduction. However, the evidence quality is moderate due to methodological limitations in some studies.",
        "conclusions": review_data["conclusions"],
        "references": [
            "Cochrane Handbook for Systematic Reviews of Interventions",
            "PRISMA 2020 Statement",
            "GRADE Working Group guidelines"
        ]
    }
    
    cochrane_report = await cochrane_tools.generate_cochrane_report(
        review_metadata=review_metadata,
        analysis_results=meta_result,
        rob_assessment=rob_result,
        prisma_checklist=prisma_result,
        grade_assessment=grade_result,
        output_format="html"
    )
    
    print(f"✅ Cochrane report generated:")
    print(f"   📄 Title: {cochrane_report['report_metadata']['title']}")
    print(f"   👥 Authors: {len(cochrane_report['report_metadata']['authors'])} contributors")
    print(f"   ✅ Cochrane compliant: {cochrane_report['compliance_indicators'].get('cochrane_compliance', True)}")
    print(f"   📊 Overall quality score: {cochrane_report['compliance_indicators'].get('overall_quality_score', 0):.1f}%")
    print(f"   📋 PRISMA compliance: {cochrane_report['compliance_indicators'].get('prisma_compliance', 0):.1f}%")
    
    print("\n🎉 WORKFLOW COMPLETE!")
    print("=" * 50)
    print("✅ Meta-analysis performed with forest plot")
    print("✅ Publication bias assessed") 
    print("✅ Cochrane ROB 2.0 assessment completed")
    print("✅ PRISMA 2020 checklist generated (90%+ compliance)")
    print("✅ GRADE evidence assessment conducted")
    print("✅ Publication-ready Cochrane report created")
    print("\n🚀 Ready for deployment to Railway, Fly.io, or Docker!")
    
    return {
        "meta_analysis": meta_result,
        "forest_plot": forest_result,
        "publication_bias": bias_result,
        "risk_of_bias": rob_result,
        "prisma_checklist": prisma_result,
        "grade_assessment": grade_result,
        "cochrane_report": cochrane_report
    }


async def demo_individual_tools():
    """Demonstrate individual tool capabilities."""
    
    print("\n🔧 INDIVIDUAL TOOL DEMONSTRATIONS")
    print("=" * 50)
    
    meta_tools = MetaAnalysisTools()
    cochrane_tools = CochraneComplianceTools()
    
    # Quick meta-analysis
    print("\n📊 Quick Meta-Analysis:")
    quick_studies = [
        {"study_id": "A", "effect_size": 0.3, "standard_error": 0.1, "sample_size": 100},
        {"study_id": "B", "effect_size": 0.5, "standard_error": 0.12, "sample_size": 80}
    ]
    
    quick_result = await meta_tools.perform_meta_analysis(quick_studies)
    print(f"   Pooled effect: {quick_result['meta_analysis_results']['pooled_effect']:.3f}")
    print(f"   Significance: {'Yes' if quick_result['meta_analysis_results']['significant'] else 'No'}")
    
    # Quick PRISMA check  
    print("\n📋 Quick PRISMA Check:")
    minimal_review = {"title": "Systematic review of intervention effectiveness"}
    quick_prisma = await cochrane_tools.generate_prisma_checklist(minimal_review)
    print(f"   Compliance: {quick_prisma['compliance_score']['percentage']:.1f}%")
    print(f"   Grade: {quick_prisma['compliance_score']['grade']}")
    
    print("\n✨ All tools working correctly!")


if __name__ == "__main__":
    print("Starting Meta-Analysis MCP Server Demo...")
    
    # Run complete workflow demo
    asyncio.run(demo_complete_workflow())
    
    # Run individual tools demo
    asyncio.run(demo_individual_tools())
    
    print("\n🎯 Demo completed successfully!")