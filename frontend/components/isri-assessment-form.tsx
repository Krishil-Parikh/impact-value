"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { CompanyDetailsStep } from "./form-steps/company-details-step"
import { BarriersStep } from "./form-steps/barriers-step"
import { CostFactorsStep } from "./form-steps/cost-factors-step"
import { KPIFactorsStep } from "./form-steps/kpi-factors-step"
import { ReviewStep } from "./form-steps/review-step"
import { ChevronLeft, ChevronRight, Download, Zap } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

export interface FormData {
  company_details: {
    company_name: string
    industry: string
    num_employees: number
    annual_revenue: number
  }
  barriers: {
    barrier1: any
    barrier2: any
    barrier3: any
    barrier4: any
    barrier5: any
    barrier6: any
    barrier7: any
    barrier8: any
    barrier9: any
    barrier10: any
    barrier11: any
    barrier12: any
    barrier13: any
    barrier14: any
    barrier15: any
  }
  cost_factor_inputs: any
  kpi_factor_inputs: any
}

const steps = [
  { id: "company", title: "Company Details", description: "Basic information about your organization" },
  { id: "barriers", title: "Barrier Assessment", description: "Evaluate 15 key barriers to IoT adoption" },
  { id: "costs", title: "Cost Factors", description: "Analyze your cost structure and financial metrics" },
  { id: "kpis", title: "KPI Factors", description: "Assess key performance indicators" },
  { id: "review", title: "Review & Submit", description: "Review your inputs and generate reports" },
]

