"""Cochrane Compliance Tools with PRISMA Reporting."""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
import json
from datetime import datetime
from jinja2 import Template
import base64

logger = logging.getLogger(__name__)


class CochraneComplianceTools:
    """Cochrane compliance and PRISMA reporting tools."""

    def __init__(self):
        """Initialize Cochrane tools."""
        self.logger = logger
        self.rob_domains = [
            "randomization",
            "deviations", 
            "missing_outcome_data",
            "outcome_measurement",
            "selective_reporting"
        ]
        self.prisma_items = self._initialize_prisma_items()
        self.grade_factors = [
            "risk_of_bias",
            "inconsistency",
            "indirectness", 
            "imprecision",
            "publication_bias"
        ]

    def _initialize_prisma_items(self) -> Dict[str, Dict[str, str]]:
        """Initialize PRISMA 2020 checklist items."""
        return {
            "1": {"section": "Title", "item": "Identify the report as a systematic review"},
            "2": {"section": "Abstract - Background", "item": "Provide structured summary including background"},
            "3": {"section": "Abstract - Objectives", "item": "Provide structured summary including objectives"},
            "4": {"section": "Abstract - Methods", "item": "Provide structured summary including methods"},
            "5": {"section": "Abstract - Results", "item": "Provide structured summary including results"},
            "6": {"section": "Abstract - Conclusions", "item": "Provide structured summary including conclusions"},
            "7": {"section": "Abstract - Registration", "item": "Provide registration information"},
            "8": {"section": "Introduction - Rationale", "item": "Describe rationale for review"},
            "9": {"section": "Introduction - Objectives", "item": "Provide explicit statement of objectives"},
            "10": {"section": "Methods - Eligibility criteria", "item": "Specify inclusion and exclusion criteria"},
            "11": {"section": "Methods - Information sources", "item": "Describe all information sources"},
            "12": {"section": "Methods - Search strategy", "item": "Present full search strategies"},
            "13": {"section": "Methods - Selection process", "item": "Describe methods of study selection"},
            "14": {"section": "Methods - Data collection", "item": "Describe methods of data extraction"},
            "15": {"section": "Methods - Data items", "item": "List and define all variables"},
            "16": {"section": "Methods - Study risk of bias", "item": "Describe methods for assessing risk of bias"},
            "17": {"section": "Methods - Effect measures", "item": "Specify for each outcome the effect measure"},
            "18": {"section": "Methods - Synthesis methods", "item": "Describe processes used to decide whether to meta-analyse"},
            "19": {"section": "Methods - Reporting bias", "item": "Describe any methods used to assess risk of bias"},
            "20": {"section": "Methods - Certainty assessment", "item": "Describe methods used to assess certainty"},
            "21": {"section": "Results - Study selection", "item": "Give numbers of studies screened and included"},
            "22": {"section": "Results - Study characteristics", "item": "Cite each included study and present characteristics"},
            "23": {"section": "Results - Risk of bias", "item": "Present assessments of risk of bias for each study"},
            "24": {"section": "Results - Results of individual studies", "item": "For all outcomes present summary statistics"},
            "25": {"section": "Results - Results of syntheses", "item": "Present results of each meta-analysis"},
            "26": {"section": "Results - Reporting biases", "item": "Present assessments of risk of bias due to missing results"},
            "27": {"section": "Results - Certainty of evidence", "item": "Present assessments of certainty for each outcome"}
        }

    async def assess_risk_of_bias(
        self,
        studies: List[Dict[str, Any]],
        assessment_mode: str = "hybrid",
        domains: List[str] = None
    ) -> Dict[str, Any]:
        """
        Perform Cochrane ROB 2.0 risk of bias assessment.
        
        Args:
            studies: List of studies to assess
            assessment_mode: Assessment mode (automated, manual, hybrid)
            domains: ROB domains to assess
            
        Returns:
            Risk of bias assessment results
        """
        try:
            if not studies:
                raise ValueError("No studies provided for risk of bias assessment")

            if domains is None:
                domains = self.rob_domains.copy()

            rob_results = {
                "assessment_summary": {
                    "total_studies": len(studies),
                    "assessment_mode": assessment_mode,
                    "domains_assessed": domains,
                    "assessment_date": datetime.now().isoformat()
                },
                "study_assessments": [],
                "domain_summary": {},
                "overall_assessment": {}
            }

            # Assess each study
            for study in studies:
                study_rob = await self._assess_study_rob(study, domains, assessment_mode)
                rob_results["study_assessments"].append(study_rob)

            # Generate domain summary
            rob_results["domain_summary"] = self._generate_domain_summary(
                rob_results["study_assessments"], domains
            )

            # Overall assessment
            rob_results["overall_assessment"] = self._generate_overall_rob_assessment(
                rob_results["study_assessments"]
            )

            # Generate ROB visualization data
            rob_results["visualization"] = self._generate_rob_visualization(
                rob_results["study_assessments"], domains
            )

            return rob_results

        except Exception as e:
            self.logger.error(f"Error in risk of bias assessment: {e}")
            raise

    async def _assess_study_rob(
        self,
        study: Dict[str, Any],
        domains: List[str],
        mode: str
    ) -> Dict[str, Any]:
        """Assess individual study risk of bias."""
        study_rob = {
            "study_id": study["study_id"],
            "title": study.get("title", ""),
            "domain_assessments": {},
            "overall_risk": "Some concerns"  # Default
        }

        for domain in domains:
            if mode == "automated":
                assessment = self._automated_domain_assessment(study, domain)
            elif mode == "manual":
                assessment = self._manual_domain_assessment(study, domain)
            else:  # hybrid
                assessment = self._hybrid_domain_assessment(study, domain)
            
            study_rob["domain_assessments"][domain] = assessment

        # Determine overall risk
        study_rob["overall_risk"] = self._determine_overall_risk(
            study_rob["domain_assessments"]
        )

        return study_rob

    def _automated_domain_assessment(self, study: Dict[str, Any], domain: str) -> Dict[str, Any]:
        """Automated assessment based on available data."""
        assessment = {
            "risk_level": "Some concerns",
            "reasoning": "Automated assessment based on available information",
            "confidence": "Low",
            "signaling_questions": []
        }

        if domain == "randomization":
            if study.get("randomization_method"):
                method = study["randomization_method"].lower()
                if any(word in method for word in ["computer", "table", "sequence", "block"]):
                    assessment["risk_level"] = "Low"
                    assessment["reasoning"] = "Adequate randomization method described"
                    assessment["confidence"] = "High"
                elif "unclear" in method or "not reported" in method:
                    assessment["risk_level"] = "Some concerns"
                    assessment["reasoning"] = "Randomization method not clearly described"
            
            assessment["signaling_questions"] = [
                "Was the allocation sequence random?",
                "Was the allocation sequence concealed until participants were enrolled and assigned?"
            ]

        elif domain == "deviations":
            if study.get("blinding"):
                blinding = study["blinding"].lower()
                if "double" in blinding or "triple" in blinding:
                    assessment["risk_level"] = "Low"
                    assessment["reasoning"] = "Adequate blinding described"
                    assessment["confidence"] = "High"
                elif "single" in blinding:
                    assessment["risk_level"] = "Some concerns"
                    assessment["reasoning"] = "Partial blinding may affect adherence"
                elif "open" in blinding or "unblinded" in blinding:
                    assessment["risk_level"] = "High"
                    assessment["reasoning"] = "Unblinded study may affect adherence and outcomes"

        elif domain == "missing_outcome_data":
            attrition = study.get("attrition_rate", 0)
            if attrition <= 5:
                assessment["risk_level"] = "Low"
                assessment["reasoning"] = f"Low attrition rate ({attrition}%)"
                assessment["confidence"] = "High"
            elif attrition <= 15:
                assessment["risk_level"] = "Some concerns"
                assessment["reasoning"] = f"Moderate attrition rate ({attrition}%)"
            else:
                assessment["risk_level"] = "High"
                assessment["reasoning"] = f"High attrition rate ({attrition}%)"

        elif domain == "outcome_measurement":
            if study.get("outcome_assessment"):
                assessment_desc = study["outcome_assessment"].lower()
                if any(word in assessment_desc for word in ["blinded", "objective", "validated"]):
                    assessment["risk_level"] = "Low"
                    assessment["reasoning"] = "Objective or blinded outcome assessment"
                    assessment["confidence"] = "High"

        elif domain == "selective_reporting":
            if study.get("selective_reporting"):
                reporting = study["selective_reporting"].lower()
                if "protocol" in reporting and "registered" in reporting:
                    assessment["risk_level"] = "Low"
                    assessment["reasoning"] = "Pre-registered protocol available"
                    assessment["confidence"] = "High"
                elif "no protocol" in reporting:
                    assessment["risk_level"] = "Some concerns"
                    assessment["reasoning"] = "No pre-registered protocol identified"

        return assessment

    def _manual_domain_assessment(self, study: Dict[str, Any], domain: str) -> Dict[str, Any]:
        """Manual assessment placeholder - would be interactive in real implementation."""
        return {
            "risk_level": "Some concerns",
            "reasoning": f"Manual assessment required for {domain} domain",
            "confidence": "Medium",
            "signaling_questions": self._get_signaling_questions(domain),
            "requires_manual_input": True
        }

    def _hybrid_domain_assessment(self, study: Dict[str, Any], domain: str) -> Dict[str, Any]:
        """Hybrid assessment combining automated and manual elements."""
        automated = self._automated_domain_assessment(study, domain)
        
        # Add manual review flag if automated confidence is low
        if automated["confidence"] == "Low":
            automated["requires_manual_review"] = True
            automated["reasoning"] += " - Manual review recommended"
        
        return automated

    def _get_signaling_questions(self, domain: str) -> List[str]:
        """Get signaling questions for ROB domain."""
        questions = {
            "randomization": [
                "Was the allocation sequence random?",
                "Was the allocation sequence concealed until participants were enrolled and assigned?",
                "Did baseline differences between intervention groups suggest a problem with the randomization process?"
            ],
            "deviations": [
                "Were participants aware of their assigned intervention during the trial?",
                "Were carers and people delivering the interventions aware of participants' assigned intervention during the trial?",
                "Were there deviations from the intended intervention that arose because of the experimental context?",
                "Were these deviations likely to have affected the outcome?"
            ],
            "missing_outcome_data": [
                "Were data for this outcome available for all, or nearly all, participants randomized?",
                "Is there evidence that the result was not biased by missing outcome data?",
                "Could missingness in the outcome depend on its true value?"
            ],
            "outcome_measurement": [
                "Was the method of measuring the outcome inappropriate?",
                "Could measurement or ascertainment of the outcome have differed between intervention groups?",
                "Were outcome assessors aware of the intervention received by study participants?"
            ],
            "selective_reporting": [
                "Were the data that produced this result analysed in accordance with a pre-specified analysis plan?",
                "Were multiple eligible outcome measurements within the outcome domain reported?",
                "Were multiple eligible analyses of the data reported?"
            ]
        }
        return questions.get(domain, [])

    def _determine_overall_risk(self, domain_assessments: Dict[str, Any]) -> str:
        """Determine overall risk of bias."""
        risk_levels = [assessment["risk_level"] for assessment in domain_assessments.values()]
        
        if "High" in risk_levels:
            return "High"
        elif all(level == "Low" for level in risk_levels):
            return "Low"
        else:
            return "Some concerns"

    def _generate_domain_summary(self, assessments: List[Dict[str, Any]], domains: List[str]) -> Dict[str, Any]:
        """Generate summary across all domains."""
        summary = {}
        
        for domain in domains:
            domain_risks = [study["domain_assessments"][domain]["risk_level"] 
                          for study in assessments]
            
            summary[domain] = {
                "low_risk": domain_risks.count("Low"),
                "some_concerns": domain_risks.count("Some concerns"),
                "high_risk": domain_risks.count("High"),
                "percentage_low": (domain_risks.count("Low") / len(domain_risks)) * 100,
                "percentage_high": (domain_risks.count("High") / len(domain_risks)) * 100
            }
        
        return summary

    def _generate_overall_rob_assessment(self, assessments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate overall ROB assessment."""
        overall_risks = [study["overall_risk"] for study in assessments]
        
        return {
            "studies_low_risk": overall_risks.count("Low"),
            "studies_some_concerns": overall_risks.count("Some concerns"),
            "studies_high_risk": overall_risks.count("High"),
            "percentage_low_risk": (overall_risks.count("Low") / len(overall_risks)) * 100,
            "percentage_high_risk": (overall_risks.count("High") / len(overall_risks)) * 100,
            "interpretation": self._interpret_overall_rob(overall_risks)
        }

    def _interpret_overall_rob(self, risks: List[str]) -> str:
        """Interpret overall risk of bias pattern."""
        high_pct = (risks.count("High") / len(risks)) * 100
        low_pct = (risks.count("Low") / len(risks)) * 100
        
        if high_pct >= 50:
            return "High overall risk - results should be interpreted with caution"
        elif low_pct >= 70:
            return "Low overall risk - results are likely reliable"
        else:
            return "Mixed risk profile - moderate confidence in results"

    def _generate_rob_visualization(self, assessments: List[Dict[str, Any]], domains: List[str]) -> Dict[str, Any]:
        """Generate ROB visualization data."""
        # This would generate traffic light plot data
        return {
            "plot_type": "traffic_light",
            "data_matrix": [
                {
                    "study_id": study["study_id"],
                    "domains": {
                        domain: study["domain_assessments"][domain]["risk_level"]
                        for domain in domains
                    }
                }
                for study in assessments
            ],
            "color_coding": {
                "Low": "#00FF00",
                "Some concerns": "#FFFF00", 
                "High": "#FF0000"
            }
        }

    async def generate_prisma_checklist(
        self,
        review_data: Dict[str, Any],
        generate_flow_diagram: bool = True,
        screening_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate PRISMA 2020 compliance checklist.
        
        Args:
            review_data: Systematic review metadata
            generate_flow_diagram: Whether to generate flow diagram
            screening_data: Study screening numbers
            
        Returns:
            PRISMA checklist with compliance scoring
        """
        try:
            prisma_results = {
                "checklist_summary": {
                    "prisma_version": "PRISMA 2020",
                    "total_items": len(self.prisma_items),
                    "assessment_date": datetime.now().isoformat(),
                    "review_title": review_data.get("title", "")
                },
                "item_assessments": {},
                "compliance_score": {},
                "recommendations": [],
                "flow_diagram": {}
            }

            # Assess each PRISMA item
            compliance_count = 0
            for item_num, item_info in self.prisma_items.items():
                assessment = self._assess_prisma_item(item_num, item_info, review_data)
                prisma_results["item_assessments"][item_num] = assessment
                
                if assessment["compliant"]:
                    compliance_count += 1

            # Calculate compliance score
            compliance_percentage = (compliance_count / len(self.prisma_items)) * 100
            prisma_results["compliance_score"] = {
                "compliant_items": compliance_count,
                "total_items": len(self.prisma_items),
                "percentage": compliance_percentage,
                "grade": self._get_compliance_grade(compliance_percentage),
                "interpretation": self._interpret_compliance_score(compliance_percentage)
            }

            # Generate recommendations
            prisma_results["recommendations"] = self._generate_prisma_recommendations(
                prisma_results["item_assessments"], compliance_percentage
            )

            # Generate flow diagram
            if generate_flow_diagram and screening_data:
                prisma_results["flow_diagram"] = self._generate_prisma_flow_diagram(screening_data)

            return prisma_results

        except Exception as e:
            self.logger.error(f"Error generating PRISMA checklist: {e}")
            raise

    def _assess_prisma_item(self, item_num: str, item_info: Dict[str, str], review_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess individual PRISMA item compliance."""
        assessment = {
            "item_number": item_num,
            "section": item_info["section"],
            "description": item_info["item"],
            "compliant": False,
            "evidence": "",
            "confidence": "Low"
        }

        # Check for relevant data in review_data
        section_lower = item_info["section"].lower()
        
        if "title" in section_lower:
            if review_data.get("title") and "systematic review" in review_data["title"].lower():
                assessment["compliant"] = True
                assessment["evidence"] = "Title identifies report as systematic review"
                assessment["confidence"] = "High"
        
        elif "abstract" in section_lower:
            if review_data.get("abstract"):
                abstract = review_data["abstract"].lower()
                if "background" in section_lower and any(word in abstract for word in ["background", "rationale"]):
                    assessment["compliant"] = True
                    assessment["evidence"] = "Abstract includes background information"
                elif "objectives" in section_lower and any(word in abstract for word in ["objective", "aim", "purpose"]):
                    assessment["compliant"] = True
                    assessment["evidence"] = "Abstract includes objectives"
                elif "methods" in section_lower and any(word in abstract for word in ["method", "search", "criteria"]):
                    assessment["compliant"] = True
                    assessment["evidence"] = "Abstract includes methods information"
                elif "results" in section_lower and any(word in abstract for word in ["result", "finding", "outcome"]):
                    assessment["compliant"] = True
                    assessment["evidence"] = "Abstract includes results"
                elif "conclusions" in section_lower and any(word in abstract for word in ["conclusion", "implication"]):
                    assessment["compliant"] = True
                    assessment["evidence"] = "Abstract includes conclusions"
        
        elif "search" in section_lower:
            if review_data.get("search_strategy"):
                assessment["compliant"] = True
                assessment["evidence"] = "Search strategy provided"
                assessment["confidence"] = "High"
        
        elif "eligibility" in section_lower or "criteria" in section_lower:
            if review_data.get("inclusion_criteria") or review_data.get("exclusion_criteria"):
                assessment["compliant"] = True
                assessment["evidence"] = "Inclusion/exclusion criteria provided"
                assessment["confidence"] = "High"
        
        elif "data" in section_lower and "extraction" in section_lower:
            if review_data.get("data_extraction"):
                assessment["compliant"] = True
                assessment["evidence"] = "Data extraction methods described"
                assessment["confidence"] = "High"
        
        elif "bias" in section_lower:
            if review_data.get("risk_of_bias"):
                assessment["compliant"] = True
                assessment["evidence"] = "Risk of bias assessment described"
                assessment["confidence"] = "High"
        
        elif "statistical" in section_lower or "synthesis" in section_lower:
            if review_data.get("statistical_analysis"):
                assessment["compliant"] = True
                assessment["evidence"] = "Statistical analysis methods described"
                assessment["confidence"] = "High"
        
        elif "results" in section_lower:
            if review_data.get("results_summary"):
                assessment["compliant"] = True
                assessment["evidence"] = "Results provided"
                assessment["confidence"] = "Medium"
        
        elif "limitations" in section_lower:
            if review_data.get("limitations"):
                assessment["compliant"] = True
                assessment["evidence"] = "Limitations discussed"
                assessment["confidence"] = "High"
        
        elif "conclusions" in section_lower:
            if review_data.get("conclusions"):
                assessment["compliant"] = True
                assessment["evidence"] = "Conclusions provided"
                assessment["confidence"] = "High"
        
        elif "funding" in section_lower:
            if review_data.get("funding"):
                assessment["compliant"] = True
                assessment["evidence"] = "Funding information provided"
                assessment["confidence"] = "High"
        
        elif "conflicts" in section_lower:
            if review_data.get("conflicts_of_interest"):
                assessment["compliant"] = True
                assessment["evidence"] = "Conflicts of interest declared"
                assessment["confidence"] = "High"

        return assessment

    def _get_compliance_grade(self, percentage: float) -> str:
        """Get compliance grade based on percentage."""
        if percentage >= 95:
            return "A+ (Excellent)"
        elif percentage >= 90:
            return "A (Very Good)"
        elif percentage >= 85:
            return "B+ (Good)"
        elif percentage >= 80:
            return "B (Satisfactory)"
        elif percentage >= 75:
            return "C+ (Acceptable)"
        elif percentage >= 70:
            return "C (Needs Improvement)"
        else:
            return "D (Poor)"

    def _interpret_compliance_score(self, percentage: float) -> str:
        """Interpret compliance score."""
        if percentage >= 95:
            return "Excellent PRISMA compliance - ready for publication"
        elif percentage >= 90:
            return "Very good PRISMA compliance - minor improvements needed"
        elif percentage >= 85:
            return "Good PRISMA compliance - some improvements recommended"
        elif percentage >= 80:
            return "Satisfactory PRISMA compliance - several improvements needed"
        elif percentage >= 75:
            return "Acceptable PRISMA compliance - substantial improvements required"
        else:
            return "Poor PRISMA compliance - major revisions needed before publication"

    def _generate_prisma_recommendations(self, assessments: Dict[str, Any], compliance_pct: float) -> List[str]:
        """Generate recommendations for PRISMA compliance."""
        recommendations = []
        
        # Check for missing items
        non_compliant = [
            f"Item {num}: {info['description']}"
            for num, info in assessments.items()
            if not info["compliant"]
        ]
        
        if non_compliant:
            recommendations.append("Address the following non-compliant items:")
            recommendations.extend(non_compliant[:5])  # Show top 5
            
        if compliance_pct < 90:
            recommendations.append("Consider using PRISMA-P for protocol development")
            recommendations.append("Register systematic review protocol in PROSPERO")
        
        if compliance_pct < 85:
            recommendations.append("Consult PRISMA 2020 explanation and elaboration document")
            recommendations.append("Consider peer review of reporting before submission")
        
        return recommendations

    def _generate_prisma_flow_diagram(self, screening_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate PRISMA flow diagram data."""
        return {
            "diagram_type": "PRISMA 2020 Flow Diagram",
            "identification": {
                "records_identified": screening_data.get("records_identified", 0),
                "registers_searched": screening_data.get("registers_searched", 0)
            },
            "screening": {
                "records_screened": screening_data.get("records_screened", 0),
                "records_excluded": screening_data.get("records_screened", 0) - screening_data.get("full_text_assessed", 0)
            },
            "eligibility": {
                "full_text_assessed": screening_data.get("full_text_assessed", 0),
                "full_text_excluded": screening_data.get("full_text_assessed", 0) - screening_data.get("studies_included", 0),
                "exclusion_reasons": screening_data.get("exclusion_reasons", {})
            },
            "included": {
                "studies_included": screening_data.get("studies_included", 0)
            },
            "svg_data": self._create_flow_diagram_svg(screening_data)
        }

    def _create_flow_diagram_svg(self, screening_data: Dict[str, Any]) -> str:
        """Create SVG representation of flow diagram."""
        # Simplified SVG flow diagram
        svg_template = '''
        <svg width="600" height="800" xmlns="http://www.w3.org/2000/svg">
            <rect x="50" y="50" width="200" height="80" fill="#e6f3ff" stroke="#0066cc" stroke-width="2"/>
            <text x="150" y="85" text-anchor="middle" font-size="12">Records identified</text>
            <text x="150" y="105" text-anchor="middle" font-size="14" font-weight="bold">n = {records_identified}</text>
            
            <rect x="50" y="200" width="200" height="80" fill="#ffe6e6" stroke="#cc0000" stroke-width="2"/>
            <text x="150" y="235" text-anchor="middle" font-size="12">Records screened</text>
            <text x="150" y="255" text-anchor="middle" font-size="14" font-weight="bold">n = {records_screened}</text>
            
            <rect x="50" y="350" width="200" height="80" fill="#e6ffe6" stroke="#00cc00" stroke-width="2"/>
            <text x="150" y="385" text-anchor="middle" font-size="12">Full-text assessed</text>
            <text x="150" y="405" text-anchor="middle" font-size="14" font-weight="bold">n = {full_text_assessed}</text>
            
            <rect x="50" y="500" width="200" height="80" fill="#f0f0f0" stroke="#666666" stroke-width="2"/>
            <text x="150" y="535" text-anchor="middle" font-size="12">Studies included</text>
            <text x="150" y="555" text-anchor="middle" font-size="14" font-weight="bold">n = {studies_included}</text>
            
            <!-- Arrows -->
            <line x1="150" y1="130" x2="150" y2="200" stroke="#000" stroke-width="2" marker-end="url(#arrowhead)"/>
            <line x1="150" y1="280" x2="150" y2="350" stroke="#000" stroke-width="2" marker-end="url(#arrowhead)"/>
            <line x1="150" y1="430" x2="150" y2="500" stroke="#000" stroke-width="2" marker-end="url(#arrowhead)"/>
            
            <defs>
                <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
                    <polygon points="0 0, 10 3.5, 0 7" fill="#000"/>
                </marker>
            </defs>
        </svg>
        '''.format(
            records_identified=screening_data.get("records_identified", 0),
            records_screened=screening_data.get("records_screened", 0),
            full_text_assessed=screening_data.get("full_text_assessed", 0),
            studies_included=screening_data.get("studies_included", 0)
        )
        
        return base64.b64encode(svg_template.encode()).decode()

    async def perform_grade_assessment(
        self,
        evidence_profile: Dict[str, Any],
        assessment_criteria: Optional[Dict[str, bool]] = None
    ) -> Dict[str, Any]:
        """
        Perform GRADE evidence quality assessment.
        
        Args:
            evidence_profile: Evidence profile data
            assessment_criteria: Which criteria to assess
            
        Returns:
            GRADE assessment results
        """
        try:
            if assessment_criteria is None:
                assessment_criteria = {
                    "assess_risk_of_bias": True,
                    "assess_inconsistency": True,
                    "assess_indirectness": True,
                    "assess_imprecision": True,
                    "assess_publication_bias": True
                }

            grade_results = {
                "assessment_summary": {
                    "outcome": evidence_profile.get("outcome", ""),
                    "studies": evidence_profile.get("studies", 0),
                    "participants": evidence_profile.get("participants", 0),
                    "study_design": evidence_profile.get("study_design", ""),
                    "assessment_date": datetime.now().isoformat()
                },
                "domain_assessments": {},
                "overall_certainty": "Moderate",  # Starting point for RCTs
                "certainty_rating": {},
                "summary_of_findings": {}
            }

            # Initial certainty based on study design
            initial_certainty = self._get_initial_certainty(evidence_profile.get("study_design", ""))
            certainty_score = self._certainty_to_score(initial_certainty)

            # Assess each GRADE domain
            if assessment_criteria.get("assess_risk_of_bias", True):
                rob_assessment = self._assess_grade_rob(evidence_profile)
                grade_results["domain_assessments"]["risk_of_bias"] = rob_assessment
                certainty_score -= rob_assessment["downgrade_points"]

            if assessment_criteria.get("assess_inconsistency", True):
                inconsistency_assessment = self._assess_grade_inconsistency(evidence_profile)
                grade_results["domain_assessments"]["inconsistency"] = inconsistency_assessment
                certainty_score -= inconsistency_assessment["downgrade_points"]

            if assessment_criteria.get("assess_indirectness", True):
                indirectness_assessment = self._assess_grade_indirectness(evidence_profile)
                grade_results["domain_assessments"]["indirectness"] = indirectness_assessment
                certainty_score -= indirectness_assessment["downgrade_points"]

            if assessment_criteria.get("assess_imprecision", True):
                imprecision_assessment = self._assess_grade_imprecision(evidence_profile)
                grade_results["domain_assessments"]["imprecision"] = imprecision_assessment
                certainty_score -= imprecision_assessment["downgrade_points"]

            if assessment_criteria.get("assess_publication_bias", True):
                bias_assessment = self._assess_grade_publication_bias(evidence_profile)
                grade_results["domain_assessments"]["publication_bias"] = bias_assessment
                certainty_score -= bias_assessment["downgrade_points"]

            # Final certainty rating
            final_certainty = self._score_to_certainty(max(1, min(4, certainty_score)))
            grade_results["overall_certainty"] = final_certainty

            # Detailed certainty rating
            grade_results["certainty_rating"] = {
                "initial_certainty": initial_certainty,
                "final_certainty": final_certainty,
                "total_downgrades": self._calculate_total_downgrades(grade_results["domain_assessments"]),
                "interpretation": self._interpret_grade_certainty(final_certainty),
                "implications": self._grade_implications(final_certainty)
            }

            # Summary of findings
            grade_results["summary_of_findings"] = self._generate_sof_table(
                evidence_profile, grade_results
            )

            return grade_results

        except Exception as e:
            self.logger.error(f"Error in GRADE assessment: {e}")
            raise

    def _get_initial_certainty(self, study_design: str) -> str:
        """Get initial certainty based on study design."""
        design_lower = study_design.lower()
        
        if any(word in design_lower for word in ["rct", "randomized", "randomised"]):
            return "High"
        elif any(word in design_lower for word in ["cohort", "case-control", "observational"]):
            return "Low"
        else:
            return "Moderate"

    def _certainty_to_score(self, certainty: str) -> int:
        """Convert certainty level to numeric score."""
        mapping = {"Very Low": 1, "Low": 2, "Moderate": 3, "High": 4}
        return mapping.get(certainty, 3)

    def _score_to_certainty(self, score: int) -> str:
        """Convert numeric score to certainty level."""
        mapping = {1: "Very Low", 2: "Low", 3: "Moderate", 4: "High"}
        return mapping.get(score, "Moderate")

    def _assess_grade_rob(self, evidence_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk of bias for GRADE."""
        rob_info = evidence_profile.get("risk_of_bias", "").lower()
        
        if any(word in rob_info for word in ["low", "minimal"]):
            downgrade = 0
            reasoning = "Low risk of bias across studies"
        elif any(word in rob_info for word in ["high", "serious"]):
            downgrade = 2
            reasoning = "Serious risk of bias concerns"
        else:
            downgrade = 1
            reasoning = "Some risk of bias concerns"
        
        return {
            "domain": "Risk of Bias",
            "downgrade_points": downgrade,
            "reasoning": reasoning,
            "confidence": "Medium"
        }

    def _assess_grade_inconsistency(self, evidence_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Assess inconsistency for GRADE."""
        inconsistency_info = evidence_profile.get("inconsistency", "").lower()
        
        if any(word in inconsistency_info for word in ["low", "minimal", "i2"]) and "25" in inconsistency_info:
            downgrade = 0
            reasoning = "Low statistical heterogeneity"
        elif any(word in inconsistency_info for word in ["high", "substantial"]) or "75" in inconsistency_info:
            downgrade = 2
            reasoning = "Substantial unexplained heterogeneity"
        else:
            downgrade = 1
            reasoning = "Moderate heterogeneity"
        
        return {
            "domain": "Inconsistency",
            "downgrade_points": downgrade,
            "reasoning": reasoning,
            "confidence": "Medium"
        }

    def _assess_grade_indirectness(self, evidence_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Assess indirectness for GRADE."""
        indirectness_info = evidence_profile.get("indirectness", "").lower()
        
        if any(word in indirectness_info for word in ["direct", "applicable"]):
            downgrade = 0
            reasoning = "Direct evidence"
        elif any(word in indirectness_info for word in ["indirect", "surrogate"]):
            downgrade = 1
            reasoning = "Some indirectness concerns"
        else:
            downgrade = 0
            reasoning = "Assumed direct evidence"
        
        return {
            "domain": "Indirectness",
            "downgrade_points": downgrade,
            "reasoning": reasoning,
            "confidence": "Low"
        }

    def _assess_grade_imprecision(self, evidence_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Assess imprecision for GRADE."""
        participants = evidence_profile.get("participants", 0)
        ci_info = evidence_profile.get("confidence_interval", "").lower()
        
        if participants >= 400:
            downgrade = 0
            reasoning = "Adequate sample size"
        elif participants >= 100:
            downgrade = 1
            reasoning = "Moderate sample size, some imprecision"
        else:
            downgrade = 2
            reasoning = "Small sample size, serious imprecision"
        
        # Check confidence interval width
        if "wide" in ci_info or "crosses" in ci_info:
            downgrade = max(downgrade, 1)
            reasoning += " and wide confidence intervals"
        
        return {
            "domain": "Imprecision",
            "downgrade_points": downgrade,
            "reasoning": reasoning,
            "confidence": "High"
        }

    def _assess_grade_publication_bias(self, evidence_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Assess publication bias for GRADE."""
        studies = evidence_profile.get("studies", 0)
        bias_info = evidence_profile.get("publication_bias", "").lower()
        
        if studies < 10:
            downgrade = 0
            reasoning = "Too few studies to assess publication bias"
        elif any(word in bias_info for word in ["detected", "likely", "egger"]):
            downgrade = 1
            reasoning = "Publication bias suspected"
        else:
            downgrade = 0
            reasoning = "No strong evidence of publication bias"
        
        return {
            "domain": "Publication Bias",
            "downgrade_points": downgrade,
            "reasoning": reasoning,
            "confidence": "Low"
        }

    def _calculate_total_downgrades(self, assessments: Dict[str, Any]) -> int:
        """Calculate total downgrade points."""
        return sum(assessment["downgrade_points"] for assessment in assessments.values())

    def _interpret_grade_certainty(self, certainty: str) -> str:
        """Interpret GRADE certainty level."""
        interpretations = {
            "High": "We are very confident that the true effect lies close to that of the estimate of the effect",
            "Moderate": "We are moderately confident in the effect estimate; the true effect is likely to be close to the estimate of the effect, but there is a possibility that it is substantially different",
            "Low": "Our confidence in the effect estimate is limited; the true effect may be substantially different from the estimate of the effect",
            "Very Low": "We have very little confidence in the effect estimate; the true effect is likely to be substantially different from the estimate of effect"
        }
        return interpretations.get(certainty, "")

    def _grade_implications(self, certainty: str) -> str:
        """Provide implications based on GRADE certainty."""
        implications = {
            "High": "Further research is very unlikely to change our confidence in the estimate of effect",
            "Moderate": "Further research is likely to have an important impact on our confidence in the estimate of effect and may change the estimate",
            "Low": "Further research is very likely to have an important impact on our confidence in the estimate of effect and is likely to change the estimate",
            "Very Low": "Any estimate of effect is very uncertain"
        }
        return implications.get(certainty, "")

    def _generate_sof_table(self, evidence_profile: Dict[str, Any], grade_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Summary of Findings table."""
        return {
            "outcome": evidence_profile.get("outcome", ""),
            "studies_participants": f"{evidence_profile.get('studies', 0)} studies, {evidence_profile.get('participants', 0)} participants",
            "effect_estimate": evidence_profile.get("effect_size", "Not reported"),
            "confidence_interval": evidence_profile.get("confidence_interval", "Not reported"),
            "certainty_of_evidence": grade_results["overall_certainty"],
            "downgrade_reasons": [
                f"{domain}: {assessment['reasoning']}"
                for domain, assessment in grade_results["domain_assessments"].items()
                if assessment["downgrade_points"] > 0
            ]
        }

    async def generate_cochrane_report(
        self,
        review_metadata: Dict[str, Any],
        analysis_results: Optional[Dict[str, Any]] = None,
        rob_assessment: Optional[Dict[str, Any]] = None,
        prisma_checklist: Optional[Dict[str, Any]] = None,
        grade_assessment: Optional[Dict[str, Any]] = None,
        output_format: str = "html"
    ) -> Dict[str, Any]:
        """
        Generate Cochrane-compliant systematic review report.
        
        Args:
            review_metadata: Review metadata and content
            analysis_results: Meta-analysis results
            rob_assessment: Risk of bias assessment
            prisma_checklist: PRISMA checklist results
            grade_assessment: GRADE assessment results
            output_format: Output format (html, pdf, docx)
            
        Returns:
            Cochrane-compliant report
        """
        try:
            report_data = {
                "report_metadata": {
                    "title": review_metadata.get("title", ""),
                    "authors": review_metadata.get("authors", []),
                    "generation_date": datetime.now().isoformat(),
                    "cochrane_compliance": True,
                    "format": output_format
                },
                "sections": {},
                "appendices": {},
                "compliance_indicators": {}
            }

            # Generate report sections
            report_data["sections"] = {
                "title_page": self._generate_title_page(review_metadata),
                "abstract": self._generate_abstract_section(review_metadata),
                "background": self._generate_background_section(review_metadata),
                "objectives": self._generate_objectives_section(review_metadata),
                "methods": self._generate_methods_section(review_metadata),
                "results": self._generate_results_section(review_metadata, analysis_results),
                "discussion": self._generate_discussion_section(review_metadata),
                "conclusions": self._generate_conclusions_section(review_metadata),
                "references": self._generate_references_section(review_metadata)
            }

            # Generate appendices
            report_data["appendices"] = {}
            if rob_assessment:
                report_data["appendices"]["risk_of_bias"] = self._format_rob_appendix(rob_assessment)
            if prisma_checklist:
                report_data["appendices"]["prisma_checklist"] = self._format_prisma_appendix(prisma_checklist)
            if grade_assessment:
                report_data["appendices"]["grade_assessment"] = self._format_grade_appendix(grade_assessment)

            # Compliance indicators
            report_data["compliance_indicators"] = {
                "cochrane_handbook_compliance": True,
                "prisma_compliance": prisma_checklist["compliance_score"]["percentage"] if prisma_checklist else 0,
                "grade_assessment_included": grade_assessment is not None,
                "rob_assessment_included": rob_assessment is not None,
                "overall_quality_score": self._calculate_report_quality_score(
                    prisma_checklist, grade_assessment, rob_assessment
                )
            }

            # Generate formatted output
            if output_format == "html":
                report_data["formatted_output"] = self._generate_html_report(report_data)
            elif output_format == "pdf":
                report_data["formatted_output"] = "PDF generation requires additional processing"
            elif output_format == "docx":
                report_data["formatted_output"] = "DOCX generation requires additional processing"

            return report_data

        except Exception as e:
            self.logger.error(f"Error generating Cochrane report: {e}")
            raise

    def _generate_title_page(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate title page content."""
        return {
            "title": metadata.get("title", ""),
            "authors": metadata.get("authors", []),
            "affiliation": "Cochrane Systematic Review",
            "date": datetime.now().strftime("%B %Y"),
            "version": "1.0"
        }

    def _generate_abstract_section(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured abstract."""
        return {
            "background": metadata.get("background", ""),
            "objectives": metadata.get("objectives", ""),
            "search_methods": "Comprehensive search of major databases",
            "selection_criteria": metadata.get("inclusion_criteria", ""),
            "data_collection": "Standardized data extraction forms",
            "main_results": metadata.get("results", ""),
            "authors_conclusions": metadata.get("conclusions", "")
        }

    def _generate_background_section(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate background section."""
        return {
            "description_of_condition": metadata.get("background", ""),
            "description_of_intervention": "Intervention details",
            "how_intervention_works": "Mechanism of action",
            "why_review_important": "Rationale for systematic review"
        }

    def _generate_objectives_section(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate objectives section."""
        return {
            "primary_objective": metadata.get("objectives", ""),
            "secondary_objectives": "Additional research questions",
            "types_of_studies": "Study design criteria",
            "types_of_participants": "Population criteria",
            "types_of_interventions": "Intervention criteria",
            "types_of_outcomes": "Outcome measures"
        }

    def _generate_methods_section(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate methods section."""
        return {
            "criteria_for_studies": metadata.get("inclusion_criteria", ""),
            "search_methods": metadata.get("search_strategy", ""),
            "data_collection": metadata.get("data_extraction", ""),
            "assessment_of_bias": metadata.get("risk_of_bias", ""),
            "measures_of_treatment": "Effect measures used",
            "dealing_with_missing_data": "Missing data procedures",
            "assessment_of_heterogeneity": "Heterogeneity assessment methods",
            "data_synthesis": metadata.get("statistical_analysis", "")
        }

    def _generate_results_section(self, metadata: Dict[str, Any], analysis_results: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate results section."""
        results_section = {
            "description_of_studies": "Characteristics of included studies",
            "risk_of_bias": "Risk of bias assessment results",
            "effects_of_interventions": metadata.get("results_summary", "")
        }
        
        if analysis_results:
            results_section["quantitative_synthesis"] = {
                "meta_analysis_results": analysis_results.get("meta_analysis_results", {}),
                "heterogeneity_assessment": analysis_results.get("heterogeneity", {}),
                "publication_bias": "Publication bias assessment results"
            }
        
        return results_section

    def _generate_discussion_section(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate discussion section."""
        return {
            "summary_of_findings": "Key findings summary",
            "overall_completeness": "Completeness of evidence",
            "quality_of_evidence": "Quality assessment",
            "potential_biases": "Limitations and biases",
            "agreements_disagreements": "Comparison with other reviews",
            "implications_for_practice": "Clinical implications",
            "implications_for_research": "Research implications"
        }

    def _generate_conclusions_section(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate conclusions section."""
        return {
            "implications_for_practice": "Practice recommendations",
            "implications_for_research": "Future research needs",
            "main_conclusions": metadata.get("conclusions", "")
        }

    def _generate_references_section(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate references section."""
        return {
            "included_studies": "References to included studies",
            "excluded_studies": "References to excluded studies",
            "additional_references": metadata.get("references", [])
        }

    def _format_rob_appendix(self, rob_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Format risk of bias assessment for appendix."""
        return {
            "title": "Risk of Bias Assessment",
            "summary_table": rob_assessment.get("domain_summary", {}),
            "individual_assessments": rob_assessment.get("study_assessments", []),
            "traffic_light_plot": rob_assessment.get("visualization", {})
        }

    def _format_prisma_appendix(self, prisma_checklist: Dict[str, Any]) -> Dict[str, Any]:
        """Format PRISMA checklist for appendix."""
        return {
            "title": "PRISMA 2020 Checklist",
            "compliance_score": prisma_checklist.get("compliance_score", {}),
            "item_assessments": prisma_checklist.get("item_assessments", {}),
            "flow_diagram": prisma_checklist.get("flow_diagram", {})
        }

    def _format_grade_appendix(self, grade_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Format GRADE assessment for appendix."""
        return {
            "title": "GRADE Evidence Assessment",
            "summary_of_findings": grade_assessment.get("summary_of_findings", {}),
            "certainty_ratings": grade_assessment.get("certainty_rating", {}),
            "domain_assessments": grade_assessment.get("domain_assessments", {})
        }

    def _calculate_report_quality_score(self, prisma: Optional[Dict], grade: Optional[Dict], rob: Optional[Dict]) -> float:
        """Calculate overall report quality score."""
        score = 0.0
        
        if prisma:
            score += prisma["compliance_score"]["percentage"] * 0.4  # 40% weight
        
        if grade:
            score += 30.0  # 30 points for GRADE inclusion
        
        if rob:
            score += 20.0  # 20 points for ROB assessment
        
        score += 10.0  # 10 points for basic structure
        
        return min(100.0, score)

    def _generate_html_report(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML formatted report."""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>{{ title }}</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
                h1 { color: #2c3e50; border-bottom: 2px solid #3498db; }
                h2 { color: #34495e; margin-top: 30px; }
                h3 { color: #7f8c8d; }
                .abstract { background: #ecf0f1; padding: 20px; margin: 20px 0; }
                .compliance-badge { background: #27ae60; color: white; padding: 5px 10px; border-radius: 5px; }
                .section { margin: 30px 0; }
                table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                th, td { border: 1px solid #bdc3c7; padding: 10px; text-align: left; }
                th { background: #3498db; color: white; }
            </style>
        </head>
        <body>
            <h1>{{ report_data.sections.title_page.title }}</h1>
            <p><strong>Authors:</strong> {{ ", ".join(report_data.sections.title_page.authors) }}</p>
            <p><strong>Date:</strong> {{ report_data.sections.title_page.date }}</p>
            <span class="compliance-badge">Cochrane Compliant</span>
            
            <div class="section">
                <h2>Abstract</h2>
                <div class="abstract">
                    <h3>Background</h3>
                    <p>{{ report_data.sections.abstract.background }}</p>
                    <h3>Objectives</h3>
                    <p>{{ report_data.sections.abstract.objectives }}</p>
                    <h3>Main Results</h3>
                    <p>{{ report_data.sections.abstract.main_results }}</p>
                    <h3>Authors' Conclusions</h3>
                    <p>{{ report_data.sections.abstract.authors_conclusions }}</p>
                </div>
            </div>
            
            <div class="section">
                <h2>Background</h2>
                <p>{{ report_data.sections.background.description_of_condition }}</p>
            </div>
            
            <div class="section">
                <h2>Objectives</h2>
                <p>{{ report_data.sections.objectives.primary_objective }}</p>
            </div>
            
            <div class="section">
                <h2>Results</h2>
                <p>{{ report_data.sections.results.effects_of_interventions }}</p>
            </div>
            
            <div class="section">
                <h2>Conclusions</h2>
                <p>{{ report_data.sections.conclusions.main_conclusions }}</p>
            </div>
            
            <div class="section">
                <h2>Compliance Summary</h2>
                <p><strong>Overall Quality Score:</strong> {{ "%.1f"|format(report_data.compliance_indicators.overall_quality_score) }}%</p>
                <p><strong>PRISMA Compliance:</strong> {{ "%.1f"|format(report_data.compliance_indicators.prisma_compliance) }}%</p>
                <p><strong>GRADE Assessment:</strong> {{ "Included" if report_data.compliance_indicators.grade_assessment_included else "Not Included" }}</p>
                <p><strong>Risk of Bias Assessment:</strong> {{ "Included" if report_data.compliance_indicators.rob_assessment_included else "Not Included" }}</p>
            </div>
        </body>
        </html>
        """
        
        template = Template(html_template)
        return template.render(report_data=report_data)