from datetime import datetime
import json
import csv
from pymongo import MongoClient

import os
from mistralai import Mistral

client = Mistral(api_key="QbcjiOlNBfc4tmq8N1zjc1aBbITrjX1e")

def call_llm(prompt):
    response = client.chat.complete(
        model="mistral-small-latest",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=300
    )
    return response.choices[0].message.content

def get_db():
    client = MongoClient("mongodb://localhost:27017/")  # or your Atlas URI
    db = client["iot_scores_db"]  # database name
    return db

def save_raw_to_mongodb(company, barriers, kpis, costs):
    db = get_db()

    document = {
        "company_details": company,
        "barriers_raw": barriers,
        "kpi_raw": kpis,
        "cost_raw": costs
    }

    db.raw_inputs.insert_one(document)
    print("✔ Raw extracted data saved to MongoDB (raw_inputs collection)")

# -------------------------------
# 1. Extract company details
# -------------------------------
def extract_company_details(data):
    return data.get("company_details", {})

# -------------------------------
# 2. Extract all barrier scores (barrier1 → barrier15)
# -------------------------------
def extract_barrier_scores(data):
    barriers = {}
    for key, value in data.items():
        if key.startswith("barrier"):
            barriers[key] = value
    return barriers

# -------------------------------
# 3. Extract KPI factors
# -------------------------------
def extract_kpi_factors(data):
    return data.get("kpi_factor_inputs", {})

# -------------------------------
# 4. Extract Cost factors
# -------------------------------
def extract_cost_factors(data):
    return data.get("cost_factor_inputs", {})

# -------------------------------
# 5. Save extracted raw info to CSV
# -------------------------------
def save_to_csv(company, barriers, kpis, costs, filename="output.csv"):
    rows = []

    # --- Company ---
    for key, val in company.items():
        rows.append(["company_details", key, val])

    # --- Barriers raw values ---
    for barrier_name, barrier_dict in barriers.items():
        for key, val in barrier_dict.items():
            rows.append([barrier_name, key, val])

    # --- KPI ---
    for key, val in kpis.items():
        rows.append(["kpi_factor_inputs", key, val])

    # --- Costs ---
    for key, val in costs.items():
        rows.append(["cost_factor_inputs", key, val])

    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["category", "field", "value"])
        writer.writerows(rows)

    print(f"✔ Raw extracted CSV saved as {filename}")


import matplotlib.pyplot as plt
import os

def generate_barrier_charts(barrier_id, scores, output_dir="charts"):
    os.makedirs(output_dir, exist_ok=True)

    labels = ["KPI Score", "Barrier Score", "Cost Score"]
    values = [
        scores["kpi_score"],
        scores["barrier_score"],
        scores["cost_score"]
    ]

    plt.figure(figsize=(6, 4))
    bars = plt.bar(labels, values)
    plt.title(f"Barrier {barrier_id} – Score Breakdown")
    plt.ylabel("Score")

    for bar in bars:
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                 f"{round(bar.get_height(),2)}",
                 ha="center", va="bottom")

    chart_path = f"{output_dir}/barrier_{barrier_id}_scores.png"
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

    return chart_path

# -------------------------------
# BARRIER SCORE CALCULATOR
# -------------------------------
# Severity classification helper
def classify_barrier_score(score: float) -> str:
    if score <= 3.0:
        return "Low"
    elif score <= 7.0:
        return "Moderate"
    elif score <= 8.5:
        return "High"
    else:
        return "Critically High"


