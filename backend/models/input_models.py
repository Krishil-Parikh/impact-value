"""
Pydantic models for input validation
"""
from pydantic import BaseModel, Field
from typing import Literal


class CompanyDetailsInput(BaseModel):
    company_name: str = Field(..., description="Name of the company")
    industry: str = Field(..., description="Industry of the company")
    num_employees: int = Field(..., description="Number of employees")
    annual_revenue: float = Field(..., description="Annual revenue")


class Barrier1Input(BaseModel):
    num_training_programs: float = Field(..., description="Number of training programs per year (Max 5)")
    pct_employees_trained: float = Field(..., description="Percentage of employees trained (0-100)")
    pct_budget_training_of_payroll: float = Field(..., description="Training budget as % of payroll")


class Barrier2Input(BaseModel):
    employee_turnover_rate_pct: float = Field(..., description="Employee turnover rate (%)")
    pct_employees_resisting: float = Field(..., description="% of employees resisting change")
    num_feedback_sessions: int = Field(..., description="Number of feedback sessions")


class Barrier3Input(BaseModel):
    num_digital_skills_workshops: int = Field(..., description="Number of digital skills workshops")
    pct_comfortable_digital_tools: float = Field(..., description="% comfortable with digital tools")
    adoption_rate_new_digital_tools_pct: float = Field(..., description="Adoption rate of new tools (%)")


class Barrier4Input(BaseModel):
    pct_training_expenditure_of_op_costs: float = Field(..., description="Training expenditure as % of op costs")
    avg_training_hours_per_employee: float = Field(..., description="Average training hours per employee")
    roi_training_programs_pct: float = Field(..., description="ROI on training programs (%)")


class Barrier5Input(BaseModel):
    num_knowledge_sharing_sessions: int = Field(..., description="Number of knowledge-sharing sessions")
    pct_employees_access_kms: float = Field(..., description="% with access to knowledge system")
    freq_updates_kms: Literal["Daily", "Weekly", "Monthly", "Quarterly", "Bi-Annually", "Annually"] = Field(..., description="Frequency of KMS updates")


class Barrier6Input(BaseModel):
    num_non_compliance_incidents: int = Field(..., description="Number of non-compliance incidents")
    pct_projects_delayed_regulatory: float = Field(..., description="% of projects delayed due to regulations")
    time_to_achieve_compliance_days: int = Field(..., description="Time to achieve compliance (days)")


class Barrier7Input(BaseModel):
    num_industry_standards_adopted: int = Field(..., description="Number of industry standards adopted")
    pct_iot_devices_conforming: float = Field(..., description="% of IoT devices conforming to architecture")
    pct_projects_delayed_standardized_solutions: float = Field(..., description="% of projects delayed due to lack of standards")


class Barrier8Input(BaseModel):
    pct_internet_coverage: float = Field(..., description="% internet coverage")
    avg_internet_speed_mbps: float = Field(..., description="Average internet speed (Mbps)")
    freq_it_infrastructure_outages_per_month: int = Field(..., description="IT outages per month")


class Barrier9Input(BaseModel):
    pct_loan_approved: float = Field(..., description="% of loan applications approved")
    pct_projects_delayed_lack_funding: float = Field(..., description="% of projects delayed due to lack of funding")
    ratio_external_funding_total_project_costs_pct: float = Field(..., description="External funding ratio (%)")


class Barrier10Input(BaseModel):
    yoy_revenue_growth_iot_pct: float = Field(..., description="YoY revenue growth from IoT (%)")
    profit_margin_improvement_iot_pct: float = Field(..., description="Profit margin improvement (%)")
    num_new_revenue_streams_iot: int = Field(..., description="Number of new revenue streams")


class Barrier11Input(BaseModel):
    pct_critical_operations_reliant_vendor: float = Field(..., description="% of operations reliant on vendors")
    num_vendor_delays_disruptions_per_year: int = Field(..., description="Vendor delays per year")
    cost_vendor_contracts_pct_op_expenses: float = Field(..., description="Vendor costs as % of op expenses")


class Barrier12Input(BaseModel):
    pct_it_budget_allocated_iot: float = Field(..., description="% of IT budget for IoT")
    annual_maintenance_costs_pct_op_costs: float = Field(..., description="Maintenance costs as % of op costs")
    integration_costs_pct_total_project_cost: float = Field(..., description="Integration costs as % of project cost")


class Barrier13Input(BaseModel):
    num_regulatory_violations_penalties: int = Field(..., description="Number of regulatory violations")
    pct_compliance_audits_passed_without_issues: float = Field(..., description="% of audits passed")
    freq_updates_internal_policies: Literal["Monthly", "Quarterly", "Bi-Annually", "Annually"] = Field(..., description="Frequency of policy updates")


class Barrier14Input(BaseModel):
    pct_standards_compliant_iot_devices: float = Field(..., description="% of standards-compliant IoT devices")
    num_industry_specific_guidelines_implemented: int = Field(..., description="Number of guidelines implemented")


class Barrier15Input(BaseModel):
    pct_customers_refuse_data: float = Field(..., description="% of customers refusing to share data")
    num_customer_complaints_data_sharing: int = Field(..., description="Customer complaints about data sharing")
    pct_customer_contracts_explicit_data_sharing: float = Field(..., description="% of contracts with data-sharing agreements")


class CostFactorInput(BaseModel):
    aftermarket_services_warranty: float
    depreciation: float
    labour: float
    maintenance_repair: float
    raw_materials_consumables: float
    rental_operating_lease: float
    research_development: float
    selling_general_administrative_expense: float
    utilities: float
    earnings_before_interest_taxes_ebit: float
    financing_costs_interest: float
    taxation_compliance_costs: float
    supply_chain_logistics_costs: float
    technology_digital_infrastructure_costs: float
    training_skill_development_costs: float
    regulatory_compliance_costs: float
    insurance_costs: float
    marketing_customer_acquisition_costs: float
    environmental_social_responsibility_costs: float
    quality_control_assurance: float


class KPIFactorInput(BaseModel):
    asset_equipment_efficiency: float
    utilities_efficiency: float
    inventory_efficiency: float
    process_quality: float
    product_quality: float
    safety_security: float
    planning_scheduling_effectiveness: float
    time_to_market: float
    production_flexibility: float
    customer_satisfaction: float
    supply_chain_efficiency: float
    market_share_growth: float
    employee_productivity: float
    return_on_investment_roi: float
    financial_health_and_stability: float
    talent_retention: float
    customer_retention_rate: float


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
