"use client"

import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Info } from "lucide-react"
import { cn } from "@/lib/utils"

interface CostFactorsStepProps {
  data: any
  onChange: (data: any) => void
}

const costFactorGroups = [
  {
    title: "Operational Costs",
    color: "text-blue-600",
    factors: [
      { key: "labour", label: "Labour" },
      { key: "raw_materials_consumables", label: "Raw Materials & Consumables" },
      { key: "maintenance_repair", label: "Maintenance & Repair" },
      { key: "utilities", label: "Utilities" },
      { key: "supply_chain_logistics_costs", label: "Supply Chain & Logistics" },
      { key: "quality_control_assurance", label: "Quality Control & Assurance" },
      { key: "rental_operating_lease", label: "Rental & Operating Lease" },
      { key: "selling_general_administrative_expense", label: "Selling, General & Administrative" },
    ],
  },
  {
    title: "Financial & Compliance",
    color: "text-emerald-600",
    factors: [
      { key: "earnings_before_interest_taxes_ebit", label: "EBIT" },
      { key: "financing_costs_interest", label: "Financing Costs (Interest)" },
      { key: "taxation_compliance_costs", label: "Taxation & Compliance" },
      { key: "regulatory_compliance_costs", label: "Regulatory Compliance" },
      { key: "insurance_costs", label: "Insurance" },
      { key: "depreciation", label: "Depreciation" },
      { key: "aftermarket_services_warranty", label: "Aftermarket Services / Warranty" },
    ],
  },
  {
    title: "Strategic Investments",
    color: "text-violet-600",
    factors: [
      { key: "research_development", label: "Research & Development (R&D)" },
      { key: "technology_digital_infrastructure_costs", label: "Technology & Digital Infrastructure" },
      { key: "training_skill_development_costs", label: "Training & Skill Development" },
      { key: "marketing_customer_acquisition_costs", label: "Marketing & Customer Acquisition" },
      { key: "environmental_social_responsibility_costs", label: "Environmental & Social Responsibility" },
    ],
  },
]

export function CostFactorsStep({ data, onChange }: CostFactorsStepProps) {
  const clamp = (n: number) => {
    if (Number.isNaN(n)) return 0
    return Math.min(1000, Math.max(0, n))
  }

  const handleChange = (field: string, value: number) => {
    onChange({ ...data, [field]: clamp(value) })
  }

  return (
    <div className="space-y-6">
      {/* Instruction banner */}
      <div className="flex items-start gap-2.5 p-3.5 rounded-xl bg-primary/5 border border-primary/15">
        <Info className="h-4 w-4 text-primary flex-shrink-0 mt-0.5" />
        <p className="text-xs text-primary/80 leading-relaxed">
          Enter each category as a <strong>decimal fraction of annual revenue</strong> (not a percentage).
          For example, if labour costs are 13% of revenue, enter <strong>0.13</strong>.
        </p>
      </div>

      {costFactorGroups.map((group) => (
        <div key={group.title}>
          <h3 className={cn("text-xs font-semibold uppercase tracking-wider mb-3", group.color)}>
            {group.title}
          </h3>
          <div className="grid sm:grid-cols-2 gap-3">
            {group.factors.map((factor) => (
              <div key={factor.key} className="space-y-1">
                <Label htmlFor={factor.key} className="text-sm text-foreground/90">
                  {factor.label}
                </Label>
                <div className="relative">
                  <Input
                    id={factor.key}
                    type="number"
                    step="0.001"
                    min={0}
                    max={1000}
                    value={data[factor.key] ?? ""}
                    onChange={(e) => handleChange(factor.key, parseFloat(e.target.value) || 0)}
                    placeholder="e.g., 0.13"
                    className="pr-16"
                  />
                  <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-muted-foreground pointer-events-none">
                    fraction
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