def calc_barrier_scores(barriers: dict):

    def safe_div(x, y):
        return x / y if y != 0 else 0

    results = {}

    # ------------------ BARRIER 1 ------------------
    b = barriers["barrier1"]
    s1 = (1 - safe_div(b["num_training_programs"], 5)) * 0.2 * 10
    s2 = (1 - b["pct_employees_trained"]) * 0.5 * 10
    s3 = (1 - safe_div(b["pct_budget_training_of_payroll"], 2.5)) * 0.3 * 10
    total = s1 + s2 + s3
    results["barrier1"] = {
        "num_training_programs_score": s1,
        "pct_employees_trained_score": s2,
        "pct_budget_training_of_payroll_score": s3,
        "total": total,
        "level": classify_barrier_score(total)
    }

    # ------------------ BARRIER 2 ------------------
    b = barriers["barrier2"]
    s1 = safe_div(b["employee_turnover_rate_pct"], 20) * 0.4 * 10
    s2 = (1 - b["pct_employees_resisting"]) * 0.35 * 10
    s3 = (1 - safe_div(b["num_feedback_sessions"], 12)) * 0.25 * 10
    total = s1 + s2 + s3
    results["barrier2"] = {
        "employee_turnover_rate_pct_score": s1,
        "pct_employees_resisting_score": s2,
        "num_feedback_sessions_score": s3,
        "total": total,
        "level": classify_barrier_score(total)
    }

    # ------------------ BARRIER 3 ------------------
    b = barriers["barrier3"]
    s1 = (1 - safe_div(b["num_digital_skills_workshops"], 5)) * 0.2 * 10
    s2 = (1 - b["pct_comfortable_digital_tools"]) * 0.4 * 10
    s3 = (1 - safe_div(b["adoption_rate_new_digital_tools_pct"], 100)) * 0.4 * 10
    total = s1 + s2 + s3
    results["barrier3"] = {
        "num_digital_skills_workshops_score": s1,
        "pct_comfortable_digital_tools_score": s2,
        "adoption_rate_new_digital_tools_pct_score": s3,
        "total": total,
        "level": classify_barrier_score(total)
    }

    # ------------------ BARRIER 4 ------------------
    b = barriers["barrier4"]
    s1 = (1 - safe_div(b["pct_training_expenditure_of_op_costs"], 5)) * 0.4 * 10
    s2 = safe_div(b["avg_training_hours_per_employee"], 40) * 0.3 * 10
    s3 = (1 - safe_div(b["roi_training_programs_pct"], 100)) * 0.3 * 10
    total = s1 + s2 + s3
    results["barrier4"] = {
        "pct_training_expenditure_of_op_costs_score": s1,
        "avg_training_hours_per_employee_score": s2,
        "roi_training_programs_pct_score": s3,
        "total": total,
        "level": classify_barrier_score(total)
    }

    # ------------------ BARRIER 5 ------------------
    b = barriers["barrier5"]
    s1 = (1 - safe_div(b["num_knowledge_sharing_sessions"], 24)) * 0.3 * 10
    s2 = (1 - safe_div(b["pct_employees_access_kms"], 100)) * 0.4 * 10

    if b["freq_updates_kms"] == "Weekly":
        freq_updates_kms = 0.25
    elif b["freq_updates_kms"] == "Monthly":
        freq_updates_kms = 0.5
    else:
        freq_updates_kms = 0.75

    s3 = freq_updates_kms * 0.3 * 10
    total = s1 + s2 + s3
    results["barrier5"] = {
        "num_knowledge_sharing_sessions_score": s1,
        "pct_employees_access_kms_score": s2,
        "freq_updates_kms_score": s3,
        "total": total,
        "level": classify_barrier_score(total)
    }

    # ------------------ BARRIER 6 ------------------
    b = barriers["barrier6"]
    s1 = safe_div(b["num_non_compliance_incidents"], 5) * 0.4 * 10
    s2 = safe_div(b["pct_projects_delayed_regulatory"], 100) * 0.4 * 10
    s3 = safe_div(b["time_to_achieve_compliance_days"], 180) * 0.2 * 10
    total = s1 + s2 + s3
    results["barrier6"] = {
        "num_non_compliance_incidents_score": s1,
        "pct_projects_delayed_regulatory_score": s2,
        "time_to_achieve_compliance_days_score": s3,
        "total": total,
        "level": classify_barrier_score(total)
    }

    # ------------------ BARRIER 7 ------------------
    b = barriers["barrier7"]
    s1 = (1 - safe_div(b["num_industry_standards_adopted"], 10)) * 0.35 * 10
    s2 = (1 - safe_div(b["pct_iot_devices_conforming"], 50)) * 0.4 * 10
    s3 = safe_div(b["pct_projects_delayed_standardized_solutions"], 100) * 0.25 * 10
    total = s1 + s2 + s3
    results["barrier7"] = {
        "num_industry_standards_adopted_score": s1,
        "pct_iot_devices_conforming_score": s2,
        "pct_projects_delayed_standardized_solutions_score": s3,
        "total": total,
        "level": classify_barrier_score(total)
    }

    # ------------------ BARRIER 8 ------------------
    b = barriers["barrier8"]
    s1 = (1 - safe_div(b["pct_internet_coverage"], 100)) * 0.3 * 10
    s2 = (1 - safe_div(b["avg_internet_speed_mbps"], 50)) * 0.2 * 10
    s3 = safe_div(b["freq_it_infrastructure_outages_per_month"], 8) * 0.5 * 10
    total = s1 + s2 + s3
    results["barrier8"] = {
        "pct_internet_coverage_score": s1,
        "avg_internet_speed_mbps_score": s2,
        "freq_it_infrastructure_outages_per_month_score": s3,
        "total": total,
        "level": classify_barrier_score(total)
    }

    # ------------------ BARRIER 9 ------------------
    b = barriers["barrier9"]
    s1 = (1 - safe_div(b["pct_loan_approved"], 5)) * 0.4 * 10
    s2 = safe_div(b["pct_projects_delayed_lack_funding"], 100) * 0.4 * 10
    s3 = (1 - safe_div(b["ratio_external_funding_total_project_costs_pct"], 100)) * 0.2 * 10
    total = s1 + s2 + s3
    results["barrier9"] = {
        "pct_loan_approved_score": s1,
        "pct_projects_delayed_lack_funding_score": s2,
        "ratio_external_funding_total_project_costs_pct_score": s3,
        "total": total,
        "level": classify_barrier_score(total)
    }

    # ------------------ BARRIER 10 ------------------
    b = barriers["barrier10"]
    s1 = (1 - safe_div(b["yoy_revenue_growth_iot_pct"], 20)) * 0.4 * 10
    s2 = (1 - safe_div(b["profit_margin_improvement_iot_pct"], 5)) * 0.4 * 10
    s3 = (1 - safe_div(b["num_new_revenue_streams_iot"], 3)) * 0.2 * 10
    total = s1 + s2 + s3
    results["barrier10"] = {
        "yoy_revenue_growth_iot_pct_score": s1,
        "profit_margin_improvement_iot_pct_score": s2,
        "num_new_revenue_streams_iot_score": s3,
        "total": total,
        "level": classify_barrier_score(total)
    }

    # ------------------ BARRIER 11 ------------------
    b = barriers["barrier11"]
    s1 = safe_div(b["pct_critical_operations_reliant_vendor"], 100) * 0.4 * 10
    s2 = (1 - (1 - safe_div(b["num_vendor_delays_disruptions_per_year"], 5))) * 0.4 * 10
    s3 = safe_div(b["cost_vendor_contracts_pct_op_expenses"], 100) * 0.2 * 10
    total = s1 + s2 + s3
    results["barrier11"] = {
        "pct_critical_operations_reliant_vendor_score": s1,
        "num_vendor_delays_disruptions_per_year_score": s2,
        "cost_vendor_contracts_pct_op_expenses_score": s3,
        "total": total,
        "level": classify_barrier_score(total)
    }

    # ------------------ BARRIER 12 ------------------
    b = barriers["barrier12"]
    s1 = safe_div(b["pct_it_budget_allocated_iot"], 100) * 0.4 * 10
    s2 = (1 - (1 - safe_div(b["annual_maintenance_costs_pct_op_costs"], 5))) * 0.3 * 10
    s3 = safe_div(b["integration_costs_pct_total_project_cost"], 100) * 0.3 * 10
    total = s1 + s2 + s3
    results["barrier12"] = {
        "pct_it_budget_allocated_iot_score": s1,
        "annual_maintenance_costs_pct_op_costs_score": s2,
        "integration_costs_pct_total_project_cost_score": s3,
        "total": total,
        "level": classify_barrier_score(total)
    }

    # ------------------ BARRIER 13 ------------------
    b = barriers["barrier13"]
    s1 = safe_div(b["num_regulatory_violations_penalties"], 4) * 0.5 * 10
    s2 = (1 - safe_div(b["pct_compliance_audits_passed_without_issues"], 100)) * 0.3 * 10

    if b["freq_updates_internal_policies"] == "Quarterly":
        freq_updates_internal_policies = 0.5
    elif b["freq_updates_internal_policies"] == "Bi-Annually":
        freq_updates_internal_policies = 0.75
    else:
        freq_updates_internal_policies = 1

    s3 = freq_updates_internal_policies * 0.5 * 10
    total = s1 + s2 + s3
    results["barrier13"] = {
        "num_regulatory_violations_penalties_score": s1,
        "pct_compliance_audits_passed_without_issues_score": s2,
        "freq_updates_internal_policies_score": s3,
        "total": total,
        "level": classify_barrier_score(total)
    }

    # ------------------ BARRIER 14 ------------------
    b = barriers["barrier14"]
    s1 = (1 - safe_div(b["pct_standards_compliant_iot_devices"], 100)) * 0.4 * 10
    s2 = (1 - safe_div(b["num_industry_specific_guidelines_implemented"], 10)) * 0.6 * 10
    total = s1 + s2
    results["barrier14"] = {
        "pct_standards_compliant_iot_devices_score": s1,
        "num_industry_specific_guidelines_implemented_score": s2,
        "total": total,
        "level": classify_barrier_score(total)
    }

    # ------------------ BARRIER 15 ------------------
    b = barriers["barrier15"]
    s1 = safe_div(b["pct_customers_refuse_data"], 100) * 0.4 * 10
    s2 = safe_div(b["num_customer_complaints_data_sharing"], 25) * 0.35 * 10
    s3 = (1 - safe_div(b["pct_customer_contracts_explicit_data_sharing"], 100)) * 0.25 * 10
    total = s1 + s2 + s3
    results["barrier15"] = {
        "pct_customers_refuse_data_score": s1,
        "num_customer_complaints_data_sharing_score": s2,
        "pct_customer_contracts_explicit_data_sharing_score": s3,
        "total": total,
        "level": classify_barrier_score(total)
    }

    return results

