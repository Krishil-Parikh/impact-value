"use client"

import * as React from "react"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

interface BarrierFormProps {
  barrierKey: string
  data: Record<string, any>
  onChange: (data: Record<string, any>) => void
}

type FieldType = "number" | "select" | "text"

interface Field {
  key: string
  label: string
  type: FieldType
  placeholder?: string
  options?: string[]
}

const barrierFields: Record<string, Field[]> = {
  barrier1: [
    { key: "num_training_programs", label: "Training programs offered per year", type: "number", placeholder: "Average is 5, put 5 if more than 5" },
    { key: "pct_employees_trained", label: "Employees trained in digital technologies (%)", type: "number", placeholder: "e.g., 30" },
    { key: "pct_budget_training_of_payroll", label: "Training budget as % of total payroll", type: "number", placeholder: "e.g., 2" },
  ],
  barrier2: [
    { key: "employee_turnover_rate_pct", label: "Employee turnover rate following IoT initiatives (%)", type: "number", placeholder: "e.g., 15" },
    { key: "pct_employees_resisting", label: "Employees expressing resistance (%)", type: "number", placeholder: "e.g., 20" },
    { key: "num_feedback_sessions", label: "Feedback sessions held to address concerns", type: "number", placeholder: "Number of sessions" },
  ],
  barrier3: [
    { key: "num_digital_skills_workshops", label: "Digital skills workshops attended by employees", type: "number", placeholder: "Number of workshops" },
    { key: "pct_comfortable_digital_tools", label: "Employees comfortable using digital tools (%)", type: "number", placeholder: "e.g., 30" },
    { key: "adoption_rate_new_digital_tools_pct", label: "Adoption rate of new digital tools (%)", type: "number", placeholder: "e.g., 25" },
  ],
  barrier4: [
    { key: "pct_training_expenditure_of_op_costs", label: "Training expenditure as % of operational costs", type: "number", placeholder: "e.g., 1.25" },
    { key: "avg_training_hours_per_employee", label: "Average training hours per employee per year", type: "number", placeholder: "Hours per employee" },
    { key: "roi_training_programs_pct", label: "ROI on training programs (%)", type: "number", placeholder: "e.g., 5" },
  ],
  barrier5: [
    { key: "num_knowledge_sharing_sessions", label: "Knowledge-sharing sessions conducted internally", type: "number", placeholder: "Number of sessions" },
    { key: "pct_employees_access_kms", label: "Employees with access to centralised knowledge system (%)", type: "number", placeholder: "e.g., 20" },
    { key: "freq_updates_kms", label: "Frequency of updates to knowledge management system", type: "select", options: ["Daily", "Weekly", "Monthly", "Quarterly", "Bi-Annually", "Annually"] },
  ],
  barrier6: [
    { key: "num_non_compliance_incidents", label: "Non-compliance incidents or penalties", type: "number", placeholder: "Number of incidents" },
    { key: "pct_projects_delayed_regulatory", label: "IoT projects delayed due to regulatory challenges (%)", type: "number", placeholder: "e.g., 40" },
    { key: "time_to_achieve_compliance_days", label: "Time to achieve compliance with new regulations (days)", type: "number", placeholder: "Number of days" },
  ],
  barrier7: [
    { key: "num_industry_standards_adopted", label: "Industry standards adopted by the organisation", type: "number", placeholder: "Number of standards" },
    { key: "pct_iot_devices_conforming", label: "IoT devices conforming to reference architecture (%)", type: "number", placeholder: "e.g., 50" },
    { key: "pct_projects_delayed_standardized_solutions", label: "Projects delayed due to lack of standardised solutions (%)", type: "number", placeholder: "e.g., 50" },
  ],
  barrier8: [
    { key: "pct_internet_coverage", label: "Internet coverage across all operational areas (%)", type: "number", placeholder: "e.g., 70" },
    { key: "avg_internet_speed_mbps", label: "Average internet speed across locations (Mbps)", type: "number", placeholder: "Speed in Mbps" },
    { key: "freq_it_infrastructure_outages_per_month", label: "IT infrastructure outages per month", type: "number", placeholder: "Number per month" },
  ],
  barrier9: [
    { key: "pct_loan_approved", label: "Loan applications approved (%)", type: "number", placeholder: "e.g., 80" },
    { key: "pct_projects_delayed_lack_funding", label: "Projects delayed due to lack of funding (%)", type: "number", placeholder: "e.g., 30" },
    { key: "ratio_external_funding_total_project_costs_pct", label: "External funding as % of total project costs", type: "number", placeholder: "e.g., 15" },
  ],
  barrier10: [
    { key: "yoy_revenue_growth_iot_pct", label: "Year-over-year revenue growth attributed to IoT (%)", type: "number", placeholder: "e.g., 2" },
    { key: "profit_margin_improvement_iot_pct", label: "Profit margin improvement following IoT implementation (%)", type: "number", placeholder: "e.g., 0.5" },
    { key: "num_new_revenue_streams_iot", label: "New revenue streams generated through IoT", type: "number", placeholder: "Number of streams" },
  ],
  barrier11: [
    { key: "pct_critical_operations_reliant_vendor", label: "Critical operations reliant on third-party vendors (%)", type: "number", placeholder: "e.g., 75" },
    { key: "num_vendor_delays_disruptions_per_year", label: "Vendor-related delays or disruptions per year", type: "number", placeholder: "Number per year" },
    { key: "cost_vendor_contracts_pct_op_expenses", label: "Vendor contracts cost as % of operating expenses", type: "number", placeholder: "e.g., 5" },
  ],
  barrier12: [
    { key: "pct_it_budget_allocated_iot", label: "IT budget allocated to IoT implementation (%)", type: "number", placeholder: "e.g., 50" },
    { key: "annual_maintenance_costs_pct_op_costs", label: "Annual maintenance costs as % of operational costs", type: "number", placeholder: "e.g., 3" },
    { key: "integration_costs_pct_total_project_cost", label: "Integration costs as % of total project cost", type: "number", placeholder: "e.g., 40" },
  ],
  barrier13: [
    { key: "num_regulatory_violations_penalties", label: "Regulatory violations or penalties incurred", type: "number", placeholder: "Number of violations" },
    { key: "pct_compliance_audits_passed_without_issues", label: "Compliance audits passed without issues (%)", type: "number", placeholder: "e.g., 60" },
    { key: "freq_updates_internal_policies", label: "Frequency of updates to internal policies", type: "select", options: ["Monthly", "Quarterly", "Bi-Annually", "Annually"] },
  ],
  barrier14: [
    { key: "pct_standards_compliant_iot_devices", label: "Standards-compliant IoT devices used (%)", type: "number", placeholder: "e.g., 30" },
    { key: "num_industry_specific_guidelines_implemented", label: "Industry-specific guidelines implemented", type: "number", placeholder: "Number of guidelines" },
  ],
  barrier15: [
    { key: "pct_customers_refuse_data", label: "Customers who refuse to share data (%)", type: "number", placeholder: "e.g., 40" },
    { key: "num_customer_complaints_data_sharing", label: "Customer complaints regarding data sharing", type: "number", placeholder: "Number of complaints" },
    { key: "pct_customer_contracts_explicit_data_sharing", label: "Contracts with explicit data-sharing agreements (%)", type: "number", placeholder: "e.g., 50" },
  ],
}