export function ISRIAssessmentForm() {
  const [currentStep, setCurrentStep] = useState(0)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { toast } = useToast()

  const [formData, setFormData] = useState<FormData>({
    company_details: {
      company_name: "",
      industry: "",
      num_employees: 0,
      annual_revenue: 0,
    },
    barriers: {
      barrier1: {},
      barrier2: {},
      barrier3: {},
      barrier4: {},
      barrier5: {},
      barrier6: {},
      barrier7: {},
      barrier8: {},
      barrier9: {},
      barrier10: {},
      barrier11: {},
      barrier12: {},
      barrier13: {},
      barrier14: {},
      barrier15: {},
    },
    cost_factor_inputs: {},
    kpi_factor_inputs: {},
  })

  const fillSampleData = () => {
    setFormData({
      company_details: {
        company_name: "XYZ",
        industry: "Behh",
        num_employees: 1000,
        annual_revenue: 100000,
      },
      barriers: {
        barrier1: {
          num_training_programs: 1,
          pct_employees_trained: 9,
          pct_budget_training_of_payroll: 2.272727273,
        },
        barrier2: {
          employee_turnover_rate_pct: 15,
          pct_employees_resisting: 40,
          num_feedback_sessions: 2,
        },
        barrier3: {
          num_digital_skills_workshops: 1,
          pct_comfortable_digital_tools: 28,
          adoption_rate_new_digital_tools_pct: 25,
        },
        barrier4: {
          pct_training_expenditure_of_op_costs: 1.25,
          avg_training_hours_per_employee: 20,
          roi_training_programs_pct: 5,
        },
        barrier5: {
          num_knowledge_sharing_sessions: 4,
          pct_employees_access_kms: 20,
          freq_updates_kms: "Quarterly",
        },
        barrier6: {
          num_non_compliance_incidents: 3,
          pct_projects_delayed_regulatory: 40,
          time_to_achieve_compliance_days: 90,
        },
        barrier7: {
          num_industry_standards_adopted: 2,
          pct_iot_devices_conforming: 10,
          pct_projects_delayed_standardized_solutions: 50,
        },
        barrier8: {
          pct_internet_coverage: 70,
          avg_internet_speed_mbps: 20,
          freq_it_infrastructure_outages_per_month: 2,
        },
        barrier9: {
          pct_loan_approved: 1,
          pct_projects_delayed_lack_funding: 30,
          ratio_external_funding_total_project_costs_pct: 15,
        },
        barrier10: {
          yoy_revenue_growth_iot_pct: 2,
          profit_margin_improvement_iot_pct: 0.5,
          num_new_revenue_streams_iot: 0,
        },
        barrier11: {
          pct_critical_operations_reliant_vendor: 80,
          num_vendor_delays_disruptions_per_year: 4,
          cost_vendor_contracts_pct_op_expenses: 35,
        },
        barrier12: {
          pct_it_budget_allocated_iot: 50,
          annual_maintenance_costs_pct_op_costs: 3,
          integration_costs_pct_total_project_cost: 40,
        },
        barrier13: {
          num_regulatory_violations_penalties: 2,
          pct_compliance_audits_passed_without_issues: 60,
          freq_updates_internal_policies: "Bi-Annually",
        },
        barrier14: {
          pct_standards_compliant_iot_devices: 30,
          num_industry_specific_guidelines_implemented: 2,
        },
        barrier15: {
          pct_customers_refuse_data: 40,
          num_customer_complaints_data_sharing: 15,
          pct_customer_contracts_explicit_data_sharing: 20,
        },
      },
      cost_factor_inputs: {
        aftermarket_services_warranty: 0.01,
        depreciation: 0.04,
        labour: 0.13,
        maintenance_repair: 0.035,
        raw_materials_consumables: 0.42,
        rental_operating_lease: 0.02,
        research_development: 0.015,
        selling_general_administrative_expense: 0.07,
        utilities: 0.06,
        earnings_before_interest_taxes_ebit: 0.08,
        financing_costs_interest: 0.01,
        taxation_compliance_costs: 0.0175,
        supply_chain_logistics_costs: 0.05,
        technology_digital_infrastructure_costs: 0.015,
        training_skill_development_costs: 0.005,
        regulatory_compliance_costs: 0.005,
        insurance_costs: 0.005,
        marketing_customer_acquisition_costs: 0.02,
        environmental_social_responsibility_costs: 0.005,
        quality_control_assurance: 0.01,
      },
      kpi_factor_inputs: {
        asset_equipment_efficiency: 0,
        utilities_efficiency: 1,
        inventory_efficiency: 0,
        process_quality: 1,
        product_quality: 0,
        safety_security: 0,
        planning_scheduling_effectiveness: 1,
        time_to_market: 0,
        production_flexibility: 1,
        customer_satisfaction: 0,
        supply_chain_efficiency: 1,
        market_share_growth: 0,
        employee_productivity: 1,
        return_on_investment_roi: 0,
        financial_health_and_stability: 0,
        talent_retention: 0,
        customer_retention_rate: 0,
      },
    })

    toast({
      title: "Sample Data Loaded",
      description: "Form has been populated with the provided test data for XYZ company.",
    })
  }

  const updateFormData = (section: keyof FormData, data: any) => {
    setFormData((prev) => ({
      ...prev,
      [section]: { ...prev[section], ...data },
    }))
  }

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1)
    }
  }

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleSubmit = async () => {
    setIsSubmitting(true)
    try {
      const response = await fetch("/api/generate-report", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      })

      if (!response.ok) {
        throw new Error("Failed to generate report")
      }

      // Handle ZIP file download
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.style.display = "none"
      a.href = url
      a.download = "ISRI_AI_Reports.zip"
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      toast({
        title: "Reports Generated Successfully",
        description: "Your ISRI assessment reports have been downloaded as a ZIP file.",
      })
    } catch (error) {
      console.error("Error generating report:", error)
      toast({
        title: "Error",
        description: "Failed to generate reports. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const progress = ((currentStep + 1) / steps.length) * 100

  return (
    <div className="max-w-4xl mx-auto">
      {/* Progress Header */}
      <Card className="mb-8">
        <CardHeader>
          <div className="flex items-center justify-between mb-4">
            <div>
              <CardTitle className="font-serif text-2xl text-primary">{steps[currentStep].title}</CardTitle>
              <CardDescription className="text-base">{steps[currentStep].description}</CardDescription>
            </div>
            <div className="flex items-center gap-4">
              <Button
                variant="outline"
                onClick={fillSampleData}
                className="flex items-center gap-2 text-sm bg-transparent"
              >
                <Zap className="h-4 w-4" />
                Fill Sample Data
              </Button>
              <div className="text-right">
                <div className="text-sm text-muted-foreground mb-2">
                  Step {currentStep + 1} of {steps.length}
                </div>
                <Progress value={progress} className="w-32" />
              </div>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Step Content */}
      <Card className="mb-8">
        <CardContent className="p-8">
          {currentStep === 0 && (
            <CompanyDetailsStep
              data={formData.company_details}
              onChange={(data) => updateFormData("company_details", data)}
            />
          )}
          {currentStep === 1 && (
            <BarriersStep data={formData.barriers} onChange={(data) => updateFormData("barriers", data)} />
          )}
          {currentStep === 2 && (
            <CostFactorsStep
              data={formData.cost_factor_inputs}
              onChange={(data) => updateFormData("cost_factor_inputs", data)}
            />
          )}
          {currentStep === 3 && (
            <KPIFactorsStep
              data={formData.kpi_factor_inputs}
              onChange={(data) => updateFormData("kpi_factor_inputs", data)}
            />
          )}
          {currentStep === 4 && <ReviewStep data={formData} onSubmit={handleSubmit} isSubmitting={isSubmitting} />}
        </CardContent>
      </Card>

      {/* Navigation */}
      <div className="flex justify-between items-center">
        <Button
          variant="outline"
          onClick={handlePrevious}
          disabled={currentStep === 0}
          className="flex items-center gap-2 bg-transparent"
        >
          <ChevronLeft className="h-4 w-4" />
          Previous
        </Button>

        <div className="flex gap-2">
          {steps.map((_, index) => (
            <div
              key={index}
              className={`w-3 h-3 rounded-full transition-colors ${index <= currentStep ? "bg-secondary" : "bg-muted"}`}
            />
          ))}
        </div>

        {currentStep < steps.length - 1 ? (
          <Button onClick={handleNext} className="flex items-center gap-2 bg-secondary hover:bg-secondary/90">
            Next
            <ChevronRight className="h-4 w-4" />
          </Button>
        ) : (
          <Button
            onClick={handleSubmit}
            disabled={isSubmitting}
            className="flex items-center gap-2 bg-secondary hover:bg-secondary/90"
          >
            {isSubmitting ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Generating Reports...
              </>
            ) : (
              <>
                <Download className="h-4 w-4" />
                Generate Reports
              </>
            )}
          </Button>
        )}
      </div>
    </div>
  )
}
