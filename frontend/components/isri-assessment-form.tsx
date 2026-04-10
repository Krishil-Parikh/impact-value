"use client"

import { useRef, useState } from "react"
import { Button } from "@/components/ui/button"
import { CompanyDetailsStep } from "./form-steps/company-details-step"
import { BarriersStep } from "./form-steps/barriers-step"
import { CostFactorsStep } from "./form-steps/cost-factors-step"
import { KPIFactorsStep } from "./form-steps/kpi-factors-step"
import { ReviewStep } from "./form-steps/review-step"
import { ChevronLeft, ChevronRight, Download, FileSpreadsheet, Upload, Zap, Check } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { parseExcelTemplate } from "@/lib/parse-excel"
import { motion, AnimatePresence } from "framer-motion"
import { cn } from "@/lib/utils"

export interface FormData {
  company_details: {
    company_name: string
    industry: string
    num_employees: number
    annual_revenue: number
  }
  barriers: {
    barrier1: any; barrier2: any; barrier3: any; barrier4: any; barrier5: any
    barrier6: any; barrier7: any; barrier8: any; barrier9: any; barrier10: any
    barrier11: any; barrier12: any; barrier13: any; barrier14: any; barrier15: any
  }
  cost_factor_inputs: any
  kpi_factor_inputs: any
}

const steps = [
  { id: "company",  title: "Company",  description: "Organisation details" },
  { id: "barriers", title: "Barriers", description: "15 IoT adoption barriers" },
  { id: "costs",    title: "Costs",    description: "Cost factor analysis" },
  { id: "kpis",     title: "KPIs",     description: "Performance indicators" },
  { id: "review",   title: "Review",   description: "Review & generate" },
]

