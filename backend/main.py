from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field
from typing import List, Dict, Union, Literal
import pandas as pd
import io
import httpx # For making asynchronous HTTP requests to Mistral API
import numpy as np
import os
import pdfplumber

# --- Mistral API Configuration ---
MISTRAL_MODEL: str = "mistral-large-latest" # Using Mistral API model
MISTRAL_API_KEY: str = "xT8aMNyrN28eXoWKEaSYHFn4RFMN6K0u" # Your Mistral API key
MISTRAL_API_URL: str = "https://api.mistral.ai/v1/chat/completions"

# --- Global Storage for Results ---
# NOTE: This global state is maintained as per the original design.
calculated_data = {
    "barrier_scores": None,
    "cost_factors": None,
    "kpi_factors": None,
    "barrier_input_details": None,
    "isri_data": None,
    "company_details": None
}

# --- Pydantic Models for Input Data (UNCHANGED) ---

class CompanyDetailsInput(BaseModel):
    company_name: str = Field(..., description="Name of the company")
    industry: str = Field(..., description="Industry of the company (e.g., Manufacturing, Automotive)")
    num_employees: int = Field(..., description="Number of employees")
    annual_revenue: float = Field(..., description="Annual revenue in a suitable currency (e.g., in crores)")
    
class Barrier1Input(BaseModel):
    num_training_programs: float = Field(..., description="Number of training programs offered per year (Avg-5, put 5 only if there is more than 5)")
    pct_employees_trained: float = Field(..., description="Percentage of employees trained in digital technologies (e.g., 30 for 30%)")
    pct_budget_training_of_payroll: float = Field(..., description="Budget allocated for employee training as percentage of total payroll (e.g., 2 for 2%)")

class Barrier2Input(BaseModel):
    employee_turnover_rate_pct: float = Field(..., description="Employee turnover rate following the introduction of IoT initiatives (e.g., 15 for 15%)")
    pct_employees_resisting: float = Field(..., description="Percentage of employees who express resistance in surveys (e.g., 20 for 20%)")
    num_feedback_sessions: int = Field(..., description="Number of feedback sessions held to address concerns")

class Barrier3Input(BaseModel):
    num_digital_skills_workshops: int = Field(..., description="Number of digital skills workshops attended by employees")
    pct_comfortable_digital_tools: float = Field(..., description="Percentage of employees who are comfortable using digital tools (e.g., 30 for 30%)")
    adoption_rate_new_digital_tools_pct: float = Field(..., description="Adoption rate of new digital tools (e.g., 25 for 25%)")

class Barrier4Input(BaseModel):
    pct_training_expenditure_of_op_costs: float = Field(..., description="Training expenditure as percentage of total operational costs (e.g., 1.25 for 1.25%)")
    avg_training_hours_per_employee: float = Field(..., description="Average training hours per employee per year")
    roi_training_programs_pct: float = Field(..., description="ROI on training programs (e.g., 5 for 5%)")

class Barrier5Input(BaseModel):
    num_knowledge_sharing_sessions: int = Field(..., description="Number of knowledge-sharing sessions conducted internally")
    pct_employees_access_kms: float = Field(..., description="Percentage of employees with access to a centralized knowledge system (e.g., 20 for 20%)")
    freq_updates_kms: Literal["Daily", "Weekly", "Monthly", "Quarterly", "Bi-Annually", "Annually"] = Field(..., description="Frequency of updates to the knowledge management system")

class Barrier6Input(BaseModel):
    num_non_compliance_incidents: int = Field(..., description="Number of non-compliance incidents or penalties")
    pct_projects_delayed_regulatory: float = Field(..., description="Percentage of IoT projects delayed due to regulatory challenges (e.g., 40 for 40%)")
    time_to_achieve_compliance_days: int = Field(..., description="Time taken to achieve compliance with new regulations (in days)")

class Barrier7Input(BaseModel):
    num_industry_standards_adopted: int = Field(..., description="Number of industry standards adopted by the organization")
    pct_iot_devices_conforming: float = Field(..., description="Percentage of IoT devices conforming to a reference architecture (e.g., 50 for 50%)")
    pct_projects_delayed_standardized_solutions: float = Field(..., description="Percentage of IoT projects delayed due to lack of standardized solutions (e.g., 50 for 50%)")

class Barrier8Input(BaseModel):
    pct_internet_coverage: float = Field(..., description="Percentage coverage across all necessary operational areas (e.g., 70 for 70%)")
    avg_internet_speed_mbps: float = Field(..., description="Average internet speed across different locations (in Mbps)")
    freq_it_infrastructure_outages_per_month: int = Field(..., description="Frequency of IT infrastructure outages per month")

class Barrier9Input(BaseModel):
    pct_loan_approved: float = Field(..., description="Percentage of loan applications approved (e.g., 80 for 80%)")
    pct_projects_delayed_lack_funding: float = Field(..., description="Percentage of projects delayed or canceled due to lack of funding (e.g., 30 for 30%)")
    ratio_external_funding_total_project_costs_pct: float = Field(..., description="Ratio of external funding to total project costs (e.g., 15 for 15%)")

class Barrier10Input(BaseModel):
    yoy_revenue_growth_iot_pct: float = Field(..., description="Year-over-year (YoY) growth in revenue attributed to IoT (e.g., 2 for 2%)")
    profit_margin_improvement_iot_pct: float = Field(..., description="Profit margin improvement following IoT implementation (e.g., 0.5 for 0.5%)")
    num_new_revenue_streams_iot: int = Field(..., description="Number of new revenue streams generated through IoT")

class Barrier11Input(BaseModel):
    pct_critical_operations_reliant_vendor: float = Field(..., description="Percentage of critical operations reliant on third-party vendors (e.g., 75 for 75%)")
    num_vendor_delays_disruptions_per_year: int = Field(..., description="Number of vendor-related delays or disruptions per year")
    cost_vendor_contracts_pct_op_expenses: float = Field(..., description="Cost of vendor contracts as a percentage of total operating expenses (e.g., 5 for 5%)")

class Barrier12Input(BaseModel):
    pct_it_budget_allocated_iot: float = Field(..., description="Percentage of the total IT budget allocated to IoT implementation (e.g., 50 for 50%)")
    annual_maintenance_costs_pct_op_costs: float = Field(..., description="Annual maintenance costs as a percentage of total operational costs (e.g., 3 for 3%)")
    integration_costs_pct_total_project_cost: float = Field(..., description="Integration costs as a percentage of total project cost (e.g., 40 for 40%)")

class Barrier13Input(BaseModel):
    num_regulatory_violations_penalties: int = Field(..., description="Number of regulatory violations or penalties incurred")
    pct_compliance_audits_passed_without_issues: float = Field(..., description="Percentage of compliance audits passed without issues (e.g., 60 for 60%)")
    freq_updates_internal_policies: Literal["Monthly", "Quarterly", "Bi-Annually", "Annually"] = Field(..., description="Frequency of updates to internal policies in response to regulatory changes")

class Barrier14Input(BaseModel):
    pct_standards_compliant_iot_devices: float = Field(..., description="Percentage of standards-compliant IoT devices used (e.g., 30 for 30%)")
    num_industry_specific_guidelines_implemented: int = Field(..., description="Number of industry-specific guidelines implemented")

class Barrier15Input(BaseModel):
    pct_customers_refuse_data: float = Field(..., description="Percentage of customers who refuse to share data (e.g., 40 for 40%)")
    num_customer_complaints_data_sharing: int = Field(..., description="Number of customer complaints or concerns regarding data sharing")
    pct_customer_contracts_explicit_data_sharing: float = Field(..., description="Percentage of customer contracts with explicit data-sharing agreements (e.g., 50 for 50%)")

class CostFactorInput(BaseModel):
    aftermarket_services_warranty: float = Field(..., description="Aftermarket Services / Warranty (% of Annual Revenue)")
    depreciation: float = Field(..., description="Depreciation (% of Annual Revenue)")
    labour: float = Field(..., description="Labour (% of Annual Revenue)")
    maintenance_repair: float = Field(..., description="Maintenance & Repair (% of Annual Revenue)")
    raw_materials_consumables: float = Field(..., description="Raw Materials & Consumables (% of Annual Revenue)")
    rental_operating_lease: float = Field(..., description="Rental & Operating Lease (% of Annual Revenue)")
    research_development: float = Field(..., description="Research & Development (R&D) (% of Annual Revenue)")
    selling_general_administrative_expense: float = Field(..., description="Selling, General & Administrative Expense (% of Annual Revenue)")
    utilities: float = Field(..., description="Utilities (% of Annual Revenue)")
    earnings_before_interest_taxes_ebit: float = Field(..., description="Earnings Before Interest & Taxes (EBIT) (% of Annual Revenue)")
    financing_costs_interest: float = Field(..., description="Financing Costs (Interest) (% of Annual Revenue)")
    taxation_compliance_costs: float = Field(..., description="Taxation and Compliance Costs (% of Annual Revenue)")
    supply_chain_logistics_costs: float = Field(..., description="Supply Chain and Logistics Costs (% of Annual Revenue)")
    technology_digital_infrastructure_costs: float = Field(..., description="Technology and Digital Infrastructure Costs (% of Annual Revenue)")
    training_skill_development_costs: float = Field(..., description="Training and Skill Development Costs (% of Annual Revenue)")
    regulatory_compliance_costs: float = Field(..., description="Regulatory and Compliance Costs (% of Annual Revenue)")
    insurance_costs: float = Field(..., description="Insurance Costs (% of Annual Revenue)")
    marketing_customer_acquisition_costs: float = Field(..., description="Marketing and Customer Acquisition Costs (% of Annual Revenue)")
    environmental_social_responsibility_costs: float = Field(..., description="Environmental and Social Responsibility Costs (% of Annual Revenue)")
    quality_control_assurance: float = Field(..., description="Quality Control and Assurance (% of Annual Revenue)")

