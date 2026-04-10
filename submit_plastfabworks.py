import requests
import time
import sys
import os

BASE_URL = "http://localhost:8000"
OUTPUT_DIR = r"C:\Users\krish\OneDrive\Desktop\impact-value"

payload = {
    "company_details": {
        "company_name": "Plast Fab Works Pvt. Ltd.",
        "industry": "Plastic Injection Molding",
        "num_employees": 30,
        "annual_revenue": 3.0
    },
    "barrier1": {
        "num_training_programs": 2,
        "pct_employees_trained": 10,
        "pct_budget_training_of_payroll": 1.667
    },
    "barrier2": {
        "employee_turnover_rate_pct": 0,
        "pct_employees_resisting": 40,
        "num_feedback_sessions": 1
    },
    "barrier3": {
        "num_digital_skills_workshops": 3,
        "pct_comfortable_digital_tools": 30,
        "adoption_rate_new_digital_tools_pct": 25
    },
    "barrier4": {
        "pct_training_expenditure_of_op_costs": 1.25,
        "avg_training_hours_per_employee": 30,
        "roi_training_programs_pct": 5
    },
    "barrier5": {
        "num_knowledge_sharing_sessions": 2,
        "pct_employees_access_kms": 20,
        "freq_updates_kms": "Quarterly"
    },
    "barrier6": {
        "num_non_compliance_incidents": 0,
        "pct_projects_delayed_regulatory": 40,
        "time_to_achieve_compliance_days": 90
    },
    "barrier7": {
        "num_industry_standards_adopted": 7,
        "pct_iot_devices_conforming": 0,
        "pct_projects_delayed_standardized_solutions": 50
    },
    "barrier8": {
        "pct_internet_coverage": 70,
        "avg_internet_speed_mbps": 100,
        "freq_it_infrastructure_outages_per_month": 2
    },
    "barrier9": {
        "pct_loan_approved": 0,
        "pct_projects_delayed_lack_funding": 30,
        "ratio_external_funding_total_project_costs_pct": 15
    },
    "barrier10": {
        "yoy_revenue_growth_iot_pct": 0.3,
        "profit_margin_improvement_iot_pct": 0.5,
        "num_new_revenue_streams_iot": 0
    },
    "barrier11": {
        "pct_critical_operations_reliant_vendor": 80,
        "num_vendor_delays_disruptions_per_year": 15,
        "cost_vendor_contracts_pct_op_expenses": 35
    },
    "barrier12": {
        "pct_it_budget_allocated_iot": 50,
        "annual_maintenance_costs_pct_op_costs": 0.05,
        "integration_costs_pct_total_project_cost": 40
    },
    "barrier13": {
        "num_regulatory_violations_penalties": 0,
        "pct_compliance_audits_passed_without_issues": 60,
        "freq_updates_internal_policies": "Bi-Annually"
    },
    "barrier14": {
        "pct_standards_compliant_iot_devices": 30,
        "num_industry_specific_guidelines_implemented": 0
    },
    "barrier15": {
        "pct_customers_refuse_data": 40,
        "num_customer_complaints_data_sharing": 0,
        "pct_customer_contracts_explicit_data_sharing": 20
    },
    "cost_factor_inputs": {
        "aftermarket_services_warranty": 0,
        "depreciation": 0.02,
        "labour": 0.04,
        "maintenance_repair": 0.004,
        "raw_materials_consumables": 0.024,
        "rental_operating_lease": 0,
        "research_development": 0,
        "selling_general_administrative_expense": 0.002,
        "utilities": 0.032,
        "earnings_before_interest_taxes_ebit": 0.6,
        "financing_costs_interest": 0,
        "taxation_compliance_costs": 0.1,
        "supply_chain_logistics_costs": 0.008,
        "technology_digital_infrastructure_costs": 0.006,
        "training_skill_development_costs": 0.002,
        "regulatory_compliance_costs": 0.0028,
        "insurance_costs": 0.0096,
        "marketing_customer_acquisition_costs": 0.00048,
        "environmental_social_responsibility_costs": 0,
        "quality_control_assurance": 0.0008
    },
    "kpi_factor_inputs": {
        "asset_equipment_efficiency": 1,
        "utilities_efficiency": 0,
        "inventory_efficiency": 0,
        "process_quality": 1,
        "product_quality": 0,
        "safety_security": 0,
        "planning_scheduling_effectiveness": 1,
        "time_to_market": 0,
        "production_flexibility": 1,
        "customer_satisfaction": 0,
        "supply_chain_efficiency": 0,
        "market_share_growth": 1,
        "employee_productivity": 1,
        "return_on_investment_roi": 0,
        "financial_health_and_stability": 0,
        "talent_retention": 0,
        "customer_retention_rate": 0
    }
}


def check_health():
    print(f"Checking if backend is running at {BASE_URL} ...")
    for endpoint in ["/health", "/"]:
        try:
            resp = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            print(f"  GET {endpoint} -> {resp.status_code}")
            if resp.status_code < 500:
                print("Backend is reachable.")
                return True
        except requests.exceptions.ConnectionError:
            pass
        except Exception as e:
            print(f"  Error: {e}")
    print("Backend is NOT running. Please start the backend server and try again.")
    return False


def submit_report():
    print("\nSubmitting payload to POST /generate_report_async ...")
    resp = requests.post(f"{BASE_URL}/generate_report_async", json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    session_id = data.get("session_id")
    if not session_id:
        print(f"Unexpected response: {data}")
        sys.exit(1)
    print(f"Session ID: {session_id}")
    return session_id


def poll_status(session_id):
    print(f"\nPolling GET /status/{session_id} every 3 seconds ...")
    while True:
        resp = requests.get(f"{BASE_URL}/status/{session_id}", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        status = data.get("status", "unknown")
        print(f"  Status: {status}  |  {data.get('message', '')}")
        if status == "completed":
            print("Report generation completed!")
            return
        elif status in ("failed", "error"):
            print(f"Report generation failed: {data}")
            sys.exit(1)
        time.sleep(3)


def download_pdf(session_id, report_type, filename):
    url = f"{BASE_URL}/download/{session_id}/{report_type}"
    print(f"\nDownloading {report_type} report from {url} ...")
    resp = requests.get(url, timeout=60, stream=True)
    resp.raise_for_status()
    out_path = os.path.join(OUTPUT_DIR, filename)
    with open(out_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    size = os.path.getsize(out_path)
    print(f"  Saved to: {out_path}")
    print(f"  File size: {size:,} bytes ({size / 1024:.1f} KB)")
    return out_path, size


def main():
    if not check_health():
        sys.exit(0)

    session_id = submit_report()
    poll_status(session_id)

    comp_path, comp_size = download_pdf(
        session_id, "comprehensive", "Plast_Fab_Works_Comprehensive_Analysis.pdf"
    )
    road_path, road_size = download_pdf(
        session_id, "roadmap", "Plast_Fab_Works_Strategic_Roadmap.pdf"
    )

    print("\n--- SUMMARY ---")
    print(f"Session ID : {session_id}")
    print(f"Comprehensive Analysis : {comp_path}  ({comp_size:,} bytes)")
    print(f"Strategic Roadmap      : {road_path}  ({road_size:,} bytes)")
    print("Done.")


if __name__ == "__main__":
    main()
