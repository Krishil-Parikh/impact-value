"use client"

import { Button } from "@/components/ui/button"
import { CheckCircle2, AlertCircle, Building2, BarChart3, DollarSign, Target, Sparkles, FileText, Map, Download } from "lucide-react"
import { cn } from "@/lib/utils"
import type { FormData } from "../isri-assessment-form"

interface ReviewStepProps {
  data: FormData
  onSubmit: () => void
  isSubmitting: boolean
}

export function ReviewStep({ data, onSubmit, isSubmitting }: ReviewStepProps) {
  const completedBarriers = Object.values(data.barriers).filter((b) => b && Object.keys(b).length > 0).length
  const completedCosts = Object.keys(data.cost_factor_inputs).length
  const completedKPIs = Object.values(data.kpi_factor_inputs).filter((v) => v !== undefined).length

  const checks = [
    {
      label: "Company details",
      done: !!(data.company_details.company_name && data.company_details.industry),
      detail: data.company_details.company_name
        ? `${data.company_details.company_name} · ${data.company_details.industry}`
        : "Incomplete",
    },
    {
      label: "Barrier assessment",
      done: completedBarriers === 15,
      detail: `${completedBarriers}/15 barriers completed`,
    },
    {
      label: "Cost factors",
      done: completedCosts > 0,
      detail: `${completedCosts}/20 cost categories entered`,
    },
    {
      label: "KPI factors",
      done: completedKPIs > 0,
      detail: `${completedKPIs}/17 KPIs selected`,
    },
  ]

  const allComplete = checks.every((c) => c.done)
  const issueCount = checks.filter((c) => !c.done).length

  return (
    <div className="space-y-6">
      {/* Checklist */}
      <div className="bg-card border border-border/60 rounded-2xl overflow-hidden">
        <div className="px-5 py-4 border-b border-border/60 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-foreground">Assessment Checklist</h3>
          {allComplete
            ? <span className="text-xs text-secondary font-medium flex items-center gap-1"><CheckCircle2 className="h-3.5 w-3.5" /> All complete</span>
            : <span className="text-xs text-destructive font-medium flex items-center gap-1"><AlertCircle className="h-3.5 w-3.5" /> {issueCount} item{issueCount > 1 ? "s" : ""} incomplete</span>
          }
        </div>
        <div className="divide-y divide-border/40">
          {checks.map((check, i) => {
            const icons = [Building2, BarChart3, DollarSign, Target]
            const Icon = icons[i]
            return (
              <div key={i} className={cn(
                "flex items-center gap-3 px-5 py-3.5",
                check.done ? "" : "bg-destructive/5"
              )}>
                <Icon className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-foreground">{check.label}</div>
                  <div className={cn(
                    "text-xs mt-0.5 truncate",
                    check.done ? "text-muted-foreground" : "text-destructive/80"
                  )}>
                    {check.detail}
                  </div>
                </div>
                {check.done
                  ? <CheckCircle2 className="h-4 w-4 text-secondary flex-shrink-0" />
                  : <AlertCircle className="h-4 w-4 text-destructive flex-shrink-0" />
                }
              </div>
            )
          })}
        </div>
      </div>

      {/* Reports preview */}
      <div className="grid sm:grid-cols-2 gap-3">
        {[
          {
            icon: FileText,
            title: "Comprehensive Analysis",
            desc: "AI-generated analysis of all 15 barriers with severity levels, impact scores, and tailored recommendations.",
            accent: "primary" as const,
          },
          {
            icon: Map,
            title: "Strategic Roadmap",
            desc: "Phased 18-month implementation plan for the top 3 priority barriers with KPI targets.",
            accent: "secondary" as const,
          },
        ].map((report, i) => {
          const Icon = report.icon
          return (
            <div key={i} className={cn(
              "border rounded-xl p-4 flex items-start gap-3",
              report.accent === "primary" ? "bg-primary/5 border-primary/20" : "bg-secondary/5 border-secondary/20"
            )}>
              <div className={cn(
                "flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center",
                report.accent === "primary" ? "bg-primary/10" : "bg-secondary/10"
              )}>
                <Icon className={cn("h-4 w-4", report.accent === "primary" ? "text-primary" : "text-secondary")} />
              </div>
              <div>
                <div className="text-sm font-semibold text-foreground">{report.title}</div>
                <div className="text-xs text-muted-foreground mt-0.5 leading-relaxed">{report.desc}</div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Error message if incomplete */}
      {!allComplete && (
        <div className="flex items-start gap-2.5 p-4 rounded-xl bg-destructive/5 border border-destructive/20">
          <AlertCircle className="h-4 w-4 text-destructive flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-destructive mb-1">Please complete all sections before generating</p>
            <ul className="text-xs text-destructive/80 space-y-0.5">
              {!checks[0].done && <li>Company name and industry are required</li>}
              {!checks[1].done && <li>Complete all 15 barrier assessments</li>}
              {!checks[2].done && <li>Enter at least one cost factor</li>}
              {!checks[3].done && <li>Select at least one KPI factor</li>}
            </ul>
          </div>
        </div>
      )}

      {/* Generate button */}
      <Button
        onClick={onSubmit}
        disabled={!allComplete || isSubmitting}
        className="w-full py-6 text-base gap-2.5 bg-secondary hover:bg-secondary/90"
      >
        {isSubmitting ? (
          <>
            <Sparkles className="h-5 w-5 animate-pulse" />
            Generating your reports...
          </>
        ) : (
          <>
            <Download className="h-5 w-5" />
            Generate ISRI Assessment Reports
          </>
        )}
      </Button>

      <p className="text-center text-xs text-muted-foreground">
        Report generation takes 2–4 minutes. Keep this tab open.
      </p>
    </div>
  )
}
