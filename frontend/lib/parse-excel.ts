/**
 * Parse the IoT Assessment client Excel template and return FormData.
 *
 * Template layout (each data sheet):
 *   Col A (idx 0) : #
 *   Col B (idx 1) : Question label
 *   Col C (idx 2) : User's answer  ← the value we read
 *   Col D (idx 3) : Notes
 *   Col E (idx 4) : field_key      ← hidden column, identifies the field
 *
 * Sheets: "Company Details", "Barrier Assessment", "Cost Factors", "KPI Factors"
 */

import * as XLSX from "xlsx"
import type { FormData } from "@/components/isri-assessment-form"

// All recognised field keys grouped by section
const COMPANY_KEYS = new Set([
  "company_name", "industry", "num_employees", "annual_revenue",
])

const BARRIER_KEYS = new Set([
  // barrier1
  "num_training_programs", "pct_employees_trained", "pct_budget_training_of_payroll",
  // barrier2
  "employee_turnover_rate_pct", "pct_employees_resisting", "num_feedback_sessions",
  // barrier3
  "num_digital_skills_workshops", "pct_comfortable_digital_tools", "adoption_rate_new_digital_tools_pct",
  // barrier4
  "pct_training_expenditure_of_op_costs", "avg_training_hours_per_employee", "roi_training_programs_pct",
  // barrier5
  "num_knowledge_sharing_sessions", "pct_employees_access_kms", "freq_updates_kms",
  // barrier6
  "num_non_compliance_incidents", "pct_projects_delayed_regulatory", "time_to_achieve_compliance_days",
  // barrier7
  "num_industry_standards_adopted", "pct_iot_devices_conforming", "pct_projects_delayed_standardized_solutions",
  // barrier8
  "pct_internet_coverage", "avg_internet_speed_mbps", "freq_it_infrastructure_outages_per_month",
  // barrier9
  "pct_loan_approved", "pct_projects_delayed_lack_funding", "ratio_external_funding_total_project_costs_pct",
  // barrier10
  "yoy_revenue_growth_iot_pct", "profit_margin_improvement_iot_pct", "num_new_revenue_streams_iot",
  // barrier11
  "pct_critical_operations_reliant_vendor", "num_vendor_delays_disruptions_per_year", "cost_vendor_contracts_pct_op_expenses",
  // barrier12
  "pct_it_budget_allocated_iot", "annual_maintenance_costs_pct_op_costs", "integration_costs_pct_total_project_cost",
  // barrier13
  "num_regulatory_violations_penalties", "pct_compliance_audits_passed_without_issues", "freq_updates_internal_policies",
  // barrier14
  "pct_standards_compliant_iot_devices", "num_industry_specific_guidelines_implemented",
  // barrier15
  "pct_customers_refuse_data", "num_customer_complaints_data_sharing", "pct_customer_contracts_explicit_data_sharing",
])

// Which barrier each field belongs to
const KEY_TO_BARRIER: Record<string, string> = {
  num_training_programs: "barrier1",
  pct_employees_trained: "barrier1",
  pct_budget_training_of_payroll: "barrier1",

  employee_turnover_rate_pct: "barrier2",
  pct_employees_resisting: "barrier2",
  num_feedback_sessions: "barrier2",

  num_digital_skills_workshops: "barrier3",
  pct_comfortable_digital_tools: "barrier3",
  adoption_rate_new_digital_tools_pct: "barrier3",

  pct_training_expenditure_of_op_costs: "barrier4",
  avg_training_hours_per_employee: "barrier4",
  roi_training_programs_pct: "barrier4",

  num_knowledge_sharing_sessions: "barrier5",
  pct_employees_access_kms: "barrier5",
  freq_updates_kms: "barrier5",

  num_non_compliance_incidents: "barrier6",
  pct_projects_delayed_regulatory: "barrier6",
  time_to_achieve_compliance_days: "barrier6",

  num_industry_standards_adopted: "barrier7",
  pct_iot_devices_conforming: "barrier7",
  pct_projects_delayed_standardized_solutions: "barrier7",

  pct_internet_coverage: "barrier8",
  avg_internet_speed_mbps: "barrier8",
  freq_it_infrastructure_outages_per_month: "barrier8",

  pct_loan_approved: "barrier9",
  pct_projects_delayed_lack_funding: "barrier9",
  ratio_external_funding_total_project_costs_pct: "barrier9",

  yoy_revenue_growth_iot_pct: "barrier10",
  profit_margin_improvement_iot_pct: "barrier10",
  num_new_revenue_streams_iot: "barrier10",

  pct_critical_operations_reliant_vendor: "barrier11",
  num_vendor_delays_disruptions_per_year: "barrier11",
  cost_vendor_contracts_pct_op_expenses: "barrier11",

  pct_it_budget_allocated_iot: "barrier12",
  annual_maintenance_costs_pct_op_costs: "barrier12",
  integration_costs_pct_total_project_cost: "barrier12",

  num_regulatory_violations_penalties: "barrier13",
  pct_compliance_audits_passed_without_issues: "barrier13",
  freq_updates_internal_policies: "barrier13",

  pct_standards_compliant_iot_devices: "barrier14",
  num_industry_specific_guidelines_implemented: "barrier14",

  pct_customers_refuse_data: "barrier15",
  num_customer_complaints_data_sharing: "barrier15",
  pct_customer_contracts_explicit_data_sharing: "barrier15",
}

// String-type fields (select dropdowns — keep as-is, not parsed as numbers)
const STRING_FIELDS = new Set(["freq_updates_kms", "freq_updates_internal_policies", "company_name", "industry"])