# -------------------------------
# CALCULATE COST FACTOR SCORES
# -------------------------------
def calc_cost_factor_scores(cost_factors: dict):
    cost_values = list(cost_factors.values())
    barrier_1 = [0,0,2,0,0,0,2,1,0,2,1,1,1,3,3,1,1,1,2,1]
    barrier_2 = [0,0,2,0,0,0,1,1,0,1,1,1,1,2,2,1,1,1,1,1]
    barrier_3 = [0,0,2,0,0,0,1,1,0,1,1,1,1,3,3,1,1,1,2,1]
    barrier_4 = [0,0,2,0,0,0,2,1,0,1,1,1,1,3,3,1,1,1,2,1]
    barrier_5 = [0,0,2,0,0,0,2,1,0,2,1,1,1,3,3,1,1,1,2,1]
    barrier_6 = [0,0,2,0,0,0,1,1,0,1,1,1,1,2,2,1,1,1,1,1]
    barrier_7 = [0,0,2,0,0,0,1,1,0,1,1,1,1,2,2,1,1,1,1,1]
    barrier_8 = [0,0,2,0,0,0,1,1,0,1,1,1,1,2,2,1,1,1,1,1]
    barrier_9 = [0,0,2,0,0,0,1,2,0,3,3,1,2,1,1,1,1,1,1,1]
    barrier_10 = [2,1,3,2,2,1,3,3,2,3,2,2,3,3,3,3,1,3,2,3]
    barrier_11 = [0,0,2,0,0,0,1,1,0,2,2,1,2,1,1,1,1,1,1,1]
    barrier_12 = [0,0,2,0,0,0,2,1,0,3,2,3,2,1,1,3,1,1,1,1]
    barrier_13 = [0,0,2,0,0,0,1,1,0,2,2,3,2,1,1,3,1,1,1,1]
    barrier_14 = [0,0,2,0,0,0,1,1,0,2,2,3,2,1,1,3,1,1,1,1]
    barrier_15 = [0,0,2,0,0,0,1,1,0,2,1,1,2,3,3,1,1,1,1,1]

    all_barriers = [
        barrier_1, barrier_2, barrier_3, barrier_4, barrier_5,
        barrier_6, barrier_7, barrier_8, barrier_9, barrier_10,
        barrier_11, barrier_12, barrier_13, barrier_14, barrier_15
    ]

    results = {}

    for i in range(15):   # 0–14
        score_sum = 0
        for j in range(20):   # 0–19 (20 cost factors)
            score_sum += cost_values[j] * all_barriers[i][j]

        results[f"barrier_{i+1}_cost_score"] = score_sum

    return results