class KPIFactorInput(BaseModel):
    asset_equipment_efficiency: float = Field(..., description="Asset & Equipment Efficiency (0 or 1)")
    utilities_efficiency: float = Field(..., description="Utilities Efficiency (0 or 1)")
    inventory_efficiency: float = Field(..., description="Inventory Efficiency (0 or 1)")
    process_quality: float = Field(..., description="Process Quality (0 or 1)")
    product_quality: float = Field(..., description="Product Quality (0 or 1)")
    safety_security: float = Field(..., description="Safety & Security (0 or 1)")
    planning_scheduling_effectiveness: float = Field(..., description="Planning & Scheduling Effectiveness (0 or 1)")
    time_to_market: float = Field(..., description="Time to Market (0 or 1)")
    production_flexibility: float = Field(..., description="Production Flexibility (0 or 1)")
    customer_satisfaction: float = Field(..., description="Customer Satisfaction (0 or 1)")
    supply_chain_efficiency: float = Field(..., description="Supply Chain Efficiency (0 or 1)")
    market_share_growth: float = Field(..., description="Market Share Growth (0 or 1)")
    employee_productivity: float = Field(..., description="Employee Productivity (0 or 1)")
    return_on_investment_roi: float = Field(..., description="Return on Investment (ROI) (0 or 1)")
    financial_health_and_stability: float = Field(..., description="Financial Health and Stability (0 or 1)")
    talent_retention: float = Field(..., description="Talent Retention (0 or 1)")
    customer_retention_rate: float = Field(..., description="Customer Retention Rate (0 or 1)")

# --- NEW: Single Pydantic Model for the Single Endpoint ---
class ComprehensiveInput(BaseModel):
    company_details: CompanyDetailsInput
    barrier1: Barrier1Input
    barrier2: Barrier2Input
    barrier3: Barrier3Input
    barrier4: Barrier4Input
    barrier5: Barrier5Input
    barrier6: Barrier6Input
    barrier7: Barrier7Input
    barrier8: Barrier8Input
    barrier9: Barrier9Input
    barrier10: Barrier10Input
    barrier11: Barrier11Input
    barrier12: Barrier12Input
    barrier13: Barrier13Input
    barrier14: Barrier14Input
    barrier15: Barrier15Input
    cost_factor_inputs: CostFactorInput
    kpi_factor_inputs: KPIFactorInput

# --- Constants and Mappings (UNCHANGED) ---

BARRIER_DEFINITIONS = {
    "Lack of training for workers and managers": { "sr_no": 1, "indicators": [{"name": "i. Number of training programs offered per year.", "weight": 0.2, "target": 5, "type": "inverted_ratio"}, {"name": "ii Percentage of employees trained in digital technologies.", "weight": 0.5, "type": "inverted_percentage"}, {"name": "iii.Budget allocation for employee training", "weight": 0.3, "type": "special_payroll_calc"}], "doc_input_map": {"i. Number of training programs offered per year.": "num_training_programs", "ii Percentage of employees trained in digital technologies.": "pct_employees_trained", "iii.Budget allocation for employee training": "pct_budget_training_of_payroll"}},
    "Resistance to change": { "sr_no": 2, "indicators": [{"name": "i.Employee turnover rate following the introduction of IoT initiatives.", "weight": 0.4, "crisis_level": 20, "type": "ratio"}, {"name": "ii.Percentage of employees who express resistance to adopting new technologies in surveys.", "weight": 0.35, "type": "percentage"}, {"name": "iii.Number of feedback sessions held to address concerns.", "weight": 0.25, "target": 12, "type": "inverted_ratio"}], "doc_input_map": {"i.Employee turnover rate following the introduction of IoT initiatives.": "employee_turnover_rate_pct", "ii.Percentage of employees who express resistance to adopting new technologies in surveys.": "pct_employees_resisting", "iii.Number of feedback sessions held to address concerns.": "num_feedback_sessions"}},
    "Lack of digital culture and training": { "sr_no": 3, "indicators": [{"name": "i. Number of digital skills workshops attended by employees.", "weight": 0.2, "target": 5, "type": "inverted_ratio"}, {"name": "ii.Percentage of employees who are comfortable using digital tools.", "weight": 0.4, "type": "inverted_percentage"}, {"name": "iii.Adoption rate of new digital tools.", "weight": 0.4, "type": "inverted_percentage"}], "doc_input_map": {"i. Number of digital skills workshops attended by employees.": "num_digital_skills_workshops", "ii.Percentage of employees who are comfortable using digital tools.": "pct_comfortable_digital_tools", "iii.Adoption rate of new digital tools.": "adoption_rate_new_digital_tools_pct"}},
    "Higher investment in employees' training.": { "sr_no": 4, "indicators": [{"name": "i.Training expenditure as a percentage of total operational costs.", "weight": 0.4, "benchmark": 5, "type": "special_op_cost_calc"}, {"name": "ii.Average training hours per employee per year.", "weight": 0.3, "benchmark": 40, "type": "ratio"}, {"name": "iii.ROI on training programs.", "weight": 0.3, "type": "inverted_percentage"}], "doc_input_map": {"i.Training expenditure as a percentage of total operational costs.": "pct_training_expenditure_of_op_costs", "ii.Average training hours per employee per year.": "avg_training_hours_per_employee", "iii.ROI on training programs.": "roi_training_programs_pct"}},
    "Lack of knowledge management systems": { "sr_no": 5, "indicators": [{"name": "i.Number of knowledge-sharing sessions conducted internally.", "weight": 0.3, "target": 24, "type": "inverted_ratio"}, {"name": "ii.Percentage of employees with access to a centralized knowledge system.", "weight": 0.4, "type": "inverted_percentage"}, {"name": "iii.Frequency of updates to the knowledge management system.", "weight": 0.3, "type": "frequency_map"}], "doc_input_map": {"i.Number of knowledge-sharing sessions conducted internally.": "num_knowledge_sharing_sessions", "ii.Percentage of employees with access to a centralized knowledge system.": "pct_employees_access_kms", "iii.Frequency of updates to the knowledge management system.": "freq_updates_kms"}, "frequency_map": {"Daily": 0, "Weekly": 0.25, "Monthly": 0.5, "Quarterly": 0.75, "Bi-Annually": 0.875, "Annually": 1.0}},
    "Regulatory compliance issues": { "sr_no": 6, "indicators": [{"name": "i.Number of non-compliance incidents or penalties.", "weight": 0.4, "crisis_level": 5, "type": "ratio"}, {"name": "ii.Percentage of IoT projects delayed due to regulatory challenges.", "weight": 0.4, "type": "percentage"}, {"name": "iii.Time taken to achieve compliance with new regulations.", "weight": 0.2, "crisis_level": 180, "type": "ratio"}], "doc_input_map": {"i.Number of non-compliance incidents or penalties.": "num_non_compliance_incidents", "ii.Percentage of IoT projects delayed due to regulatory challenges.": "pct_projects_delayed_regulatory", "iii.Time taken to achieve compliance with new regulations.": "time_to_achieve_compliance_days"}},
    "Lack of Standards and Reference Architecture": { "sr_no": 7, "indicators": [{"name": "i.Number of industry standards adopted by the organization.", "weight": 0.35, "target": 10, "type": "inverted_ratio"}, {"name": "ii.Number of IoT devices conforming to a reference architecture.", "weight": 0.4, "type": "custom_div_50"}, {"name": "iii.Percentage of IoT projects delayed due to lack of standardized solutions.", "weight": 0.25, "type": "percentage"}], "doc_input_map": {"i.Number of industry standards adopted by the organization.": "num_industry_standards_adopted", "ii.Number of IoT devices conforming to a reference architecture.": "pct_iot_devices_conforming", "iii.Percentage of IoT projects delayed due to lack of standardized solutions.": "pct_projects_delayed_standardized_solutions"}},
    "Lack of Internet coverage and IT facilities": { "sr_no": 8, "indicators": [{"name": "i.Lack of Internet coverage and IT facilities", "weight": 0.3, "type": "inverted_percentage"}, {"name": "ii.Average internet speed across different locations", "weight": 0.2, "target": 50, "type": "inverted_ratio"}, {"name": "iii.Frequency of IT infrastructure outages", "weight": 0.5, "crisis_level": 8, "type": "ratio"}], "doc_input_map": {"i.Lack of Internet coverage and IT facilities": "pct_internet_coverage", "ii.Average internet speed across different locations": "avg_internet_speed_mbps", "iii.Frequency of IT infrastructure outages": "freq_it_infrastructure_outages_per_month"}},
    "Limited Access to Funding and Credit": { "sr_no": 9, "indicators": [{"name": "i.Number of loan applications submitted and approved.", "weight": 0.4, "type": "custom_div_5"}, {"name": "ii.Percentage of projects delayed or canceled due to lack of funding.", "weight": 0.4, "type": "percentage"}, {"name": "iii.Ratio of external funding to total project costs.", "weight": 0.2, "type": "inverted_percentage"}], "doc_input_map": {"i.Number of loan applications submitted and approved.": "pct_loan_approved", "ii.Percentage of projects delayed or canceled due to lack of funding.": "pct_projects_delayed_lack_funding", "iii.Ratio of external funding to total project costs.": "ratio_external_funding_total_project_costs_pct"}},
    "Future viability & profitability": { "sr_no": 10, "indicators": [{"name": "i.Year-over-year (YoY) growth in revenue attributed to IoT.", "weight": 0.4, "target": 20, "type": "inverted_ratio"}, {"name": "ii.Profit margin improvement following IoT implementation.", "weight": 0.4, "target": 5, "type": "inverted_ratio"}, {"name": "iii.Number of new revenue streams generated through IoT.", "weight": 0.2, "target": 3, "type": "inverted_ratio"}], "doc_input_map": {"i.Year-over-year (YoY) growth in revenue attributed to IoT.": "yoy_revenue_growth_iot_pct", "ii.Profit margin improvement following IoT implementation.": "profit_margin_improvement_iot_pct", "iii.Number of new revenue streams generated through IoT.": "num_new_revenue_streams_iot"}},
    "Dependency on External Vendors": { "sr_no": 11, "indicators": [{"name": "i.Percentage of critical operations reliant on third-party vendors.", "weight": 0.4, "type": "percentage"}, {"name": "ii.Number of vendor-related delays or disruptions per year.", "weight": 0.4, "type": "custom_inv_div_5"}, {"name": "iii.Cost of vendor contracts as a percentage of total operating expenses.", "weight": 0.2, "type": "custom_div_100"}], "doc_input_map": {"i.Percentage of critical operations reliant on third-party vendors.": "pct_critical_operations_reliant_vendor", "ii.Number of vendor-related delays or disruptions per year.": "num_vendor_delays_disruptions_per_year", "iii.Cost of vendor contracts as a percentage of total operating expenses.": "cost_vendor_contracts_pct_op_expenses"}},
    "High Implementation Cost": { "sr_no": 12, "indicators": [{"name": "i.Percentage of the total IT budget allocated to IoT implementation.", "weight": 0.4, "type": "percentage"}, {"name": "ii.Annual maintenance costs as a percentage of total operational costs.", "weight": 0.3, "crisis_level": 5, "type": "ratio"}, {"name": "iii.Integration costs as a percentage of total project cost.", "weight": 0.3, "type": "percentage"}], "doc_input_map": {"i.Percentage of the total IT budget allocated to IoT implementation.": "pct_it_budget_allocated_iot", "ii.Annual maintenance costs as a percentage of total operational costs.": "annual_maintenance_costs_pct_op_costs", "iii.Integration costs as a percentage of total project cost.": "integration_costs_pct_total_project_cost"}},
    "Compliance with Sector-Specific Regulations": { "sr_no": 13, "indicators": [{"name": "i.Number of regulatory violations or penalties incurred.", "weight": 0.5, "crisis_level": 4, "type": "ratio"}, {"name": "ii: Percentage of compliance audits passed without issues.", "weight": 0.3, "type": "inverted_percentage"}, {"name": "iii: Frequency of updates to internal policies and procedures in response to regulatory changes.", "weight": 0.2, "type": "frequency_map"}], "doc_input_map": {"i.Number of regulatory violations or penalties incurred.": "num_regulatory_violations_penalties", "ii: Percentage of compliance audits passed without issues.": "pct_compliance_audits_passed_without_issues", "iii: Frequency of updates to internal policies and procedures in response to regulatory changes.": "freq_updates_internal_policies"}, "frequency_map": {"Monthly": 0.25, "Quarterly": 0.5, "Bi-Annually": 0.75, "Annually": 1.0}},
    "Lack of Regulations and Standards": { "sr_no": 14, "indicators": [{"name": "ii.Number of standards-compliant IoT devices used within the organization.", "weight": 0.4, "type": "inverted_percentage"}, {"name": "iii.Number of industry-specific guidelines or frameworks that have been implemented.", "weight": 0.6, "target": 10, "type": "inverted_ratio"}], "doc_input_map": {"ii.Number of standards-compliant IoT devices used within the organization.": "pct_standards_compliant_iot_devices", "iii.Number of industry-specific guidelines or frameworks that have been implemented.": "num_industry_specific_guidelines_implemented"}},
    "Customers are hesitant to share data": { "sr_no": 15, "indicators": [{"name": "i.Percentage of customers who refuse to share data (survey-based).", "weight": 0.4, "type": "percentage"}, {"name": "ii.Number of customer complaints or concerns regarding data sharing.", "weight": 0.35, "crisis_level": 25, "type": "ratio"}, {"name": "iii.Number of customer contracts with explicit data-sharing agreements.", "weight": 0.25, "type": "inverted_percentage"}], "doc_input_map": {"i.Percentage of customers who refuse to share data (survey-based).": "pct_customers_refuse_data", "ii.Number of customer complaints or concerns regarding data sharing.": "num_customer_complaints_data_sharing", "iii.Number of customer contracts with explicit data-sharing agreements.": "pct_customer_contracts_explicit_data_sharing"}}
}