const COST_KEYS = new Set([
  "aftermarket_services_warranty", "depreciation", "labour", "maintenance_repair",
  "raw_materials_consumables", "rental_operating_lease", "research_development",
  "selling_general_administrative_expense", "utilities", "earnings_before_interest_taxes_ebit",
  "financing_costs_interest", "taxation_compliance_costs", "supply_chain_logistics_costs",
  "technology_digital_infrastructure_costs", "training_skill_development_costs",
  "regulatory_compliance_costs", "insurance_costs", "marketing_customer_acquisition_costs",
  "environmental_social_responsibility_costs", "quality_control_assurance",
])

const KPI_KEYS = new Set([
  "asset_equipment_efficiency", "utilities_efficiency", "inventory_efficiency",
  "process_quality", "product_quality", "safety_security",
  "planning_scheduling_effectiveness", "time_to_market", "production_flexibility",
  "customer_satisfaction", "supply_chain_efficiency", "market_share_growth",
  "employee_productivity", "return_on_investment_roi", "financial_health_and_stability",
  "talent_retention", "customer_retention_rate",
])

// ── helpers ───────────────────────────────────────────────────────────────────

function extractKV(sheet: XLSX.WorkSheet): Record<string, unknown> {
  // sheet_to_json with header:1 gives array-of-arrays
  // row[4] = Col E = field_key
  // row[2] = Col C = user answer
  const rows = XLSX.utils.sheet_to_json<unknown[]>(sheet, { header: 1, defval: null })
  const kv: Record<string, unknown> = {}
  for (const row of rows) {
    if (!Array.isArray(row)) continue
    const key = row[4]
    const val = row[2]
    if (typeof key === "string" && key.trim() !== "" && val !== null && val !== undefined && val !== "") {
      kv[key.trim()] = val
    }
  }
  return kv
}

function toNumber(v: unknown): number {
  if (typeof v === "number") return v
  const n = parseFloat(String(v))
  return isNaN(n) ? 0 : n
}

function toInt(v: unknown): number {
  return Math.round(toNumber(v))
}

function yesNoToInt(v: unknown): number {
  if (typeof v === "number") return v === 0 ? 0 : 1
  const s = String(v).trim().toLowerCase()
  return s === "yes" || s === "1" ? 1 : 0
}

function clamp(n: number): number {
  if (isNaN(n)) return 0
  return Math.min(1000, Math.max(0, n))
}

// ── main export ───────────────────────────────────────────────────────────────

export interface ParseResult {
  data: FormData
  warnings: string[]
}

export async function parseExcelTemplate(file: File): Promise<ParseResult> {
  const warnings: string[] = []

  const arrayBuffer = await file.arrayBuffer()
  const workbook = XLSX.read(arrayBuffer, { type: "array" })

  // Collect all key-value pairs from the 4 data sheets
  const allKV: Record<string, unknown> = {}
  const sheetNames = ["Company Details", "Barrier Assessment", "Cost Factors", "KPI Factors"]
  const missingSheets: string[] = []

  for (const name of sheetNames) {
    const sheet = workbook.Sheets[name]
    if (!sheet) {
      missingSheets.push(name)
      continue
    }
    Object.assign(allKV, extractKV(sheet))
  }

  if (missingSheets.length > 0) {
    warnings.push(`Missing sheets: ${missingSheets.join(", ")}. Data from those sheets was skipped.`)
  }

  // ── Build FormData ──────────────────────────────────────────────────────────

  // Company details
  const company_details: FormData["company_details"] = {
    company_name: String(allKV["company_name"] ?? ""),
    industry: String(allKV["industry"] ?? ""),
    num_employees: clamp(toInt(allKV["num_employees"])),
    annual_revenue: clamp(toNumber(allKV["annual_revenue"])),
  }

  // Barriers
  const barriers: FormData["barriers"] = {
    barrier1: {}, barrier2: {}, barrier3: {}, barrier4: {}, barrier5: {},
    barrier6: {}, barrier7: {}, barrier8: {}, barrier9: {}, barrier10: {},
    barrier11: {}, barrier12: {}, barrier13: {}, barrier14: {}, barrier15: {},
  }

  for (const [key, val] of Object.entries(allKV)) {
    if (!BARRIER_KEYS.has(key)) continue
    const barrierKey = KEY_TO_BARRIER[key]
    if (!barrierKey) continue

    if (STRING_FIELDS.has(key)) {
      // Select dropdown — keep as string
      ;(barriers as any)[barrierKey][key] = String(val).trim()
    } else {
      ;(barriers as any)[barrierKey][key] = clamp(toNumber(val))
    }
  }

  // Check for missing barrier fields
  const missingBarrierFields: string[] = []
  for (const key of BARRIER_KEYS) {
    const barrierKey = KEY_TO_BARRIER[key]
    if (barrierKey && (barriers as any)[barrierKey][key] === undefined) {
      missingBarrierFields.push(key)
    }
  }
  if (missingBarrierFields.length > 0) {
    warnings.push(`${missingBarrierFields.length} barrier field(s) are empty and defaulted to 0. Check your template.`)
  }

  // Cost factors
  const cost_factor_inputs: Record<string, number> = {}
  for (const key of COST_KEYS) {
    cost_factor_inputs[key] = clamp(toNumber(allKV[key] ?? 0))
  }

  // KPI factors — Yes/No → 1/0
  const kpi_factor_inputs: Record<string, number> = {}
  for (const key of KPI_KEYS) {
    kpi_factor_inputs[key] = yesNoToInt(allKV[key] ?? 0)
  }

  return {
    data: {
      company_details,
      barriers,
      cost_factor_inputs,
      kpi_factor_inputs,
    },
    warnings,
  }
}