def calc_kpi_scores(kpi: dict):
    kpi_values = list(kpi.values())
    barrier_1 = [1, 1, 1, 2, 2, 1, 2, 1, 2, 1, 1, 2, 3, 2, 2, 3, 2]
    barrier_2 = [1, 1, 1, 2, 2, 1, 2, 1, 2, 1, 1, 2, 3, 2, 2, 3, 2]
    barrier_3 = [1, 1, 1, 2, 2, 1, 2, 2, 2, 1, 1, 1, 3, 2, 2, 3, 2]
    barrier_4 = [1, 1, 1, 2, 2, 1, 2, 2, 2, 1, 1, 1, 3, 2, 2, 3, 2]
    barrier_5 = [1, 1, 1, 2, 2, 1, 2, 2, 2, 1, 1, 1, 3, 2, 2, 2, 2]
    barrier_6 = [1, 0, 1, 2, 2, 2, 1, 1, 2, 2, 1, 2, 1, 3, 3, 1, 2]
    barrier_7 = [1, 0, 1, 2, 2, 2, 1, 1, 2, 2, 1, 2, 1, 2, 2, 1, 2]
    barrier_8 = [1, 0, 1, 2, 2, 1, 2, 2, 2, 1, 1, 1, 2, 2, 2, 1, 1]
    barrier_9 = [2, 1, 2, 1, 1, 0, 1, 2, 2, 1, 2, 2, 2, 3, 3, 1, 1]
    barrier_10 = [3, 2, 3, 3, 3, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 3]
    barrier_11 = [2, 1, 2, 1, 1, 1, 2, 2, 2, 1, 3, 1, 2, 2, 2, 1, 2]
    barrier_12 = [1, 0, 1, 1, 1, 0, 1, 2, 1, 1, 2, 1, 1, 3, 3, 1, 1]
    barrier_13 = [1, 0, 1, 2, 2, 2, 1, 1, 2, 2, 1, 2, 1, 3, 3, 1, 2]
    barrier_14 = [1, 0, 1, 2, 2, 2, 1, 1, 2, 2, 1, 2, 1, 3, 3, 1, 2]
    barrier_15 = [1, 0, 1, 2, 2, 2, 1, 1, 2, 2, 1, 1, 1, 2, 2, 1, 3]
    
    all_barriers = [
        barrier_1, barrier_2, barrier_3, barrier_4, barrier_5,
        barrier_6, barrier_7, barrier_8, barrier_9, barrier_10,
        barrier_11, barrier_12, barrier_13, barrier_14, barrier_15
    ]

    results = {}

    for i in range(15):   # 0–14
        score_sum = 0
        for j in range(17):   # 0–19 (20 cost factors)
            score_sum += kpi_values[j] * all_barriers[i][j]

        results[f"barrier_{i+1}_kpi_score"] = score_sum

    return results