COST_FACTOR_MAPPING_BARRIERS = {
    "Aftermarket Services / Warranty": {"input_key": "aftermarket_services_warranty", "Lack of training for workers and managers": 0, "Resistance to change": 0, "Lack of digital culture and training": 0, "Higher investment in employees' training.": 0, "Lack of knowledge management systems": 0, "Regulatory compliance issues": 0, "Lack of Standards and Reference Architecture": 0, "Lack of Internet coverage and IT facilities": 0, "Limited Access to Funding and Credit": 0, "Future viability & profitability": 2, "Dependency on External Vendors": 0, "High Implementation Cost": 0, "Compliance with Sector-Specific Regulations": 0, "Lack of Regulations and Standards": 0, "Customers are hesitant to share data": 0}, "Depreciation": {"input_key": "depreciation", "Lack of training for workers and managers": 0, "Resistance to change": 0, "Lack of digital culture and training": 0, "Higher investment in employees' training.": 0, "Lack of knowledge management systems": 0, "Regulatory compliance issues": 0, "Lack of Standards and Reference Architecture": 0, "Lack of Internet coverage and IT facilities": 0, "Limited Access to Funding and Credit": 0, "Future viability & profitability": 1, "Dependency on External Vendors": 0, "High Implementation Cost": 0, "Compliance with Sector-Specific Regulations": 0, "Lack of Regulations and Standards": 0, "Customers are hesitant to share data": 0}, "Labour": {"input_key": "labour", "Lack of training for workers and managers": 2, "Resistance to change": 2, "Lack of digital culture and training": 2, "Higher investment in employees' training.": 2, "Lack of knowledge management systems": 2, "Regulatory compliance issues": 2, "Lack of Standards and Reference Architecture": 2, "Lack of Internet coverage and IT facilities": 2, "Limited Access to Funding and Credit": 2, "Future viability & profitability": 3, "Dependency on External Vendors": 2, "High Implementation Cost": 2, "Compliance with Sector-Specific Regulations": 2, "Lack of Regulations and Standards": 2, "Customers are hesitant to share data": 2}, "Maintenance & Repair": {"input_key": "maintenance_repair", "Lack of training for workers and managers": 0, "Resistance to change": 0, "Lack of digital culture and training": 0, "Higher investment in employees' training.": 0, "Lack of knowledge management systems": 0, "Regulatory compliance issues": 0, "Lack of Standards and Reference Architecture": 0, "Lack of Internet coverage and IT facilities": 0, "Limited Access to Funding and Credit": 0, "Future viability & profitability": 2, "Dependency on External Vendors": 0, "High Implementation Cost": 0, "Compliance with Sector-Specific Regulations": 0, "Lack of Regulations and Standards": 0, "Customers are hesitant to share data": 0}, "Raw Materials & Consumables": {"input_key": "raw_materials_consumables", "Lack of training for workers and managers": 0, "Resistance to change": 0, "Lack of digital culture and training": 0, "Higher investment in employees' training.": 0, "Lack of knowledge management systems": 0, "Regulatory compliance issues": 0, "Lack of Standards and Reference Architecture": 0, "Lack of Internet coverage and IT facilities": 0, "Limited Access to Funding and Credit": 0, "Future viability & profitability": 2, "Dependency on External Vendors": 0, "High Implementation Cost": 0, "Compliance with Sector-Specific Regulations": 0, "Lack of Regulations and Standards": 0, "Customers are hesitant to share data": 0}, "Rental & Operating Lease": {"input_key": "rental_operating_lease", "Lack of training for workers and managers": 0, "Resistance to change": 0, "Lack of digital culture and training": 0, "Higher investment in employees' training.": 0, "Lack of knowledge management systems": 0, "Regulatory compliance issues": 0, "Lack of Standards and Reference Architecture": 0, "Lack of Internet coverage and IT facilities": 0, "Limited Access to Funding and Credit": 0, "Future viability & profitability": 1, "Dependency on External Vendors": 0, "High Implementation Cost": 0, "Compliance with Sector-Specific Regulations": 0, "Lack of Regulations and Standards": 0, "Customers are hesitant to share data": 0}, "Research & Development (R&D)": {"input_key": "research_development", "Lack of training for workers and managers": 2, "Resistance to change": 1, "Lack of digital culture and training": 1, "Higher investment in employees' training.": 2, "Lack of knowledge management systems": 2, "Regulatory compliance issues": 1, "Lack of Standards and Reference Architecture": 1, "Lack of Internet coverage and IT facilities": 1, "Limited Access to Funding and Credit": 1, "Future viability & profitability": 3, "Dependency on External Vendors": 1, "High Implementation Cost": 2, "Compliance with Sector-Specific Regulations": 1, "Lack of Regulations and Standards": 1, "Customers are hesitant to share data": 1}, "Selling, General & Administrative Expense": {"input_key": "selling_general_administrative_expense", "Lack of training for workers and managers": 1, "Resistance to change": 1, "Lack of digital culture and training": 1, "Higher investment in employees' training.": 1, "Lack of knowledge management systems": 1, "Regulatory compliance issues": 1, "Lack of Standards and Reference Architecture": 1, "Lack of Internet coverage and IT facilities": 1, "Limited Access to Funding and Credit": 2, "Future viability & profitability": 3, "Dependency on External Vendors": 1, "High Implementation Cost": 1, "Compliance with Sector-Specific Regulations": 1, "Lack of Regulations and Standards": 1, "Customers are hesitant to share data": 1}, "Utilities": {"input_key": "utilities", "Lack of training for workers and managers": 0, "Resistance to change": 0, "Lack of digital culture and training": 0, "Higher investment in employees' training.": 0, "Lack of knowledge management systems": 0, "Regulatory compliance issues": 0, "Lack of Standards and Reference Architecture": 0, "Lack of Internet coverage and IT facilities": 0, "Limited Access to Funding and Credit": 0, "Future viability & profitability": 2, "Dependency on External Vendors": 0, "High Implementation Cost": 0, "Compliance with Sector-Specific Regulations": 0, "Lack of Regulations and Standards": 0, "Customers are hesitant to share data": 0}, "Earnings Before Interest & Taxes (EBIT)": {"input_key": "earnings_before_interest_taxes_ebit", "Lack of training for workers and managers": 2, "Resistance to change": 1, "Lack of digital culture and training": 1, "Higher investment in employees' training.": 1, "Lack of knowledge management systems": 2, "Regulatory compliance issues": 1, "Lack of Standards and Reference Architecture": 1, "Lack of Internet coverage and IT facilities": 1, "Limited Access to Funding and Credit": 3, "Future viability & profitability": 3, "Dependency on External Vendors": 2, "High Implementation Cost": 3, "Compliance with Sector-Specific Regulations": 2, "Lack of Regulations and Standards": 2, "Customers are hesitant to share data": 2}, "Financing Costs (Interest)": {"input_key": "financing_costs_interest", "Lack of training for workers and managers": 1, "Resistance to change": 1, "Lack of digital culture and training": 1, "Higher investment in employees' training.": 1, "Lack of knowledge management systems": 1, "Regulatory compliance issues": 1, "Lack of Standards and Reference Architecture": 1, "Lack of Internet coverage and IT facilities": 1, "Limited Access to Funding and Credit": 3, "Future viability & profitability": 2, "Dependency on External Vendors": 2, "High Implementation Cost": 2, "Compliance with Sector-Specific Regulations": 2, "Lack of Regulations and Standards": 2, "Customers are hesitant to share data": 1}, "Taxation and Compliance Costs": {"input_key": "taxation_compliance_costs", "Lack of training for workers and managers": 1, "Resistance to change": 1, "Lack of digital culture and training": 1, "Higher investment in employees' training.": 1, "Lack of knowledge management systems": 1, "Regulatory compliance issues": 1, "Lack of Standards and Reference Architecture": 1, "Lack of Internet coverage and IT facilities": 1, "Limited Access to Funding and Credit": 1, "Future viability & profitability": 2, "Dependency on External Vendors": 1, "High Implementation Cost": 3, "Compliance with Sector-Specific Regulations": 3, "Lack of Regulations and Standards": 3, "Customers are hesitant to share data": 1}, "Supply Chain and Logistics Costs": {"input_key": "supply_chain_logistics_costs", "Lack of training for workers and managers": 1, "Resistance to change": 1, "Lack of digital culture and training": 1, "Higher investment in employees' training.": 1, "Lack of knowledge management systems": 1, "Regulatory compliance issues": 1, "Lack of Standards and Reference Architecture": 1, "Lack of Internet coverage and IT facilities": 1, "Limited Access to Funding and Credit": 2, "Future viability & profitability": 3, "Dependency on External Vendors": 2, "High Implementation Cost": 2, "Compliance with Sector-Specific Regulations": 2, "Lack of Regulations and Standards": 2, "Customers are hesitant to share data": 2}, "Technology and Digital Infrastructure Costs": {"input_key": "technology_digital_infrastructure_costs", "Lack of training for workers and managers": 3, "Resistance to change": 2, "Lack of digital culture and training": 3, "Higher investment in employees' training.": 3, "Lack of knowledge management systems": 3, "Regulatory compliance issues": 2, "Lack of Standards and Reference Architecture": 2, "Lack of Internet coverage and IT facilities": 2, "Limited Access to Funding and Credit": 1, "Future viability & profitability": 3, "Dependency on External Vendors": 1, "High Implementation Cost": 1, "Compliance with Sector-Specific Regulations": 1, "Lack of Regulations and Standards": 1, "Customers are hesitant to share data": 3}, "Training and Skill Development Costs": {"input_key": "training_skill_development_costs", "Lack of training for workers and managers": 3, "Resistance to change": 2, "Lack of digital culture and training": 3, "Higher investment in employees' training.": 3, "Lack of knowledge management systems": 3, "Regulatory compliance issues": 2, "Lack of Standards and Reference Architecture": 2, "Lack of Internet coverage and IT facilities": 2, "Limited Access to Funding and Credit": 1, "Future viability & profitability": 3, "Dependency on External Vendors": 1, "High Implementation Cost": 1, "Compliance with Sector-Specific Regulations": 1, "Lack of Regulations and Standards": 1, "Customers are hesitant to share data": 3}, "Regulatory and Compliance Costs": {"input_key": "regulatory_compliance_costs", "Lack of training for workers and managers": 1, "Resistance to change": 1, "Lack of digital culture and training": 1, "Higher investment in employees' training.": 1, "Lack of knowledge management systems": 1, "Regulatory compliance issues": 1, "Lack of Standards and Reference Architecture": 1, "Lack of Internet coverage and IT facilities": 1, "Limited Access to Funding and Credit": 1, "Future viability & profitability": 3, "Dependency on External Vendors": 1, "High Implementation Cost": 3, "Compliance with Sector-Specific Regulations": 3, "Lack of Regulations and Standards": 3, "Customers are hesitant to share data": 1}, "Insurance Costs": {"input_key": "insurance_costs", "Lack of training for workers and managers": 1, "Resistance to change": 1, "Lack of digital culture and training": 1, "Higher investment in employees' training.": 1, "Lack of knowledge management systems": 1, "Regulatory compliance issues": 1, "Lack of Standards and Reference Architecture": 1, "Lack of Internet coverage and IT facilities": 1, "Limited Access to Funding and Credit": 1, "Future viability & profitability": 1, "Dependency on External Vendors": 1, "High Implementation Cost": 1, "Compliance with Sector-Specific Regulations": 1, "Lack of Regulations and Standards": 1, "Customers are hesitant to share data": 1}, "Marketing and Customer Acquisition Costs": {"input_key": "marketing_customer_acquisition_costs", "Lack of training for workers and managers": 1, "Resistance to change": 1, "Lack of digital culture and training": 1, "Higher investment in employees' training.": 1, "Lack of knowledge management systems": 1, "Regulatory compliance issues": 1, "Lack of Standards and Reference Architecture": 1, "Lack of Internet coverage and IT facilities": 1, "Limited Access to Funding and Credit": 1, "Future viability & profitability": 3, "Dependency on External Vendors": 1, "High Implementation Cost": 1, "Compliance with Sector-Specific Regulations": 1, "Lack of Regulations and Standards": 1, "Customers are hesitant to share data": 1}, "Environmental and Social Responsibility Costs": {"input_key": "environmental_social_responsibility_costs", "Lack of training for workers and managers": 2, "Resistance to change": 1, "Lack of digital culture and training": 2, "Higher investment in employees' training.": 2, "Lack of knowledge management systems": 2, "Regulatory compliance issues": 1, "Lack of Standards and Reference Architecture": 1, "Lack of Internet coverage and IT facilities": 1, "Limited Access to Funding and Credit": 1, "Future viability & profitability": 2, "Dependency on External Vendors": 1, "High Implementation Cost": 1, "Compliance with Sector-Specific Regulations": 1, "Lack of Regulations and Standards": 1, "Customers are hesitant to share data": 1}, "Quality Control and Assurance": {"input_key": "quality_control_assurance", "Lack of training for workers and managers": 1, "Resistance to change": 1, "Lack of digital culture and training": 1, "Higher investment in employees' training.": 1, "Lack of knowledge management systems": 1, "Regulatory compliance issues": 1, "Lack of Standards and Reference Architecture": 1, "Lack of Internet coverage and IT facilities": 1, "Limited Access to Funding and Credit": 1, "Future viability & profitability": 3, "Dependency on External Vendors": 1, "High Implementation Cost": 1, "Compliance with Sector-Specific Regulations": 1, "Lack of Regulations and Standards": 1, "Customers are hesitant to share data": 1}
}

