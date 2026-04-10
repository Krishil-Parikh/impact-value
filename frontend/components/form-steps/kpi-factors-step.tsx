"use client"

import { Info } from "lucide-react"
import { cn } from "@/lib/utils"

interface KPIFactorsStepProps {
  data: any
  onChange: (data: any) => void
}

const kpiGroups = [
  {
    title: "Operational Excellence",
    factors: [
      { key: "asset_equipment_efficiency", label: "Asset & Equipment Efficiency" },
      { key: "utilities_efficiency", label: "Utilities Efficiency" },
      { key: "inventory_efficiency", label: "Inventory Efficiency" },
      { key: "planning_scheduling_effectiveness", label: "Planning & Scheduling Effectiveness" },
      { key: "production_flexibility", label: "Production Flexibility" },
      { key: "supply_chain_efficiency", label: "Supply Chain Efficiency" },
    ],
  },
  {
    title: "Quality & Safety",
    factors: [
      { key: "process_quality", label: "Process Quality" },
      { key: "product_quality", label: "Product Quality" },
      { key: "safety_security", label: "Safety & Security" },
    ],
  },
  {
    title: "Market & Growth",
    factors: [
      { key: "time_to_market", label: "Time to Market" },
      { key: "market_share_growth", label: "Market Share Growth" },
      { key: "employee_productivity", label: "Employee Productivity" },
    ],
  },
  {
    title: "Customer & People",
    factors: [
      { key: "customer_satisfaction", label: "Customer Satisfaction" },
      { key: "talent_retention", label: "Talent Retention" },
      { key: "customer_retention_rate", label: "Customer Retention Rate" },
    ],
  },
  {
    title: "Financial Performance",
    factors: [
      { key: "return_on_investment_roi", label: "Return on Investment (ROI)" },
      { key: "financial_health_and_stability", label: "Financial Health & Stability" },
    ],
  },
]

export function KPIFactorsStep({ data, onChange }: KPIFactorsStepProps) {
  const handleToggle = (key: string) => {
    const current = data[key] === 1
    onChange({ ...data, [key]: current ? 0 : 1 })
  }

  const totalSelected = Object.values(data).filter((v) => v === 1).length

  return (
    <div className="space-y-5">
      {/* Header info */}
      <div className="flex items-start gap-2.5 p-3.5 rounded-xl bg-primary/5 border border-primary/15">
        <Info className="h-4 w-4 text-primary flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <p className="text-xs text-primary/80 leading-relaxed">
            Select the KPIs your organisation actively tracks. The more relevant KPIs you select in an area,
            the higher the calculated impact of related barriers.
          </p>
        </div>
        <span className="text-xs font-semibold text-primary/70 whitespace-nowrap ml-2">
          {totalSelected}/17 selected
        </span>
      </div>

      {kpiGroups.map((group) => (
        <div key={group.title}>
          <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2.5">
            {group.title}
          </h3>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-2">
            {group.factors.map((factor) => {
              const isOn = data[factor.key] === 1
              return (
                <button
                  key={factor.key}
                  type="button"
                  onClick={() => handleToggle(factor.key)}
                  className={cn(
                    "flex items-center gap-2.5 px-3.5 py-2.5 rounded-xl border text-left transition-all duration-150 text-sm",
                    isOn
                      ? "bg-secondary/10 border-secondary/40 text-foreground shadow-sm"
                      : "bg-card border-border/60 text-muted-foreground hover:border-primary/30 hover:text-foreground hover:bg-muted/20"
                  )}
                >
                  <div className={cn(
                    "flex-shrink-0 w-4 h-4 rounded border-2 flex items-center justify-center transition-colors",
                    isOn ? "bg-secondary border-secondary" : "border-border"
                  )}>
                    {isOn && (
                      <svg className="h-2.5 w-2.5 text-white" fill="none" viewBox="0 0 12 12">
                        <path d="M2 6l3 3 5-5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    )}
                  </div>
                  <span className="leading-tight font-medium">{factor.label}</span>
                </button>
              )
            })}
          </div>
        </div>
      ))}
    </div>
  )
}