def calc_impact_value(kpi_score: dict, barrier_score: dict, cost_score: dict):
    """
    Normalization:
    KPI score     / 142
    Barrier score / 97.75
    Cost score    / 13.95

    Returns:
    {
        "barrier_1": impact_value,
        ...
        "barrier_15": impact_value
    }
    """

    impact_values = {}

    for i in range(1, 16):

        # --- Extract raw scores ---
        kpi_raw = kpi_score[f"barrier_{i}_kpi_score"]
        barrier_raw = barrier_score[f"barrier{i}"]["total"]
        cost_raw = cost_score[f"barrier_{i}_cost_score"]

        # --- Normalize ---
        kpi_norm = kpi_raw / 142
        barrier_norm = barrier_raw / 97.75
        cost_norm = cost_raw / 13.95

        # --- Impact calculation (simple additive model) ---
        impact = (0.4 * kpi_norm) + (0.3 * barrier_norm) + (0.3 * cost_norm)

        impact_values[f"barrier_{i}"] = impact

    return impact_values

def save_report_metadata_to_mongodb(barrier_id, pdf_path):
    db = get_db()

    db.generated_reports.insert_one({
        "barrier_id": barrier_id,
        "pdf_path": pdf_path,
        "generated_at": datetime.now()
    })

import zipfile