KPI_FACTOR_MAPPING = {
    "Asset & Equipment Efficiency": {"input_key": "asset_equipment_efficiency", "Lack of training for workers and managers": 1, "Resistance to change": 1, "Lack of digital culture and training": 1, "Higher investment in employees' training.": 1, "Lack of knowledge management systems": 1, "Regulatory compliance issues": 1, "Lack of Standards and Reference Architecture": 1, "Lack of Internet coverage and IT facilities": 1, "Limited Access to Funding and Credit": 2, "Future viability & profitability": 3, "Dependency on External Vendors": 2, "High Implementation Cost": 1, "Compliance with Sector-Specific Regulations": 1, "Lack of Regulations and Standards": 1, "Customers are hesitant to share data": 1}, "Utilities Efficiency": {"input_key": "utilities_efficiency", "Lack of training for workers and managers": 1, "Resistance to change": 1, "Lack of digital culture and training": 1, "Higher investment in employees' training.": 1, "Lack of knowledge management systems": 1, "Regulatory compliance issues": 0, "Lack of Standards and Reference Architecture": 0, "Lack of Internet coverage and IT facilities": 0, "Limited Access to Funding and Credit": 1, "Future viability & profitability": 2, "Dependency on External Vendors": 1, "High Implementation Cost": 0, "Compliance with Sector-Specific Regulations": 0, "Lack of Regulations and Standards": 0, "Customers are hesitant to share data": 0}, "Inventory Efficiency": {"input_key": "inventory_efficiency", "Lack of training for workers and managers": 1, "Resistance to change": 1, "Lack of digital culture and training": 1, "Higher investment in employees' training.": 1, "Lack of knowledge management systems": 1, "Regulatory compliance issues": 1, "Lack of Standards and Reference Architecture": 1, "Lack of Internet coverage and IT facilities": 1, "Limited Access to Funding and Credit": 2, "Future viability & profitability": 3, "Dependency on External Vendors": 2, "High Implementation Cost": 1, "Compliance with Sector-Specific Regulations": 1, "Lack of Regulations and Standards": 1, "Customers are hesitant to share data": 1}, "Process Quality": {"input_key": "process_quality", "Lack of training for workers and managers": 2, "Resistance to change": 2, "Lack of digital culture and training": 2, "Higher investment in employees' training.": 2, "Lack of knowledge management systems": 2, "Regulatory compliance issues": 2, "Lack of Standards and Reference Architecture": 2, "Lack of Internet coverage and IT facilities": 2, "Limited Access to Funding and Credit": 1, "Future viability & profitability": 3, "Dependency on External Vendors": 1, "High Implementation Cost": 1, "Compliance with Sector-Specific Regulations": 2, "Lack of Regulations and Standards": 2, "Customers are hesitant to share data": 2}, "Product Quality": {"input_key": "product_quality", "Lack of training for workers and managers": 2, "Resistance to change": 2, "Lack of digital culture and training": 2, "Higher investment in employees' training.": 2, "Lack of knowledge management systems": 2, "Regulatory compliance issues": 2, "Lack of Standards and Reference Architecture": 2, "Lack of Internet coverage and IT facilities": 2, "Limited Access to Funding and Credit": 1, "Future viability & profitability": 3, "Dependency on External Vendors": 1, "High Implementation Cost": 1, "Compliance with Sector-Specific Regulations": 2, "Lack of Regulations and Standards": 2, "Customers are hesitant to share data": 2}, "Safety & Security": {"input_key": "safety_security", "Lack of training for workers and managers": 1, "Resistance to change": 1, "Lack of digital culture and training": 1, "Higher investment in employees' training.": 1, "Lack of knowledge management systems": 1, "Regulatory compliance issues": 2, "Lack of Standards and Reference Architecture": 2, "Lack of Internet coverage and IT facilities": 2, "Limited Access to Funding and Credit": 0, "Future viability & profitability": 2, "Dependency on External Vendors": 2, "High Implementation Cost": 1, "Compliance with Sector-Specific Regulations": 2, "Lack of Regulations and Standards": 2, "Customers are hesitant to share data": 2}, "Planning & Scheduling Effectiveness": {"input_key": "planning_scheduling_effectiveness", "Lack of training for workers and managers": 2, "Resistance to change": 2, "Lack of digital culture and training": 2, "Higher investment in employees' training.": 2, "Lack of knowledge management systems": 2, "Regulatory compliance issues": 1, "Lack of Standards and Reference Architecture": 1, "Lack of Internet coverage and IT facilities": 2, "Limited Access to Funding and Credit": 1, "Future viability & profitability": 3, "Dependency on External Vendors": 2, "High Implementation Cost": 1, "Compliance with Sector-Specific Regulations": 1, "Lack of Regulations and Standards": 1, "Customers are hesitant to share data": 1}, "Time to Market": {"input_key": "time_to_market", "Lack of training for workers and managers": 1, "Resistance to change": 1, "Lack of digital culture and training": 2, "Higher investment in employees' training.": 2, "Lack of knowledge management systems": 2, "Regulatory compliance issues": 1, "Lack of Standards and Reference Architecture": 1, "Lack of Internet coverage and IT facilities": 2, "Limited Access to Funding and Credit": 2, "Future viability & profitability": 3, "Dependency on External Vendors": 2, "High Implementation Cost": 2, "Compliance with Sector-Specific Regulations": 1, "Lack of Regulations and Standards": 1, "Customers are hesitant to share data": 1}, "Production Flexibility": {"input_key": "production_flexibility", "Lack of training for workers and managers": 2, "Resistance to change": 2, "Lack of digital culture and training": 2, "Higher investment in employees' training.": 2, "Lack of knowledge management systems": 2, "Regulatory compliance issues": 2, "Lack of Standards and Reference Architecture": 2, "Lack of Internet coverage and IT facilities": 2, "Limited Access to Funding and Credit": 2, "Future viability & profitability": 3, "Dependency on External Vendors": 2, "High Implementation Cost": 1, "Compliance with Sector-Specific Regulations": 2, "Lack of Regulations and Standards": 1, "Customers are hesitant to share data": 2}, "Customer Satisfaction": {"input_key": "customer_satisfaction", "Lack of training for workers and managers": 1, "Resistance to change": 1, "Lack of digital culture and training": 1, "Higher investment in employees' training.": 1, "Lack of knowledge management systems": 1, "Regulatory compliance issues": 2, "Lack of Standards and Reference Architecture": 2, "Lack of Internet coverage and IT facilities": 1, "Limited Access to Funding and Credit": 1, "Future viability & profitability": 3, "Dependency on External Vendors": 1, "High Implementation Cost": 1, "Compliance with Sector-Specific Regulations": 2, "Lack of Regulations and Standards": 2, "Customers are hesitant to share data": 2}, "Supply Chain Efficiency": {"input_key": "supply_chain_efficiency", "Lack of training for workers and managers": 1, "Resistance to change": 1, "Lack of digital culture and training": 1, "Higher investment in employees' training.": 1, "Lack of knowledge management systems": 1, "Regulatory compliance issues": 1, "Lack of Standards and Reference Architecture": 1, "Lack of Internet coverage and IT facilities": 2, "Limited Access to Funding and Credit": 2, "Future viability & profitability": 3, "Dependency on External Vendors": 3, "High Implementation Cost": 2, "Compliance with Sector-Specific Regulations": 1, "Lack of Regulations and Standards": 2, "Customers are hesitant to share data": 1}, "Market Share Growth": {"input_key": "market_share_growth", "Lack of training for workers and managers": 2, "Resistance to change": 2, "Lack of digital culture and training": 1, "Higher investment in employees' training.": 1, "Lack of knowledge management systems": 2, "Regulatory compliance issues": 2, "Lack of Standards and Reference Architecture": 2, "Lack of Internet coverage and IT facilities": 2, "Limited Access to Funding and Credit": 2, "Future viability & profitability": 3, "Dependency on External Vendors": 1, "High Implementation Cost": 2, "Compliance with Sector-Specific Regulations": 2, "Lack of Regulations and Standards": 1, "Customers are hesitant to share data": 1}, "Employee Productivity": {"input_key": "employee_productivity", "Lack of training for workers and managers": 3, "Resistance to change": 3, "Lack of digital culture and training": 3, "Higher investment in employees' training.": 3, "Lack of knowledge management systems": 3, "Regulatory compliance issues": 1, "Lack of Standards and Reference Architecture": 1, "Lack of Internet coverage and IT facilities": 1, "Limited Access to Funding and Credit": 2, "Future viability & profitability": 3, "Dependency on External Vendors": 2, "High Implementation Cost": 1, "Compliance with Sector-Specific Regulations": 1, "Lack of Regulations and Standards": 1, "Customers are hesitant to share data": 1}, "Return on Investment (ROI)": {"input_key": "return_on_investment_roi", "Lack of training for workers and managers": 2, "Resistance to change": 2, "Lack of digital culture and training": 2, "Higher investment in employees' training.": 2, "Lack of knowledge management systems": 2, "Regulatory compliance issues": 3, "Lack of Standards and Reference Architecture": 2, "Lack of Internet coverage and IT facilities": 2, "Limited Access to Funding and Credit": 3, "Future viability & profitability": 3, "Dependency on External Vendors": 2, "High Implementation Cost": 3, "Compliance with Sector-Specific Regulations": 3, "Lack of Regulations and Standards": 3, "Customers are hesitant to share data": 2}, "Financial Health and Stability": {"input_key": "financial_health_and_stability", "Lack of training for workers and managers": 2, "Resistance to change": 2, "Lack of digital culture and training": 2, "Higher investment in employees' training.": 2, "Lack of knowledge management systems": 2, "Regulatory compliance issues": 3, "Lack of Standards and Reference Architecture": 2, "Lack of Internet coverage and IT facilities": 2, "Limited Access to Funding and Credit": 3, "Future viability & profitability": 3, "Dependency on External Vendors": 2, "High Implementation Cost": 3, "Compliance with Sector-Specific Regulations": 3, "Lack of Regulations and Standards": 3, "Customers are hesitant to share data": 2}, "Talent Retention": {"input_key": "talent_retention", "Lack of training for workers and managers": 3, "Resistance to change": 3, "Lack of digital culture and training": 3, "Higher investment in employees' training.": 2, "Lack of knowledge management systems": 3, "Regulatory compliance issues": 1, "Lack of Standards and Reference Architecture": 1, "Lack of Internet coverage and IT facilities": 1, "Limited Access to Funding and Credit": 1, "Future viability & profitability": 2, "Dependency on External Vendors": 1, "High Implementation Cost": 1, "Compliance with Sector-Specific Regulations": 1, "Lack of Regulations and Standards": 1, "Customers are hesitant to share data": 1}, "Customer Retention Rate": {"input_key": "customer_retention_rate", "Lack of training for workers and managers": 2, "Resistance to change": 2, "Lack of digital culture and training": 2, "Higher investment in employees' training.": 2, "Lack of knowledge management systems": 2, "Regulatory compliance issues": 2, "Lack of Standards and Reference Architecture": 2, "Lack of Internet coverage and IT facilities": 2, "Limited Access to Funding and Credit": 1, "Future viability & profitability": 3, "Dependency on External Vendors": 2, "High Implementation Cost": 1, "Compliance with Sector-Specific Regulations": 2, "Lack of Regulations and Standards": 2, "Customers are hesitant to share data": 3},
}

