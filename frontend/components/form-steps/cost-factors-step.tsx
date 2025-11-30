"use client"

import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { DollarSign, TrendingUp, Calculator } from "lucide-react"

interface CostFactorsStepProps {
  data: any
  onChange: (data: any) => void
}

const costFactors = [
  { key: "aftermarket_services_warranty", label: "Aftermarket Services / Warranty", category: "revenue" },
  { key: "depreciation", label: "Depreciation", category: "revenue" },
  { key: "labour", label: "Labour", category: "operational" },
  { key: "maintenance_repair", label: "Maintenance & Repair", category: "operational" },
  { key: "raw_materials_consumables", label: "Raw Materials & Consumables", category: "operational" },
  { key: "rental_operating_lease", label: "Rental & Operating Lease", category: "operational" },
  { key: "research_development", label: "Research & Development (R&D)", category: "strategic" },
  {
    key: "selling_general_administrative_expense",
    label: "Selling, General & Administrative Expense",
    category: "operational",
  },
  { key: "utilities", label: "Utilities", category: "operational" },
  {
    key: "earnings_before_interest_taxes_ebit",
    label: "Earnings Before Interest & Taxes (EBIT)",
    category: "financial",
  },
  { key: "financing_costs_interest", label: "Financing Costs (Interest)", category: "financial" },
  { key: "taxation_compliance_costs", label: "Taxation and Compliance Costs", category: "financial" },
  { key: "supply_chain_logistics_costs", label: "Supply Chain and Logistics Costs", category: "operational" },
  {
    key: "technology_digital_infrastructure_costs",
    label: "Technology and Digital Infrastructure Costs",
    category: "strategic",
  },
  { key: "training_skill_development_costs", label: "Training and Skill Development Costs", category: "strategic" },
  { key: "regulatory_compliance_costs", label: "Regulatory and Compliance Costs", category: "financial" },
  { key: "insurance_costs", label: "Insurance Costs", category: "financial" },
  {
    key: "marketing_customer_acquisition_costs",
    label: "Marketing and Customer Acquisition Costs",
    category: "strategic",
  },
  {
    key: "environmental_social_responsibility_costs",
    label: "Environmental and Social Responsibility Costs",
    category: "strategic",
  },
  { key: "quality_control_assurance", label: "Quality Control and Assurance", category: "operational" },
]

const categories = {
  operational: { title: "Operational Costs", icon: Calculator, color: "text-chart-1" },
  strategic: { title: "Strategic Investments", icon: TrendingUp, color: "text-chart-2" },
  financial: { title: "Financial Costs", icon: DollarSign, color: "text-chart-3" },
  revenue: { title: "Revenue-Related", icon: DollarSign, color: "text-chart-4" },
}

export function CostFactorsStep({ data, onChange }: CostFactorsStepProps) {
  const clamp = (n: number) => {
    if (Number.isNaN(n)) return 0
    return Math.min(1000, Math.max(0, n))
  }

  const handleChange = (field: string, value: number) => {
    onChange({ ...data, [field]: clamp(value) })
  }

  const getCategoryFactors = (category: string) => {
    return costFactors.filter((factor) => factor.category === category)
  }

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-serif font-bold text-primary mb-2">Cost Factor Analysis</h2>
        <p className="text-muted-foreground">
          Enter each cost category as a percentage of your annual revenue. This helps assess the financial impact of IoT
          barriers.
        </p>
      </div>

      <div className="grid gap-6">
        {Object.entries(categories).map(([categoryKey, category]) => {
          const categoryFactors = getCategoryFactors(categoryKey)
          const Icon = category.icon

          return (
            <Card key={categoryKey}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Icon className={`h-5 w-5 ${category.color}`} />
                  {category.title}
                </CardTitle>
                <CardDescription>Enter values as percentage of annual revenue</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-2">
                  {categoryFactors.map((factor) => (
                    <div key={factor.key} className="space-y-2">
                      <Label htmlFor={factor.key} className="text-sm font-medium">
                        {factor.label}
                      </Label>
                      <div className="relative">
                        <Input
                          id={factor.key}
                          type="number"
                          step="0.01"
                          min={0}
                          max={1000}
                          value={data[factor.key] ?? ""}
                          onChange={(e) => handleChange(factor.key, Number.parseFloat(e.target.value) || 0)}
                          placeholder="0 - 1000"
                          className="pr-8"
                        />
                        <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground text-sm">
                          %
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      <Card className="bg-muted/50">
        <CardContent className="pt-6">
          <div className="flex items-start gap-3">
            <div className="bg-secondary/10 p-2 rounded-lg">
              <Calculator className="h-5 w-5 text-secondary" />
            </div>
            <div>
              <h3 className="font-medium text-primary mb-1">Cost Factor Guidelines</h3>
              <p className="text-sm text-muted-foreground mb-2">
                These percentages represent how much each cost category contributes to your total annual revenue. For
                example, if your labour costs are ₹10 crores and your annual revenue is ₹100 crores, enter 10%.
              </p>
              <p className="text-sm text-muted-foreground">
                Accurate cost data helps identify which barriers have the highest financial impact on your organization.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