def zip_reports(pdf_dir, zip_name="Barrier_Reports.zip"):
    zip_path = os.path.join(pdf_dir, zip_name)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in os.listdir(pdf_dir):
            if file.endswith(".pdf"):
                zipf.write(
                    os.path.join(pdf_dir, file),
                    arcname=file
                )

    return zip_path

def save_impact_scores_to_mongodb(impact_scores: dict):
    db = get_db()
    db.impact_scores.insert_one(impact_scores)
    print("✔ Impact scores saved to MongoDB (impact_scores collection)")

# def generate_barrier_reports(
#     barrier_templates_path,
#     company_details,
#     barrier_scores,
#     kpi_scores,
#     cost_scores,
#     impact_values
# ):
#     from datetime import datetime
#     from weasyprint import HTML
#     from jinja2 import Environment, FileSystemLoader

#     output_dir = "generated_reports"
#     chart_dir = "charts"
#     os.makedirs(output_dir, exist_ok=True)

#     with open(barrier_templates_path) as f:
#         barrier_templates = json.load(f)

#     env = Environment(loader=FileSystemLoader("templates"))
#     template = env.get_template("barrier_report.html")

#     for barrier_key, barrier in barrier_templates.items():
#         bid = barrier["barrier_id"]

#         scores = {
#             "barrier_score": barrier_scores[f"barrier{bid}"]["total"],
#             "severity": barrier_scores[f"barrier{bid}"]["level"],
#             "kpi_score": kpi_scores[f"barrier_{bid}_kpi_score"],
#             "cost_score": cost_scores[f"barrier_{bid}_cost_score"],
#             "impact_value": impact_values[f"barrier_{bid}"]
#         }

#         # --------- LLM NARRATIVE ---------
#         prompt = build_barrier_prompt(barrier, scores, company_details)
#         narrative = call_llm(prompt)

#         # --------- CHART ---------
#         chart_path = generate_barrier_charts(bid, scores, chart_dir)

#         # --------- PDF CONTEXT ---------
#         context = {
#             "company": company_details,
#             "barrier": barrier,
#             "scores": scores,
#             "narrative": narrative,
#             "chart_path": chart_path,
#             "report_generated_on": datetime.now().strftime("%d %B %Y"),
#             "disclaimer": barrier.get("disclaimer", "")
#         }

#         html = template.render(context)

#         pdf_path = f"{output_dir}/Barrier_{bid}_Report.pdf"
#         HTML(string=html, base_url=".").write_pdf(pdf_path)

#         save_report_metadata_to_mongodb(bid, pdf_path)

#     zip_path = zip_reports(output_dir)
#     print(f"✔ Reports generated & zipped: {zip_path}")

#     return zip_path