# --- Calculation Functions (UNCHANGED) ---

def calculate_barrier_score(barrier_name: str, inputs: BaseModel) -> Dict:
    definition = BARRIER_DEFINITIONS.get(barrier_name)
    if not definition:
        raise ValueError(f"Barrier definition not found for: {barrier_name}")
    indicator_scores = []
    barrier_details = []
    for indicator_def in definition["indicators"]:
        indicator_name = indicator_def["name"]
        weight = indicator_def["weight"]
        raw_value = None
        input_display = ""
        indicator_calculation_desc = ""
        normalized_value_display = ""
        normalized_value = 0.0
        input_key_pydantic = definition["doc_input_map"].get(indicator_name)
        raw_value = getattr(inputs, input_key_pydantic, None)
        if barrier_name == "Lack of training for workers and managers" and indicator_name == "i. Number of training programs offered per year.":
            raw_value = min(raw_value, 5.0)
        input_display = str(raw_value)
        if barrier_name == "Resistance to change" and indicator_name == "ii.Percentage of employees who express resistance to adopting new technologies in surveys.":
            indicator_value = raw_value / 100
            normalized_value = 1 - indicator_value
            indicator_calculation_desc = f"1 - ({raw_value} / 100)"
            normalized_value_display = f"{normalized_value:.15f}"
        elif indicator_def["type"] == "inverted_ratio":
            target = indicator_def["target"]
            if target == 0:
                normalized_value = 1.0 if raw_value > 0 else 0.0
                indicator_calculation_desc = "N/A (Target is 0)"
            else:
                normalized_value = 1 - (raw_value / target)
                indicator_calculation_desc = f"1 - ({raw_value} / {target})"
        elif indicator_def["type"] == "inverted_percentage":
            normalized_value = 1 - (raw_value / 100)
            indicator_calculation_desc = f"1 - ({raw_value} / 100)"
        elif indicator_def["type"] == "percentage":
            normalized_value = raw_value / 100
            indicator_calculation_desc = f"{raw_value} / 100"
        elif indicator_def["type"] == "ratio":
            divisor = None
            if "crisis_level" in indicator_def:
                divisor = indicator_def["crisis_level"]
            elif "benchmark" in indicator_def:
                divisor = indicator_def["benchmark"]
            else:
                raise ValueError(f"Missing 'crisis_level' or 'benchmark' for ratio indicator '{indicator_name}' in barrier '{barrier_name}'")
            if divisor == 0:
                normalized_value = 1.0 if raw_value > 0 else 0.0
                indicator_calculation_desc = "N/A (Divisor is 0)"
            else:
                normalized_value = raw_value / divisor
                indicator_calculation_desc = f"{raw_value} / {divisor}"
        elif indicator_def["type"] == "frequency_map":
            freq_map = definition["frequency_map"]
            normalized_value = freq_map.get(raw_value, 1.0)
            indicator_calculation_desc = f"Mapped from '{raw_value}'"
        elif indicator_def["type"] == "custom_div_50":
            indicator_value = raw_value / 50
            normalized_value = 1 - indicator_value
            indicator_calculation_desc = f"1 - ({raw_value} / 50)"
            normalized_value_display = f"{normalized_value:.15f}"
        elif indicator_def["type"] == "custom_div_5":
            indicator_value = raw_value / 5
            normalized_value = 1 - indicator_value
            indicator_calculation_desc = f"1 - ({raw_value} / 5)"
            normalized_value_display = f"{normalized_value:.15f}"
        elif indicator_def["type"] == "custom_inv_div_5":
            indicator_value = raw_value / 5
            normalized_value = indicator_value
            indicator_calculation_desc = f"{raw_value} / 5"
            normalized_value_display = f"{normalized_value:.15f}"
        elif indicator_def["type"] == "custom_div_100":
            indicator_value = raw_value / 100
            normalized_value = indicator_value
            indicator_calculation_desc = f"{raw_value} / 100"
            normalized_value_display = f"{normalized_value:.15f}"
        elif barrier_name == "Lack of training for workers and managers" and indicator_def["name"] == "iii.Budget allocation for employee training":
            pct_budget_training_of_payroll = inputs.pct_budget_training_of_payroll
            divisor = 2.5
            input_display = f"{pct_budget_training_of_payroll}% of payroll"
            if divisor == 0:
                normalized_value = 1.0
                indicator_calculation_desc = "N/A (Divisor is 0)"
            else:
                h_value = pct_budget_training_of_payroll
                normalized_value = 1 - (h_value / divisor)
                indicator_calculation_desc = f"1 - ({h_value} / {divisor})"
            normalized_value_display = f"{normalized_value:.15f}"
            raw_value = pct_budget_training_of_payroll
        elif barrier_name == "Higher investment in employees' training." and indicator_def["name"] == "i.Training expenditure as a percentage of total operational costs.":
            pct_training_expenditure_of_op_costs = inputs.pct_training_expenditure_of_op_costs
            divisor = 5.0
            input_display = f"{pct_training_expenditure_of_op_costs}% of operational costs"
            if divisor == 0:
                normalized_value = 1.0
                indicator_calculation_desc = "N/A (Divisor is 0)"
            else:
                h_value = pct_training_expenditure_of_op_costs
                normalized_value = 1 - (h_value / divisor)
                indicator_calculation_desc = f"1 - ({h_value} / {divisor})"
            normalized_value_display = f"{normalized_value:.15f}"
            raw_value = pct_training_expenditure_of_op_costs
        else:
            raise ValueError(f"Unknown indicator type: {indicator_def['type']}")
        normalized_value = max(0.0, min(1.0, normalized_value))
        weighted_score = normalized_value * weight * 10
        indicator_scores.append(weighted_score)
        barrier_details.append({"Sr. No.": definition["sr_no"], "Indicator": indicator_name, "Input": input_display, "Indicator Calculation": indicator_calculation_desc, "Normalized Value": normalized_value_display or f"{normalized_value:.15f}", "Weight": weight, "Score": weighted_score})
    total_barrier_score = sum(indicator_scores)
    return {"total_score": total_barrier_score, "details": barrier_details}

