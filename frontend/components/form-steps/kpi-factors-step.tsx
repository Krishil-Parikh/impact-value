"use client"

import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { BarChart3, Target, Users, TrendingUp } from "lucide-react"

interface KPIFactorsStepProps {
  data: any
  onChange: (data: any) => void
}

const kpiFactors = [
  { key: "asset_equipment_efficiency", label: "Asset & Equipment Efficiency", category: "operational" },
  { key: "utilities_efficiency", label: "Utilities Efficiency", category: "operational" },
  { key: "inventory_efficiency", label: "Inventory Efficiency", category: "operational" },
  { key: "process_quality", label: "Process Quality", category: "quality" },
  { key: "product_quality", label: "Product Quality", category: "quality" },
  { key: "safety_security", label: "Safety & Security", category: "quality" },
  { key: "planning_scheduling_effectiveness", label: "Planning & Scheduling Effectiveness", category: "operational" },
  { key: "time_to_market", label: "Time to Market", category: "performance" },
  { key: "production_flexibility", label: "Production Flexibility", category: "operational" },
  { key: "customer_satisfaction", label: "Customer Satisfaction", category: "customer" },
  { key: "supply_chain_efficiency", label: "Supply Chain Efficiency", category: "operational" },
  { key: "market_share_growth", label: "Market Share Growth", category: "performance" },
  { key: "employee_productivity", label: "Employee Productivity", category: "performance" },
  { key: "return_on_investment_roi", label: "Return on Investment (ROI)", category: "financial" },
  { key: "financial_health_and_stability", label: "Financial Health and Stability", category: "financial" },
  { key: "talent_retention", label: "Talent Retention", category: "customer" },
  { key: "customer_retention_rate", label: "Customer Retention Rate", category: "customer" },
]

const categories = {
  operational: { title: "Operational Excellence", icon: BarChart3, color: "text-chart-1" },
  quality: { title: "Quality & Safety", icon: Target, color: "text-chart-2" },
  performance: { title: "Performance Metrics", icon: TrendingUp, color: "text-chart-3" },
  financial: { title: "Financial Performance", icon: TrendingUp, color: "text-chart-4" },
  customer: { title: "Customer & People", icon: Users, color: "text-chart-5" },
}

export function KPIFactorsStep({ data, onChange }: KPIFactorsStepProps) {
  const handleChange = (field: string, value: boolean) => {
    onChange({ ...data, [field]: value ? 1 : 0 })
  }

  const getCategoryFactors = (category: string) => {
    return kpiFactors.filter((factor) => factor.category === category)
  }

  const getCompletedCount = (categoryFactors: any[]) => {
    return categoryFactors.filter((factor) => data[factor.key] !== undefined).length
  }

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-serif font-bold text-primary mb-2">KPI Factor Assessment</h2>
        <p className="text-muted-foreground">
          Indicate which KPIs your organization actively tracks and considers important for business success. This helps
          identify which barriers most impact your key performance areas.
        </p>
      </div>

      <div className="grid gap-6">
        {Object.entries(categories).map(([categoryKey, category]) => {
          const categoryFactors = getCategoryFactors(categoryKey)
          const completedCount = getCompletedCount(categoryFactors)
          const Icon = category.icon

          return (
            <Card key={categoryKey}>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Icon className={`h-5 w-5 ${category.color}`} />
                    {category.title}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {completedCount}/{categoryFactors.length} completed
                  </div>
                </CardTitle>
                <CardDescription>Toggle on the KPIs that are important to your business</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-3 sm:gap-4">
                  {categoryFactors.map((factor) => (
                    <div key={factor.key} className="flex items-center justify-between space-x-2 p-2.5 sm:p-3 rounded-lg border">
                      <Label htmlFor={factor.key} className="text-xs sm:text-sm font-medium cursor-pointer flex-1 leading-tight">
                        {factor.label}
                      </Label>
                      <Switch
                        id={factor.key}
                        checked={data[factor.key] === 1}
                        onCheckedChange={(checked) => handleChange(factor.key, checked)}
                        className="flex-shrink-0"
                      />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      <Card className="bg-muted/50">
        <CardContent className="pt-4 sm:pt-6 p-4 sm:p-6">
          <div className="flex items-start gap-2 sm:gap-3">
            <div className="bg-secondary/10 p-1.5 sm:p-2 rounded-lg flex-shrink-0">
              <Target className="h-4 w-4 sm:h-5 sm:w-5 text-secondary" />
            </div>
            <div>
              <h3 className="font-medium text-primary mb-1 text-sm sm:text-base">KPI Selection Guidelines</h3>
              <p className="text-xs sm:text-sm text-muted-foreground mb-2">
                Select KPIs that your organization actively measures and considers critical for success. You don't need
                to select all KPIs - focus on those most relevant to your business model.
              </p>
              <p className="text-xs sm:text-sm text-muted-foreground">
                The more KPIs you track in an area, the higher the potential impact of related barriers on your business
                performance.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