def generate_barrier_reports_top_3(
    barrier_templates_path,
    company_details,
    barrier_scores,
    kpi_scores,
    cost_scores,
    impact_values
):
    from weasyprint import HTML
    from jinja2 import Environment, FileSystemLoader

    output_dir = "generated_reports"
    chart_dir = "charts"
    os.makedirs(output_dir, exist_ok=True)

    with open(barrier_templates_path) as f:
        barrier_templates = json.load(f)

    # 🔥 Generate LLM text ONLY for top 3
    top_3_narratives = generate_top_3_barrier_roadmaps(
        barrier_templates,
        barrier_scores,
        impact_values,
        company_details
    )

    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("barrier_report.html")

    for barrier in barrier_templates.values():
        bid = barrier["barrier_id"]

        scores = {
            "barrier_score": barrier_scores[f"barrier{bid}"]["total"],
            "severity": barrier_scores[f"barrier{bid}"]["level"],
            "kpi_score": kpi_scores[f"barrier_{bid}_kpi_score"],
            "cost_score": cost_scores[f"barrier_{bid}_cost_score"],
            "impact_value": impact_values[f"barrier_{bid}"]
        }

        chart_path = generate_barrier_charts(bid, scores, chart_dir)

        narrative = top_3_narratives.get(f"barrier_{bid}", "")

        context = {
            "company": company_details,
            "barrier": barrier,
            "scores": scores,
            "narrative": narrative,
            "chart_path": chart_path,
            "report_generated_on": datetime.now().strftime("%d %B %Y"),
            "disclaimer": barrier.get("disclaimer", "")
        }

        html = template.render(context)
        pdf_path = f"{output_dir}/Barrier_{bid}_Report.pdf"
        HTML(string=html, base_url=".").write_pdf(pdf_path)

        save_report_metadata_to_mongodb(bid, pdf_path)

    zip_path = zip_reports(output_dir)
    print(f"✔ Reports generated & zipped: {zip_path}")

    return zip_path


def build_barrier_prompt(barrier_template, scores, company):
    return f"""
You are generating a professional industrial readiness report.

STRICT RULES:
- Do NOT change drivers, phases, timelines, or actions
- ONLY contextualize language using company details and scores
- Maintain formal consulting tone
- Do NOT invent new recommendations

Company Context:
Company Name: {company.get("company_name")}
Industry: {company.get("industry")}

Barrier:
Barrier ID: {barrier_template["barrier_id"]}
Barrier Name: {barrier_template["barrier_name"]}

Scores:
Barrier Score: {scores["barrier_score"]:.2f} / 10
Severity Level: {scores["severity"]}
Impact Value: {scores["impact_value"]:.3f}

Task:
Write a concise Executive Summary (120–150 words) explaining:
- What this barrier means for the company
- Why the severity level matters
- Business risk if not addressed

Do NOT repeat drivers or action plans.
"""
def get_top_3_barriers_by_impact(impact_values: dict):
    """
    impact_values may contain MongoDB metadata like _id.
    This function safely extracts only barrier_* keys.
    """

    clean_impacts = {
        k: v for k, v in impact_values.items()
        if k.startswith("barrier_") and isinstance(v, (int, float))
    }

    return sorted(
        clean_impacts.keys(),
        key=lambda k: clean_impacts[k],
        reverse=True
    )[:3]


def prepare_barrier_context(
    barrier_key: str,
    barrier_templates: dict,
    barrier_scores: dict,
    impact_values: dict
):
    barrier_id = int(barrier_key.split("_")[1])

    barrier_template = next(
        b for b in barrier_templates.values()
        if b["barrier_id"] == barrier_id
    )

    scores = {
        "barrier_score": barrier_scores[f"barrier{barrier_id}"]["total"],
        "severity": barrier_scores[f"barrier{barrier_id}"]["level"],
        "impact_value": impact_values[f"barrier_{barrier_id}"]
    }

    return barrier_template, scores

from typing import Dict, List