def calculate_cost_factors(cost_inputs: CostFactorInput) -> Dict[str, Union[List[Dict], Dict[str, float]]]:
    barrier_cost_factors = {barrier: 0.0 for barrier in list(COST_FACTOR_MAPPING_BARRIERS.values())[0].keys() if barrier != "input_key"}
    for cost_category, mapping in COST_FACTOR_MAPPING_BARRIERS.items():
        input_value = getattr(cost_inputs, mapping["input_key"])
        for barrier_name, multiplier in mapping.items():
            if barrier_name != "input_key":
                barrier_cost_factors[barrier_name] += input_value * multiplier
    detailed_output = []
    for cost_category, mapping in COST_FACTOR_MAPPING_BARRIERS.items():
        row = {"Cost Categories": cost_category, "Input": getattr(cost_inputs, mapping["input_key"])}
        row.update({b: mapping[b] for b in barrier_cost_factors.keys()})
        detailed_output.append(row)
    total_row = {"Cost Categories": "Cost Factor", "Input": ""}
    total_row.update(barrier_cost_factors)
    detailed_output.append(total_row)
    return {"detailed_output": detailed_output, "barrier_cost_factors": barrier_cost_factors}

def calculate_kpi_factors(kpi_inputs: KPIFactorInput) -> Dict[str, Union[List[Dict], Dict[str, float]]]:
    detailed_kpi_factors = []
    aggregated_kpi_factors_barriers = {"Lack of training for workers and managers": 0.0, "Resistance to change": 0.0, "Lack of digital culture and training": 0.0, "Higher investment in employees' training.": 0.0, "Lack of knowledge management systems": 0.0, "Regulatory compliance issues": 0.0, "Lack of Standards and Reference Architecture": 0.0, "Lack of Internet coverage and IT facilities": 0.0, "Limited Access to Funding and Credit": 0.0, "Future viability & profitability": 0.0, "Dependency on External Vendors": 0.0, "High Implementation Cost": 0.0, "Compliance with Sector-Specific Regulations": 0.0, "Lack of Regulations and Standards": 0.0, "Customers are hesitant to share data": 0.0,}
    barrier_names_list = list(aggregated_kpi_factors_barriers.keys())
    for kpi_category, mapping in KPI_FACTOR_MAPPING.items():
        input_val = getattr(kpi_inputs, mapping["input_key"])
        row_data = {"KPI Categories": kpi_category, "Input": input_val}
        for barrier_name in barrier_names_list:
            multiplier = mapping.get(barrier_name, 0)
            row_data[barrier_name] = input_val * multiplier
            aggregated_kpi_factors_barriers[barrier_name] += input_val * multiplier
        detailed_kpi_factors.append(row_data)
    total_row = {"KPI Categories": "KPI Factor", "Input": ""}
    total_row.update(aggregated_kpi_factors_barriers)
    detailed_kpi_factors.append(total_row)
    return {"detailed_output": detailed_kpi_factors, "aggregated_barriers": aggregated_kpi_factors_barriers}

