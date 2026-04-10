"use client"

import { Building2, Users, IndianRupee, Factory, ShieldCheck, Info } from "lucide-react"
import { cn } from "@/lib/utils"

interface CompanyDetailsStepProps {
  data: {
    company_name: string
    industry: string
    num_employees: number
    annual_revenue: number
  }
  onChange: (data: any) => void
}

export function CompanyDetailsStep({ data, onChange }: CompanyDetailsStepProps) {
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

  const textFields = [
    {
      id: "company_name",
      label: "Company Name",
      icon: Building2,
      type: "text" as const,
      placeholder: "e.g., Acme Manufacturing Pvt. Ltd.",
      value: data.company_name,
      onChange: (v: string) => handleChange("company_name", v),
      required: true,
    },
    {
      id: "industry",
      label: "Industry / Sector",
      icon: Factory,
      type: "text" as const,
      placeholder: "e.g., Automotive, Textiles, Plastics",
      value: data.industry,
      onChange: (v: string) => handleChange("industry", v),
      required: true,
    },
  ]

  const numericFields = [
    {
      id: "num_employees",
      label: "Number of Employees",
      icon: Users,
      placeholder: "Total headcount",
      value: data.num_employees,
      onChange: (v: string) => handleChange("num_employees", parseInt(v) || 0),
      suffix: "people",
      required: true,
    },
    {
      id: "annual_revenue",
      label: "Annual Revenue",
      icon: IndianRupee,
      placeholder: "e.g., 3.5",
      value: data.annual_revenue,
      onChange: (v: string) => handleChange("annual_revenue", parseFloat(v) || 0),
      suffix: "Cr (INR)",
      step: "0.01",
      required: true,
    },
  ]

  return (
    <div className="space-y-6">
      <div className="grid sm:grid-cols-2 gap-4">
        {/* Text fields */}
        {textFields.map((field) => {
          const Icon = field.icon
          const filled = !!field.value
          return (
            <div key={field.id} className="space-y-2">
              <label htmlFor={field.id} className="flex items-center gap-1.5 text-xs font-semibold text-muted-foreground tracking-wide uppercase">
                <Icon className="h-3.5 w-3.5" />
                {field.label}
                {field.required && <span className="text-destructive ml-0.5">*</span>}
              </label>
              <div className={cn(
                "relative rounded-xl border transition-all duration-200",
                filled
                  ? "border-primary/30 bg-primary/5"
                  : "border-border/60 bg-muted/20 hover:border-border"
              )}>
                <input
                  id={field.id}
                  type="text"
                  value={field.value}
                  onChange={(e) => field.onChange(e.target.value)}
                  placeholder={field.placeholder}
                  className="w-full bg-transparent px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground/40 focus:outline-none focus:ring-0"
                />
                {filled && (
                  <div className="absolute right-3 top-1/2 -translate-y-1/2 w-1.5 h-1.5 rounded-full bg-primary/60" />
                )}
              </div>
            </div>
          )
        })}

        {/* Numeric fields */}
        {numericFields.map((field) => {
          const Icon = field.icon
          const filled = field.value > 0
          return (
            <div key={field.id} className="space-y-2">
              <label htmlFor={field.id} className="flex items-center gap-1.5 text-xs font-semibold text-muted-foreground tracking-wide uppercase">
                <Icon className="h-3.5 w-3.5" />
                {field.label}
                {field.required && <span className="text-destructive ml-0.5">*</span>}
              </label>
              <div className={cn(
                "relative rounded-xl border transition-all duration-200 flex items-center",
                filled
                  ? "border-primary/30 bg-primary/5"
                  : "border-border/60 bg-muted/20 hover:border-border"
              )}>
                <input
                  id={field.id}
                  type="number"
                  value={field.value || ""}
                  onChange={(e) => field.onChange(e.target.value)}
                  placeholder={field.placeholder}
                  step={field.step ?? "1"}
                  min={0}
                  className="flex-1 bg-transparent px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground/40 focus:outline-none focus:ring-0 mono"
                />
                <span className="pr-3 text-xs text-muted-foreground/60 whitespace-nowrap flex-shrink-0">
                  {field.suffix}
                </span>
              </div>
            </div>
          )
        })}
      </div>

      {/* Privacy note */}
      <div className="flex items-start gap-3 p-4 rounded-xl border border-border/40 bg-muted/15">
        <ShieldCheck className="h-4 w-4 text-secondary flex-shrink-0 mt-0.5" />
        <p className="text-xs text-muted-foreground leading-relaxed">
          Your data is used solely to generate your IoT readiness report. We do not store or share your
          information with any third parties.
        </p>
      </div>

      {/* Tips */}
      <div className="flex items-start gap-3 p-4 rounded-xl border border-primary/10 bg-primary/5">
        <Info className="h-4 w-4 text-primary/60 flex-shrink-0 mt-0.5" />
        <p className="text-xs text-muted-foreground leading-relaxed">
          <span className="text-primary/80 font-semibold">Tip:</span> Use the{" "}
          <span className="text-foreground/70">Download Template</span> button above to get the Excel template,
          fill it in offline, then upload it to auto-populate all sections.
        </p>
      </div>
    </div>
  )
}