export function BarrierForm({ barrierKey, data, onChange }: BarrierFormProps) {
  const fields: Field[] = barrierFields[barrierKey] || []

  const clamp = (n: number) => {
    if (Number.isNaN(n)) return 0
    return Math.min(1000, Math.max(0, n))
  }

  const handleChange = (field: string, value: string | number) => {
    if (typeof value === "number") {
      onChange({ ...data, [field]: clamp(value) })
    } else {
      onChange({ ...data, [field]: value })
    }
  }

  return (
    <div className="grid gap-4">
      {fields.map((field) => (
        <div key={field.key} className="space-y-1.5">
          <Label htmlFor={field.key} className="text-sm font-medium text-foreground/90">
            {field.label}
          </Label>
          {field.type === "select" ? (
            <Select
              value={data[field.key] ?? ""}
              onValueChange={(value: string) => handleChange(field.key, value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select frequency" />
              </SelectTrigger>
              <SelectContent>
                {field.options?.map((option: string) => (
                  <SelectItem key={option} value={option}>{option}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          ) : (
            <div className="relative">
              <Input
                id={field.key}
                type={field.type}
                value={data[field.key] ?? ""}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  handleChange(
                    field.key,
                    field.type === "number" ? Number.parseFloat(e.target.value) || 0 : e.target.value,
                  )
                }
                placeholder={field.placeholder ? `${field.placeholder} (0–1000)` : "0–1000"}
                step={field.type === "number" ? "0.01" : undefined}
                min={field.type === "number" ? 0 : undefined}
                max={field.type === "number" ? 1000 : undefined}
              />
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