def calculate_isri(barrier_scores: Dict[str, float], cost_factors_aggregated: Dict[str, float], kpi_factors_aggregated: Dict[str, float]) -> List[Dict]:
    isri_results = []
    barrier_order = ["Lack of training for workers and managers", "Resistance to change", "Lack of digital culture and training", "Higher investment in employees' training.", "Lack of knowledge management systems", "Regulatory compliance issues", "Lack of Standards and Reference Architecture", "Lack of Internet coverage and IT facilities", "Limited Access to Funding and Credit", "Future viability & profitability", "Dependency on External Vendors", "High Implementation Cost", "Compliance with Sector-Specific Regulations", "Lack of Regulations and Standards", "Customers are hesitant to share data"]
    COST_FACTOR_TOTAL = sum(cost_factors_aggregated.values())
    KPI_FACTOR_TOTAL = sum(kpi_factors_aggregated.values())
    BARRIER_SCORE_TOTAL = sum(barrier_scores.values())
    W_COST = 0.3
    W_KPI = 0.4
    W_BS = 0.3
    for barrier_name in barrier_order:
        bs = barrier_scores.get(barrier_name, 0.0)
        cf = cost_factors_aggregated.get(barrier_name, 0.0)
        kpi = kpi_factors_aggregated.get(barrier_name, 0.0)
        norm_bs = (bs / BARRIER_SCORE_TOTAL) if BARRIER_SCORE_TOTAL != 0 else 0
        norm_cf = (cf / COST_FACTOR_TOTAL) if COST_FACTOR_TOTAL != 0 else 0
        norm_kpi = (kpi / KPI_FACTOR_TOTAL) if KPI_FACTOR_TOTAL != 0 else 0
        final_impact_value = (norm_bs * W_BS) + (norm_cf * W_COST) + (norm_kpi * W_KPI)
        isri_results.append({"Barriers": barrier_name, "Cost Factor": cf, "KPI Factor": kpi, "Barrier Score": bs, "Cost Factor-N": norm_cf, "KPI Factor-N": norm_kpi, "Barrier Score-N": norm_bs, "Barrier Impact Value": final_impact_value})
    return isri_results

def get_barrier_level_from_score(score: float) -> str:
    if score <= 3.0: return "Low"
    elif score <= 7.0: return "Moderate"
    elif score <= 8.5: return "High"
    else: return "Critically High"

def get_top_three_barriers_by_impact(isri_data: List[Dict]) -> List[str]:
    sorted_barriers = sorted(isri_data, key=lambda x: x.get("Barrier Impact Value", 0), reverse=True)
    top_three_barriers = [barrier["Barriers"] for barrier in sorted_barriers[:3]]
    return top_three_barriers

def extract_content_from_pdf(barrier_name: str) -> str:
    if barrier_name not in BARRIER_DEFINITIONS:
        return f"Barrier definition for '{barrier_name}' not found."
    sr_no = BARRIER_DEFINITIONS[barrier_name]['sr_no']
    file_path = f"barrier_analysis/barrier_{sr_no}_report.pdf"
    if not os.path.exists(file_path):
        return f"Detailed analysis file for '{barrier_name}' not found at {file_path}."
    content = []
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                content.append(page.extract_text())
                tables = page.extract_tables()
                for table in tables:
                    content.append("\n" + pd.DataFrame(table).to_string(index=False, header=False))
    except Exception as e:
        return f"Error extracting content from PDF for '{barrier_name}': {e}"
    return "\n\n".join(content)

# --- Add this new helper function somewhere before your app = FastAPI() line ---

import markdown2
from weasyprint import HTML, CSS
from fastapi.responses import StreamingResponse # Make sure to import this
import zipfile

def create_pdf_from_markdown(markdown_content: str, report_title: str) -> bytes:
    """
    Converts a markdown string into a styled PDF document in memory.
    """
    # Convert markdown to HTML
    html_content = markdown2.markdown(markdown_content, extras=["tables", "fenced-code-blocks"])

    # Basic CSS for styling the PDF for a professional look
    # (You can customize this heavily)
    css_style = """
    @page {
        size: A4;
        margin: 2cm;
    }
    body {
        font-family: 'Times New Roman', serif;
        font-size: 12pt;
        line-height: 1.5;
    }
    h1, h2, h3 {
        font-family: 'Arial', sans-serif;
        color: #333;
        line-height: 1.2;
    }
    h1 { font-size: 24pt; }
    h2 { font-size: 18pt; }
    h3 { font-size: 14pt; font-weight: bold; }
    table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 1em;
        margin-bottom: 1em;
    }
    th, td {
        border: 1px solid #ccc;
        padding: 8px;
        text-align: left;
    }
    th {
        background-color: #f2f2f2;
    }
    """

    # Combine into a full HTML document
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{report_title}</title>
    </head>
    <body>
        <h1>{report_title}</h1>
        {html_content}
    </body>
    </html>
    """

    # Generate the PDF
    html_doc = HTML(string=full_html)
    css_doc = CSS(string=css_style)
    
    # Write PDF to an in-memory buffer
    pdf_bytes = html_doc.write_pdf(stylesheets=[css_doc])
    
    return pdf_bytes

async def generate_comprehensive_report_with_mistral(all_barrier_data: Dict[str, Dict]) -> str:
    if not MISTRAL_API_KEY:
        return "Mistral API key is not configured. Cannot generate report."
    full_report_prompt = []
    for barrier_name, data in all_barrier_data.items():
        score = data['total_score']
        level = get_barrier_level_from_score(score)
        barrier_report_section = f"### Barrier: {barrier_name}\n"
        barrier_report_section += f"- **Barrier Score:** {score:.2f} / 10\n"
        barrier_report_section += f"- **Severity:** {level}\n\n"
        for indicator in data['indicators']:
            indicator_desc = f"**{indicator['Indicator']}** - On a scale of 10, this SME's score for the barrier \"{barrier_name}\" is {score:.2f}, indicating a {level} problem area that requires attention. The analysis reveals that the input value for this indicator is '{indicator['Input']}'. This input directly contributes to the overall score, highlighting a specific area of concern."
            if indicator['Indicator'] == "i. Number of training programs offered per year.":
                indicator_desc = f"**Number of training programs offered per year** - On a scale of 10, this SME's score for the barrier \"{barrier_name}\" is {score:.2f}, indicating a {level} problem area that requires immediate attention. The analysis identifies the core issue as a significant deficit in proactive skill development, evidenced by the low number of training programs offered per year. Without a consistent and strategic offering of training, the workforce will remain unprepared for new digital technologies, creating a foundational obstacle to any IoT initiative. The SME must invest in a robust, ongoing training curriculum to build a digitally-fluent workforce."
            elif indicator['Indicator'] == "ii Percentage of employees trained in digital technologies.":
                indicator_desc = f"**Percentage of employees trained in digital technologies** - On a scale of 10, this SME's score for the barrier \"{barrier_name}\" is {score:.2f}, indicating a {level} problem. The most significant issue is the low percentage of employees trained in digital technologies ({indicator['Input']}%). This reveals a major skill gap across the organization, making the adoption of new IoT tools and processes nearly impossible. It is a critical bottleneck that highlights a failure in either the availability or the accessibility of digital training. Addressing this requires a top-down mandate to upskill the entire workforce."
            elif indicator['Indicator'] == "iii.Budget allocation for employee training":
                indicator_desc = f"**Budget allocation for employee training** - On a scale of 10, this SME's score for the barrier \"{barrier_name}\" is {score:.2f}, indicating a {level} problem. The analysis suggests the root cause is a strategic failure in resource allocation, evidenced by the insufficient budget allocated for employee training ({indicator['Input']}% of payroll). This financial constraint is the ultimate source of the training deficit, preventing the organization from procuring quality programs and demonstrating a lack of top-management commitment to upskilling the workforce. Leadership must view training as a strategic investment, not a cost, to enable future growth."
            barrier_report_section += f"{indicator_desc}\n\n"
        full_report_prompt.append(barrier_report_section)
    final_prompt = f"""
    You are an expert consultant specializing in Indian SME readiness for IoT adoption. You have been provided with a detailed breakdown of barrier scores for an Indian SME. The scores are on a scale of 0-10, where 10 indicates the highest barrier. Please generate a professional, structured, and actionable report. The report should:
    1. Provide a brief overall summary of the SME's IoT readiness based on the collective scores.
    2. For each barrier and its sub-indicators, provide the analysis and interpretation below in a coherent manner.
    3. Conclude with a high-level recommendation for the SME.
    Here is the company details:
    {calculated_data.get("company_details", {})}
    Here is the detailed data and analysis to include in the report:
    {full_report_prompt}
    """
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json",}
    payload = {"model": MISTRAL_MODEL, "messages": [{"role": "user", "content": final_prompt}], "temperature": 0.7, "max_tokens": 10000,}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(MISTRAL_API_URL, headers=headers, json=payload, timeout=60.0)
            response.raise_for_status()
            mistral_response = response.json()
            if mistral_response and mistral_response.get("choices"):
                return mistral_response["choices"][0]["message"]["content"]
            else:
                return "Mistral API did not return a valid response for the report."
    except httpx.HTTPStatusError as e: return f"Mistral API HTTP error: {e.response.status_code} - {e.response.text}"
    except httpx.RequestError as e: return f"Mistral API request error: {e}"
    except Exception as e: return f"An unexpected error occurred during Mistral API call: {e}"

async def generate_roadmap_with_mistral(top_barriers_data: List[Dict]) -> Dict:
    if not MISTRAL_API_KEY:
        return {"error": "Mistral API key is not configured. Cannot generate report."}
    prompt_sections = []
    for barrier in top_barriers_data:
        barrier_name = barrier["barrier_name"]
        barrier_score = barrier["barrier_score"]
        roadmap_text = barrier["roadmap_text"]
        severity = get_barrier_level_from_score(barrier_score)
        prompt_sections.append(f"""