export function ISRIAssessmentForm() {
  const [currentStep, setCurrentStep] = useState(0)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { toast } = useToast()

  const [formData, setFormData] = useState<FormData>({
    company_details: { company_name: "", industry: "", num_employees: 0, annual_revenue: 0 },
    barriers: {
      barrier1: {}, barrier2: {}, barrier3: {}, barrier4: {}, barrier5: {},
      barrier6: {}, barrier7: {}, barrier8: {}, barrier9: {}, barrier10: {},
      barrier11: {}, barrier12: {}, barrier13: {}, barrier14: {}, barrier15: {},
    },
    cost_factor_inputs: {},
    kpi_factor_inputs: {},
  })

  const fillSampleData = () => {
    setFormData({
      company_details: { company_name: "XYZ", industry: "Behh", num_employees: 1000, annual_revenue: 100000 },
      barriers: {
        barrier1: { num_training_programs: 1, pct_employees_trained: 9, pct_budget_training_of_payroll: 2.272727273 },
        barrier2: { employee_turnover_rate_pct: 15, pct_employees_resisting: 40, num_feedback_sessions: 2 },
        barrier3: { num_digital_skills_workshops: 1, pct_comfortable_digital_tools: 28, adoption_rate_new_digital_tools_pct: 25 },
        barrier4: { pct_training_expenditure_of_op_costs: 1.25, avg_training_hours_per_employee: 20, roi_training_programs_pct: 5 },
        barrier5: { num_knowledge_sharing_sessions: 4, pct_employees_access_kms: 20, freq_updates_kms: "Quarterly" },
        barrier6: { num_non_compliance_incidents: 3, pct_projects_delayed_regulatory: 40, time_to_achieve_compliance_days: 90 },
        barrier7: { num_industry_standards_adopted: 2, pct_iot_devices_conforming: 10, pct_projects_delayed_standardized_solutions: 50 },
        barrier8: { pct_internet_coverage: 70, avg_internet_speed_mbps: 20, freq_it_infrastructure_outages_per_month: 2 },
        barrier9: { pct_loan_approved: 1, pct_projects_delayed_lack_funding: 30, ratio_external_funding_total_project_costs_pct: 15 },
        barrier10: { yoy_revenue_growth_iot_pct: 2, profit_margin_improvement_iot_pct: 0.5, num_new_revenue_streams_iot: 0 },
        barrier11: { pct_critical_operations_reliant_vendor: 80, num_vendor_delays_disruptions_per_year: 4, cost_vendor_contracts_pct_op_expenses: 35 },
        barrier12: { pct_it_budget_allocated_iot: 50, annual_maintenance_costs_pct_op_costs: 3, integration_costs_pct_total_project_cost: 40 },
        barrier13: { num_regulatory_violations_penalties: 2, pct_compliance_audits_passed_without_issues: 60, freq_updates_internal_policies: "Bi-Annually" },
        barrier14: { pct_standards_compliant_iot_devices: 30, num_industry_specific_guidelines_implemented: 2 },
        barrier15: { pct_customers_refuse_data: 40, num_customer_complaints_data_sharing: 15, pct_customer_contracts_explicit_data_sharing: 20 },
      },
      cost_factor_inputs: {
        aftermarket_services_warranty: 0.01, depreciation: 0.04, labour: 0.13,
        maintenance_repair: 0.035, raw_materials_consumables: 0.42, rental_operating_lease: 0.02,
        research_development: 0.015, selling_general_administrative_expense: 0.07, utilities: 0.06,
        earnings_before_interest_taxes_ebit: 0.08, financing_costs_interest: 0.01,
        taxation_compliance_costs: 0.0175, supply_chain_logistics_costs: 0.05,
        technology_digital_infrastructure_costs: 0.015, training_skill_development_costs: 0.005,
        regulatory_compliance_costs: 0.005, insurance_costs: 0.005,
        marketing_customer_acquisition_costs: 0.02, environmental_social_responsibility_costs: 0.005,
        quality_control_assurance: 0.01,
      },
      kpi_factor_inputs: {
        asset_equipment_efficiency: 0, utilities_efficiency: 1, inventory_efficiency: 0,
        process_quality: 1, product_quality: 0, safety_security: 0,
        planning_scheduling_effectiveness: 1, time_to_market: 0, production_flexibility: 1,
        customer_satisfaction: 0, supply_chain_efficiency: 1, market_share_growth: 0,
        employee_productivity: 1, return_on_investment_roi: 0, financial_health_and_stability: 0,
        talent_retention: 0, customer_retention_rate: 0,
      },
    })
    toast({ title: "Sample Data Loaded", description: "Form populated with test data for XYZ company." })
  }

  const handleExcelUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    e.target.value = ""
    setIsUploading(true)
    try {
      const { data, warnings } = await parseExcelTemplate(file)
      setFormData(data)
      if (warnings.length > 0) {
        toast({ title: "Uploaded with Warnings", description: warnings.join(" | "), variant: "destructive" })
      } else {
        toast({ title: "Excel Uploaded", description: "All fields populated. Review each step before submitting." })
      }
      setCurrentStep(0)
    } catch (err) {
      toast({ title: "Upload Failed", description: "Could not read the file. Use the official IoT Assessment Template.", variant: "destructive" })
    } finally {
      setIsUploading(false)
    }
  }

  const updateFormData = (section: keyof FormData, data: any) => {
    const clamp = (n: number) => { if (Number.isNaN(n)) return 0; return Math.min(1000, Math.max(0, n)) }
    const processed: any = Array.isArray(data) ? [...data] : { ...data }
    Object.keys(processed).forEach((k) => {
      const v = processed[k]
      if (typeof v === "number") processed[k] = clamp(v)
      else if (v && typeof v === "object" && !Array.isArray(v)) {
        processed[k] = { ...v }
        Object.keys(processed[k]).forEach((ik) => {
          if (typeof processed[k][ik] === "number") processed[k][ik] = clamp(processed[k][ik])
        })
      }
    })
    setFormData((prev) => ({ ...prev, [section]: { ...prev[section], ...processed } }))
  }

  const handleSubmit = async () => {
    setIsSubmitting(true)
    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_URL || ""
      const endpoint = API_BASE ? `${API_BASE}/generate_report_async` : "/api/generate-report"
      const apiPayload = API_BASE ? {
        company_details: formData.company_details,
        barrier1: formData.barriers.barrier1,   barrier2: formData.barriers.barrier2,
        barrier3: formData.barriers.barrier3,   barrier4: formData.barriers.barrier4,
        barrier5: formData.barriers.barrier5,   barrier6: formData.barriers.barrier6,
        barrier7: formData.barriers.barrier7,   barrier8: formData.barriers.barrier8,
        barrier9: formData.barriers.barrier9,   barrier10: formData.barriers.barrier10,
        barrier11: formData.barriers.barrier11, barrier12: formData.barriers.barrier12,
        barrier13: formData.barriers.barrier13, barrier14: formData.barriers.barrier14,
        barrier15: formData.barriers.barrier15,
        cost_factor_inputs: formData.cost_factor_inputs,
        kpi_factor_inputs: formData.kpi_factor_inputs,
      } : formData
      localStorage.setItem("isri_last_payload", JSON.stringify(apiPayload))
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(apiPayload),
      })
      if (!response.ok) throw new Error("Failed to start report generation")
      const result = await response.json()
      window.location.href = `/loading?session=${result.session_id}`
    } catch (error) {
      toast({ title: "Error", description: "Failed to start report generation. Please try again.", variant: "destructive" })
      setIsSubmitting(false)
    }
  }

  const isStepComplete = (stepIndex: number) => {
    if (stepIndex === 0) return !!formData.company_details.company_name && !!formData.company_details.industry
    if (stepIndex === 1) return Object.values(formData.barriers).some(b => Object.keys(b).length > 0)
    if (stepIndex === 2) return Object.keys(formData.cost_factor_inputs).length > 0
    if (stepIndex === 3) return Object.keys(formData.kpi_factor_inputs).length > 0
    return false
  }

  return (
    <div className="max-w-4xl mx-auto">

      {/* ── Top toolbar ─────────────────────────────────────────────── */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-6 p-3 glass-card rounded-2xl">
        <div className="flex flex-wrap gap-2">
          <input ref={fileInputRef} type="file" accept=".xlsx,.xls" className="hidden" onChange={handleExcelUpload} />

          <a href="/IoT_Assessment_Template.xlsx" download>
            <button className="flex items-center gap-1.5 h-8 px-3 text-xs rounded-lg border border-border hover:border-primary/30 bg-muted/30 hover:bg-muted/60 text-muted-foreground hover:text-foreground transition-all">
              <FileSpreadsheet className="h-3.5 w-3.5" />
              Download Template
            </button>
          </a>

          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="flex items-center gap-1.5 h-8 px-3 text-xs rounded-lg border border-border hover:border-primary/30 bg-muted/30 hover:bg-muted/60 text-muted-foreground hover:text-foreground transition-all disabled:opacity-50"
          >
            {isUploading ? (
              <><div className="animate-spin rounded-full h-3 w-3 border-b-2 border-primary" /> Uploading…</>
            ) : (
              <><Upload className="h-3.5 w-3.5" /> Upload Excel</>
            )}
          </button>

          <button
            onClick={fillSampleData}
            className="flex items-center gap-1.5 h-8 px-3 text-xs rounded-lg border border-primary/20 bg-primary/5 hover:bg-primary/10 text-primary transition-all"
          >
            <Zap className="h-3.5 w-3.5" />
            Sample Data
          </button>
        </div>

        <span className="mono text-[10px] text-muted-foreground/60 tracking-wider">
          {currentStep + 1} / {steps.length}
        </span>
      </div>

      {/* ── Step indicator ───────────────────────────────────────────── */}
      <div className="flex items-start mb-8">
        {steps.map((step, index) => {
          const done = index < currentStep || isStepComplete(index)
          const active = index === currentStep
          return (
            <div key={step.id} className="flex items-start flex-1 min-w-0">
              <button
                onClick={() => index < currentStep && setCurrentStep(index)}
                className={cn(
                  "flex flex-col items-center gap-1.5 flex-shrink-0 w-10",
                  index < currentStep ? "cursor-pointer" : "cursor-default"
                )}
              >
                <div className={cn(
                  "w-7 h-7 rounded-full flex items-center justify-center text-[11px] font-bold border-2 transition-all duration-300 flex-shrink-0",
                  active && "bg-primary border-primary text-primary-foreground shadow-lg shadow-primary/30",
                  done && !active && "bg-secondary/20 border-secondary text-secondary",
                  !active && !done && "bg-muted border-border/60 text-muted-foreground"
                )}>
                  {done && !active ? <Check className="h-3 w-3" /> : <span>{index + 1}</span>}
                </div>
                <span className={cn(
                  "hidden sm:block text-[10px] font-medium leading-tight text-center w-full transition-colors tracking-wide",
                  active ? "text-primary" : done ? "text-secondary" : "text-muted-foreground/50"
                )}>
                  {step.title}
                </span>
              </button>

              {index < steps.length - 1 && (
                <div className={cn(
                  "flex-1 h-px mt-[13px] mx-1 rounded-full transition-colors duration-300",
                  index < currentStep ? "bg-secondary/40" : "bg-border/40"
                )} />
              )}
            </div>
          )
        })}
      </div>

      {/* ── Step title ───────────────────────────────────────────────── */}
      <div className="mb-5">
        <h2 className="font-serif font-bold text-xl text-foreground">{steps[currentStep].title}</h2>
        <p className="text-xs text-muted-foreground mt-0.5 tracking-wide">{steps[currentStep].description}</p>
      </div>

      {/* ── Step content ─────────────────────────────────────────────── */}
      <div className="glass-card rounded-2xl overflow-hidden mb-6">
        <div className="p-5 sm:p-7">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentStep}
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -14 }}
              transition={{ duration: 0.22 }}
            >
              {currentStep === 0 && <CompanyDetailsStep data={formData.company_details} onChange={(d) => updateFormData("company_details", d)} />}
              {currentStep === 1 && <BarriersStep data={formData.barriers} onChange={(d) => updateFormData("barriers", d)} />}
              {currentStep === 2 && <CostFactorsStep data={formData.cost_factor_inputs} onChange={(d) => updateFormData("cost_factor_inputs", d)} />}
              {currentStep === 3 && <KPIFactorsStep data={formData.kpi_factor_inputs} onChange={(d) => updateFormData("kpi_factor_inputs", d)} />}
              {currentStep === 4 && <ReviewStep data={formData} onSubmit={handleSubmit} isSubmitting={isSubmitting} />}
            </motion.div>
          </AnimatePresence>
        </div>
      </div>

      {/* ── Navigation ───────────────────────────────────────────────── */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => setCurrentStep(s => s - 1)}
          disabled={currentStep === 0}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl border border-border hover:border-primary/30 bg-muted/20 hover:bg-muted/40 text-muted-foreground hover:text-foreground text-sm font-medium transition-all disabled:opacity-30 disabled:cursor-not-allowed"
        >
          <ChevronLeft className="h-4 w-4" />
          Previous
        </button>

        {currentStep < steps.length - 1 ? (
          <button
            onClick={() => setCurrentStep(s => s + 1)}
            className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-primary hover:bg-primary/90 text-primary-foreground text-sm font-semibold shadow-md shadow-primary/20 hover:shadow-primary/35 transition-all"
          >
            Next
            <ChevronRight className="h-4 w-4" />
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={isSubmitting}
            className="flex items-center gap-2 px-7 py-2.5 rounded-xl bg-secondary hover:bg-secondary/90 text-secondary-foreground text-sm font-semibold shadow-md shadow-secondary/20 hover:shadow-secondary/35 transition-all min-w-[160px] justify-center disabled:opacity-50"
          >
            {isSubmitting ? (
              <><div className="animate-spin rounded-full h-4 w-4 border-b-2 border-secondary-foreground" /> Generating…</>
            ) : (
              <><Download className="h-4 w-4" /> Generate Reports</>
            )}
          </button>
        )}
      </div>
    </div>
  )
}
