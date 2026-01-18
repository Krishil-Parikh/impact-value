"""
Barrier score calculation service
Handles all barrier score calculations with proper normalization
"""
from typing import Dict, Any
from pydantic import BaseModel


def safe_div(x: float, y: float) -> float:
    """Safe division to avoid division by zero"""
    return x / y if y != 0 else 0


def classify_barrier_score(score: float) -> str:
    """Classify barrier severity based on score"""
    if score <= 3.0:
        return "Low"
    elif score <= 7.0:
        return "Moderate"
    elif score <= 8.5:
        return "High"
    else:
        return "Critically High"


def calculate_barrier_scores(barriers: Dict[str, BaseModel]) -> Dict[str, Dict[str, Any]]:
    """
    Calculate scores for all 15 barriers
    Returns a dictionary with barrier names as keys and score details as values
    """
    results = {}

    # BARRIER 1: Lack of training for workers and managers
    b = barriers["barrier1"]
    s1 = (1 - safe_div(min(b.num_training_programs, 5.0), 5)) * 0.2 * 10
    s2 = (1 - b.pct_employees_trained / 100) * 0.5 * 10
    s3 = (1 - safe_div(b.pct_budget_training_of_payroll, 2.5)) * 0.3 * 10
    total = s1 + s2 + s3
    results["barrier1"] = {
        "name": "Lack of training for workers and managers",
        "indicators": {
            "num_training_programs_score": s1,
            "pct_employees_trained_score": s2,
            "pct_budget_training_of_payroll_score": s3
        },
        "total": max(0, min(10, total)),
        "level": classify_barrier_score(total)
    }

    # BARRIER 2: Resistance to change
    b = barriers["barrier2"]
    s1 = safe_div(b.employee_turnover_rate_pct, 20) * 0.4 * 10
    s2 = (b.pct_employees_resisting / 100) * 0.35 * 10
    s3 = (1 - safe_div(b.num_feedback_sessions, 12)) * 0.25 * 10
    total = s1 + s2 + s3
    results["barrier2"] = {
        "name": "Resistance to change",
        "indicators": {
            "employee_turnover_rate_pct_score": s1,
            "pct_employees_resisting_score": s2,
            "num_feedback_sessions_score": s3
        },
        "total": max(0, min(10, total)),
        "level": classify_barrier_score(total)
    }

    # BARRIER 3: Lack of digital culture and training
    b = barriers["barrier3"]
    s1 = (1 - safe_div(b.num_digital_skills_workshops, 5)) * 0.2 * 10
    s2 = (1 - b.pct_comfortable_digital_tools / 100) * 0.4 * 10
    s3 = (1 - b.adoption_rate_new_digital_tools_pct / 100) * 0.4 * 10
    total = s1 + s2 + s3
    results["barrier3"] = {
        "name": "Lack of digital culture and training",
        "indicators": {
            "num_digital_skills_workshops_score": s1,
            "pct_comfortable_digital_tools_score": s2,
            "adoption_rate_new_digital_tools_pct_score": s3
        },
        "total": max(0, min(10, total)),
        "level": classify_barrier_score(total)
    }

    # BARRIER 4: Higher investment in employees' training
    b = barriers["barrier4"]
    s1 = (1 - safe_div(b.pct_training_expenditure_of_op_costs, 5)) * 0.4 * 10
    s2 = safe_div(b.avg_training_hours_per_employee, 40) * 0.3 * 10
    s3 = (1 - b.roi_training_programs_pct / 100) * 0.3 * 10
    total = s1 + s2 + s3
    results["barrier4"] = {
        "name": "Higher investment in employees' training.",
        "indicators": {
            "pct_training_expenditure_of_op_costs_score": s1,
            "avg_training_hours_per_employee_score": s2,
            "roi_training_programs_pct_score": s3
        },
        "total": max(0, min(10, total)),
        "level": classify_barrier_score(total)
    }

    # BARRIER 5: Lack of knowledge management systems
    b = barriers["barrier5"]
    s1 = (1 - safe_div(b.num_knowledge_sharing_sessions, 24)) * 0.3 * 10
    s2 = (1 - b.pct_employees_access_kms / 100) * 0.4 * 10
    freq_map = {"Daily": 0, "Weekly": 0.25, "Monthly": 0.5, "Quarterly": 0.75, "Bi-Annually": 0.875, "Annually": 1.0}
    s3 = freq_map.get(b.freq_updates_kms, 0.75) * 0.3 * 10
    total = s1 + s2 + s3
    results["barrier5"] = {
        "name": "Lack of knowledge management systems",
        "indicators": {
            "num_knowledge_sharing_sessions_score": s1,
            "pct_employees_access_kms_score": s2,
            "freq_updates_kms_score": s3
        },
        "total": max(0, min(10, total)),
        "level": classify_barrier_score(total)
    }

    # BARRIER 6: Regulatory compliance issues
    b = barriers["barrier6"]
    s1 = safe_div(b.num_non_compliance_incidents, 5) * 0.4 * 10
    s2 = (b.pct_projects_delayed_regulatory / 100) * 0.4 * 10
    s3 = safe_div(b.time_to_achieve_compliance_days, 180) * 0.2 * 10
    total = s1 + s2 + s3
    results["barrier6"] = {
        "name": "Regulatory compliance issues",
        "indicators": {
            "num_non_compliance_incidents_score": s1,
            "pct_projects_delayed_regulatory_score": s2,
            "time_to_achieve_compliance_days_score": s3
        },
        "total": max(0, min(10, total)),
        "level": classify_barrier_score(total)
    }

    # BARRIER 7: Lack of Standards and Reference Architecture
    b = barriers["barrier7"]
    s1 = (1 - safe_div(b.num_industry_standards_adopted, 10)) * 0.35 * 10
    s2 = (1 - safe_div(b.pct_iot_devices_conforming, 50)) * 0.4 * 10
    s3 = (b.pct_projects_delayed_standardized_solutions / 100) * 0.25 * 10
    total = s1 + s2 + s3
    results["barrier7"] = {
        "name": "Lack of Standards and Reference Architecture",
        "indicators": {
            "num_industry_standards_adopted_score": s1,
            "pct_iot_devices_conforming_score": s2,
            "pct_projects_delayed_standardized_solutions_score": s3
        },
        "total": max(0, min(10, total)),
        "level": classify_barrier_score(total)
    }

    # BARRIER 8: Lack of Internet coverage and IT facilities
    b = barriers["barrier8"]
    s1 = (1 - b.pct_internet_coverage / 100) * 0.3 * 10
    s2 = (1 - safe_div(b.avg_internet_speed_mbps, 50)) * 0.2 * 10
    s3 = safe_div(b.freq_it_infrastructure_outages_per_month, 8) * 0.5 * 10
    total = s1 + s2 + s3
    results["barrier8"] = {
        "name": "Lack of Internet coverage and IT facilities",
        "indicators": {
            "pct_internet_coverage_score": s1,
            "avg_internet_speed_mbps_score": s2,
            "freq_it_infrastructure_outages_per_month_score": s3
        },
        "total": max(0, min(10, total)),
        "level": classify_barrier_score(total)
    }

    # BARRIER 9: Limited Access to Funding and Credit
    b = barriers["barrier9"]
    s1 = (1 - safe_div(b.pct_loan_approved, 5)) * 0.4 * 10
    s2 = (b.pct_projects_delayed_lack_funding / 100) * 0.4 * 10
    s3 = (1 - b.ratio_external_funding_total_project_costs_pct / 100) * 0.2 * 10
    total = s1 + s2 + s3
    results["barrier9"] = {
        "name": "Limited Access to Funding and Credit",
        "indicators": {
            "pct_loan_approved_score": s1,
            "pct_projects_delayed_lack_funding_score": s2,
            "ratio_external_funding_total_project_costs_pct_score": s3
        },
        "total": max(0, min(10, total)),
        "level": classify_barrier_score(total)
    }

    # BARRIER 10: Future viability & profitability
    b = barriers["barrier10"]
    s1 = (1 - safe_div(b.yoy_revenue_growth_iot_pct, 20)) * 0.4 * 10
    s2 = (1 - safe_div(b.profit_margin_improvement_iot_pct, 5)) * 0.4 * 10
    s3 = (1 - safe_div(b.num_new_revenue_streams_iot, 3)) * 0.2 * 10
    total = s1 + s2 + s3
    results["barrier10"] = {
        "name": "Future viability & profitability",
        "indicators": {
            "yoy_revenue_growth_iot_pct_score": s1,
            "profit_margin_improvement_iot_pct_score": s2,
            "num_new_revenue_streams_iot_score": s3
        },
        "total": max(0, min(10, total)),
        "level": classify_barrier_score(total)
    }

    # BARRIER 11: Dependency on External Vendors
    b = barriers["barrier11"]
    s1 = (b.pct_critical_operations_reliant_vendor / 100) * 0.4 * 10
    s2 = safe_div(b.num_vendor_delays_disruptions_per_year, 5) * 0.4 * 10
    s3 = (b.cost_vendor_contracts_pct_op_expenses / 100) * 0.2 * 10
    total = s1 + s2 + s3
    results["barrier11"] = {
        "name": "Dependency on External Vendors",
        "indicators": {
            "pct_critical_operations_reliant_vendor_score": s1,
            "num_vendor_delays_disruptions_per_year_score": s2,
            "cost_vendor_contracts_pct_op_expenses_score": s3
        },
        "total": max(0, min(10, total)),
        "level": classify_barrier_score(total)
    }

    # BARRIER 12: High Implementation Cost
    b = barriers["barrier12"]
    s1 = (b.pct_it_budget_allocated_iot / 100) * 0.4 * 10
    s2 = safe_div(b.annual_maintenance_costs_pct_op_costs, 5) * 0.3 * 10
    s3 = (b.integration_costs_pct_total_project_cost / 100) * 0.3 * 10
    total = s1 + s2 + s3
    results["barrier12"] = {
        "name": "High Implementation Cost",
        "indicators": {
            "pct_it_budget_allocated_iot_score": s1,
            "annual_maintenance_costs_pct_op_costs_score": s2,
            "integration_costs_pct_total_project_cost_score": s3
        },
        "total": max(0, min(10, total)),
        "level": classify_barrier_score(total)
    }

    # BARRIER 13: Compliance with Sector-Specific Regulations
    b = barriers["barrier13"]
    s1 = safe_div(b.num_regulatory_violations_penalties, 4) * 0.5 * 10
    s2 = (1 - b.pct_compliance_audits_passed_without_issues / 100) * 0.3 * 10
    freq_map = {"Monthly": 0.25, "Quarterly": 0.5, "Bi-Annually": 0.75, "Annually": 1.0}
    s3 = freq_map.get(b.freq_updates_internal_policies, 0.75) * 0.2 * 10
    total = s1 + s2 + s3
    results["barrier13"] = {
        "name": "Compliance with Sector-Specific Regulations",
        "indicators": {
            "num_regulatory_violations_penalties_score": s1,
            "pct_compliance_audits_passed_without_issues_score": s2,
            "freq_updates_internal_policies_score": s3
        },
        "total": max(0, min(10, total)),
        "level": classify_barrier_score(total)
    }

    # BARRIER 14: Lack of Regulations and Standards
    b = barriers["barrier14"]
    s1 = (1 - b.pct_standards_compliant_iot_devices / 100) * 0.4 * 10
    s2 = (1 - safe_div(b.num_industry_specific_guidelines_implemented, 10)) * 0.6 * 10
    total = s1 + s2
    results["barrier14"] = {
        "name": "Lack of Regulations and Standards",
        "indicators": {
            "pct_standards_compliant_iot_devices_score": s1,
            "num_industry_specific_guidelines_implemented_score": s2
        },
        "total": max(0, min(10, total)),
        "level": classify_barrier_score(total)
    }

    # BARRIER 15: Customers are hesitant to share data
    b = barriers["barrier15"]
    s1 = (b.pct_customers_refuse_data / 100) * 0.4 * 10
    s2 = safe_div(b.num_customer_complaints_data_sharing, 25) * 0.35 * 10
    s3 = (1 - b.pct_customer_contracts_explicit_data_sharing / 100) * 0.25 * 10
    total = s1 + s2 + s3
    results["barrier15"] = {
        "name": "Customers are hesitant to share data",
        "indicators": {
            "pct_customers_refuse_data_score": s1,
            "num_customer_complaints_data_sharing_score": s2,
            "pct_customer_contracts_explicit_data_sharing_score": s3
        },
        "total": max(0, min(10, total)),
        "level": classify_barrier_score(total)
    }

    return results