def generate_top_3_barrier_roadmaps(
    barrier_templates: dict,
    barrier_scores: dict,
    impact_values: dict,
    company_details: dict
):
    """
    LLM-generated Executive Summaries ONLY for top 3 barriers
    """

    top_3 = get_top_3_barriers_by_impact(impact_values)
    narratives = {}

    for barrier_key in top_3:
        barrier_id = int(barrier_key.split("_")[1])

        barrier_template = next(
            b for b in barrier_templates.values()
            if b["barrier_id"] == barrier_id
        )

        scores = {
            "barrier_score": barrier_scores[f"barrier{barrier_id}"]["total"],
            "severity": barrier_scores[f"barrier{barrier_id}"]["level"],
            "impact_value": impact_values[barrier_key]
        }

        prompt = build_barrier_prompt(barrier_template, scores, company_details)
        narratives[barrier_key] = call_llm(prompt)

    return narratives


# def build_barrier_prompt(barrier_template, scores, company):
#     return f"""
# You are an enterprise IoT consulting report generator.

# STRICT RULES (MANDATORY):
# - Do NOT change drivers, headings, phases, or timelines.
# - Do NOT invent metrics, causes, or solutions.
# - ONLY adapt language using the given scores and company context.
# - Maintain professional consulting tone.

# Company Details:
# {company}

# Barrier Name:
# {barrier_template["barrier_name"]}

# Barrier Description:
# {barrier_template["description"]}

# Drivers (DO NOT CHANGE):
# {barrier_template["drivers"]}

# Phases & Timelines (DO NOT CHANGE):
# {barrier_template.get("phases", "N/A")}

# Calculated Scores:
# - Barrier Score: {scores["barrier_score"]}
# - Severity Level: {scores["severity"]}
# - KPI Impact Score: {scores["kpi_score"]}
# - Cost Impact Score: {scores["cost_score"]}
# - Overall Impact Value: {scores["impact_value"]}

# Write the following sections EXACTLY in this order:
# 1. Executive Summary
# 2. Impact Analysis
# 3. Risk Interpretation
# 4. Recommendations

# Use concise, factual, consulting-style language.
# """

# -------------------------------
# SAVE BARRIER SCORES TO CSV
# -------------------------------
def save_barrier_scores_to_mongodb(barrier_scores: dict):
    db = get_db()

    db.barrier_scores.insert_one(barrier_scores)

    print("✔ Barrier scores saved to MongoDB (barrier_scores collection)")


# -------------------------------
# SAVE COST FACTOR SCORES TO CSV
# -------------------------------
def save_cost_scores_to_mongodb(cost_scores: dict):
    db = get_db()

    db.cost_factor_scores.insert_one(cost_scores)

    print("✔ Cost factor scores saved to MongoDB (cost_factor_scores collection)")
    

def save_kpi_scores_to_mongodb(kpi_scores: dict):
    db = get_db()

    db.kpi_scores.insert_one(kpi_scores)

    print("✔ KPI scores saved to MongoDB (kpi_scores collection)")

# -------------------------------
# MAIN EXECUTION
# -------------------------------
if __name__ == "__main__":

    with open("data.json") as f:
        data = json.load(f)

    company = extract_company_details(data)
    barriers = extract_barrier_scores(data)
    kpis = extract_kpi_factors(data)
    costs = extract_cost_factors(data)

    # Save raw inputs
    save_raw_to_mongodb(company, barriers, kpis, costs)

    # Barrier scores
    computed_scores = calc_barrier_scores(barriers)
    save_barrier_scores_to_mongodb(computed_scores)

    # Cost scores
    cost_scores = calc_cost_factor_scores(costs)
    save_cost_scores_to_mongodb(cost_scores)

    # KPI scores
    kpi_scores = calc_kpi_scores(kpis)
    save_kpi_scores_to_mongodb(kpi_scores)

    # Impact scores
    impact_scores = calc_impact_value(
        kpi_score=kpi_scores,
        barrier_score=computed_scores,
        cost_score=cost_scores
    )
    save_impact_scores_to_mongodb(impact_scores)

    # Generate PDFs + ZIP
    zip_path = generate_barrier_reports_top_3(
        barrier_templates_path="barrier_reports.json",
        company_details=company,
        barrier_scores=computed_scores,
        kpi_scores=kpi_scores,
        cost_scores=cost_scores,
        impact_values=impact_scores
    )

    print("📦 All barrier reports generated:", zip_path)