### Barrier: {barrier_name}
- **Barrier Score:** {barrier_score:.2f} / 10
- **Severity:** {severity}
- **Detailed Analysis and Action Plan:**
{roadmap_text}
""")
    final_prompt = f"""
You are an expert consultant specializing in Indian SME readiness for IoT adoption. You have been provided with a detailed analysis and action plan for the top three barriers identified for a specific Indian SME. Your task is to take the provided information and rewrite it into a cohesive, professional, and actionable roadmap report for the SME's leadership. The report should:
1.  Begin with a professional greeting and disclaimer.
2.  Provide a brief executive summary of the top three critical barriers.
3.  For each of the three barriers, present the "Detailed Analysis & Action Plan" in a clear and structured format.
4.  Ensure that the tone is consultative and the recommendations are clear and actionable.
5.  Conclude with a professional closing statement.
Here is the company details:
{calculated_data.get("company_details", {})}
Here is the detailed data for the top three barriers:
{prompt_sections}
"""
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json",}
    payload = {"model": MISTRAL_MODEL, "messages": [{"role": "user", "content": final_prompt}], "temperature": 0.7, "max_tokens": 4000,}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(MISTRAL_API_URL, headers=headers, json=payload, timeout=120.0)
            response.raise_for_status()
            mistral_response = response.json()
            if mistral_response and mistral_response.get("choices"):
                return {"report": mistral_response["choices"][0]["message"]["content"]}
            else:
                return {"error": "Mistral API did not return a valid response for the report."}
    except httpx.HTTPStatusError as e: return {"error": f"Mistral API HTTP error: {e.response.status_code} - {e.response.text}"}
    except httpx.RequestError as e: return {"error": f"Mistral API request error: {e}"}
    except Exception as e: return {"error": f"An unexpected error occurred: {e}"}
        
# --- FastAPI App ---

app = FastAPI(
    title="ISRI Calculation and Reporting API",
    description="A single endpoint to calculate the Indian SME Readiness Index (ISRI), generate a barrier analysis, and create a strategic roadmap using Mistral AI.",
    version="2.0.0",
)

# --- NEW: The Single, Consolidated Endpoint ---

@app.post("/generate_full_report", summary="Generate a complete AI-powered analysis and roadmap")
async def generate_full_report(inputs: ComprehensiveInput):
    """
    This single endpoint performs all necessary actions in sequence:
    1.  Accepts all company, barrier, cost, and KPI data.
    2.  Calculates Barrier Scores, Cost Factors, and KPI Factors.
    3.  Calculates the final ISRI (Barrier Impact Value).
    4.  Generates a comprehensive AI-powered barrier analysis report.
    5.  Identifies the top 3 barriers and generates a detailed AI-powered strategic roadmap.
    6.  Returns both AI-generated reports in the response.
    """
    try:
        # Step 0: Store company details in the global state for the AI functions
        calculated_data["company_details"] = inputs.company_details.dict()

        # Step 1: Calculate Barrier Scores
        all_barrier_scores = {}
        barrier_score_details_list = []
        barrier_input_map_from_all_inputs = {
            "Lack of training for workers and managers": inputs.barrier1,
            "Resistance to change": inputs.barrier2,
            "Lack of digital culture and training": inputs.barrier3,
            "Higher investment in employees' training.": inputs.barrier4,
            "Lack of knowledge management systems": inputs.barrier5,
            "Regulatory compliance issues": inputs.barrier6,
            "Lack of Standards and Reference Architecture": inputs.barrier7,
            "Lack of Internet coverage and IT facilities": inputs.barrier8,
            "Limited Access to Funding and Credit": inputs.barrier9,
            "Future viability & profitability": inputs.barrier10,
            "Dependency on External Vendors": inputs.barrier11,
            "High Implementation Cost": inputs.barrier12,
            "Compliance with Sector-Specific Regulations": inputs.barrier13,
            "Lack of Regulations and Standards": inputs.barrier14,
            "Customers are hesitant to share data": inputs.barrier15
        }
        for full_barrier_name, barrier_input_obj in barrier_input_map_from_all_inputs.items():
            result = calculate_barrier_score(full_barrier_name, barrier_input_obj)
            all_barrier_scores[full_barrier_name] = result["total_score"]
            barrier_score_details_list.extend(result["details"])
        
        # Store barrier scores in global state for the roadmap function
        calculated_data["barrier_scores"] = all_barrier_scores

        # Step 2: Calculate Cost Factors
        cost_factors_results = calculate_cost_factors(inputs.cost_factor_inputs)
        calculated_cost_factors_aggregated = cost_factors_results["barrier_cost_factors"]

        # Step 3: Calculate KPI Factors
        kpi_factors_results = calculate_kpi_factors(inputs.kpi_factor_inputs)
        calculated_kpi_factors_aggregated = kpi_factors_results["aggregated_barriers"]
        
        # Step 4: Calculate ISRI
        isri_data = calculate_isri(
            barrier_scores=all_barrier_scores,
            cost_factors_aggregated=calculated_cost_factors_aggregated,
            kpi_factors_aggregated=calculated_kpi_factors_aggregated
        )
        # Store ISRI data in global state for the roadmap function
        calculated_data["isri_data"] = isri_data

        # Step 5: Generate the comprehensive AI Barrier Analysis Report
        all_barrier_data_for_ai = {
            name: {"total_score": score, "indicators": [d for d in barrier_score_details_list if d.get('Sr. No.') == BARRIER_DEFINITIONS[name]['sr_no']]} 
            for name, score in all_barrier_scores.items()
        }
        ai_barrier_report = await generate_comprehensive_report_with_mistral(all_barrier_data_for_ai)

        # Step 6: Generate the AI Strategic Roadmap Report
        # This logic is replicated from the original /generate_ai_roadmap endpoint
        top_three_barriers_data = sorted(isri_data, key=lambda x: x.get("Barrier Impact Value", 0), reverse=True)[:3]
        top_three_barriers_names = [b["Barriers"] for b in top_three_barriers_data]
        
        top_barriers_for_ai_roadmap = []
        for barrier_name in top_three_barriers_names:
            roadmap_text = extract_content_from_pdf(barrier_name)
            barrier_score = all_barrier_scores.get(barrier_name, 0.0)
            if "not found" in roadmap_text:
                # Handle missing PDF gracefully
                roadmap_text = f"Detailed roadmap information for '{barrier_name}' could not be loaded."
            
            top_barriers_for_ai_roadmap.append({
                "barrier_name": barrier_name,
                "barrier_score": barrier_score,
                "roadmap_text": roadmap_text
            })

        ai_roadmap_result = {"report": "No top barriers found to generate a roadmap."}
        if top_barriers_for_ai_roadmap:
            ai_roadmap_result = await generate_roadmap_with_mistral(top_barriers_for_ai_roadmap)

        if ai_roadmap_result.get("error"):
            raise HTTPException(status_code=500, detail=f"Failed to generate AI roadmap: {ai_roadmap_result['error']}")

        #Step 7: Convert both AI reports in PDF bytes
        try:
            analysis_pdf_bytes = create_pdf_from_markdown(ai_barrier_report, "Barrier Analysis Report")
            roadmap_pdf_bytes = create_pdf_from_markdown(ai_roadmap_result.get("report", "Roadmap report not available."), "Strategic Roadmap Report")
        except Exception as pdf_error:
            raise HTTPException(status_code=500, detail=f"Failed during PDF generation: {pdf_error}")


        # Step 8: Create a ZIP file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Add the first PDF to the ZIP
            zf.writestr("Barrier_Analysis_Report.pdf", analysis_pdf_bytes)
            # Add the second PDF to the ZIP
            zf.writestr("Strategic_Roadmap_Report.pdf", roadmap_pdf_bytes)

        # Step 9: Prepare the ZIP file for streaming response
        zip_buffer.seek(0)

        # Set headers to trigger a download in the browser
        headers = {
            'Content-Disposition': 'attachment; filename="ISRI_AI_Reports.zip"'
        }

        # Return the ZIP file as a streaming response
        return StreamingResponse(
            iter([zip_buffer.read()]),
            media_type="application/x-zip-compressed",
            headers=headers
        )

    except Exception as e:
        # Catch any exception during the process and return a detailed error
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
