"use client"

import { useState } from "react"
import { BarrierForm } from "./barrier-form"
import { cn } from "@/lib/utils"
import { CheckCircle2, ChevronDown } from "lucide-react"

interface BarriersStepProps {
  data: any
  onChange: (data: any) => void
}

const barrierCategories = [
  {
    id: "human-capital",
    title: "Human Capital",
    description: "Training, skills & workforce",
    barriers: [
      { key: "barrier1", title: "Lack of training for workers and managers" },
      { key: "barrier2", title: "Resistance to change" },
      { key: "barrier3", title: "Lack of digital culture and training" },
      { key: "barrier4", title: "Higher investment in employees' training" },
      { key: "barrier5", title: "Lack of knowledge management systems" },
    ],
  },
  {
    id: "regulatory-standards",
    title: "Regulatory",
    description: "Compliance and standardisation",
    barriers: [
      { key: "barrier6", title: "Regulatory compliance issues" },
      { key: "barrier7", title: "Lack of standards and reference architecture" },
      { key: "barrier13", title: "Compliance with sector-specific regulations" },
      { key: "barrier14", title: "Lack of regulations and standards" },
    ],
  },
  {
    id: "infrastructure-financial",
    title: "Infrastructure",
    description: "Technology and funding",
    barriers: [
      { key: "barrier8", title: "Lack of internet coverage and IT facilities" },
      { key: "barrier9", title: "Limited access to funding and credit" },
      { key: "barrier10", title: "Future viability and profitability" },
      { key: "barrier12", title: "High implementation cost" },
    ],
  },
  {
    id: "operational",
    title: "Operational",
    description: "Vendor & customer relations",
    barriers: [
      { key: "barrier11", title: "Dependency on external vendors" },
      { key: "barrier15", title: "Customers hesitant to share data" },
    ],
  },
]

export function BarriersStep({ data, onChange }: BarriersStepProps) {
  const [activeCategory, setActiveCategory] = useState("human-capital")
  const [expandedBarrier, setExpandedBarrier] = useState<string | null>(null)

  const updateBarrierData = (barrierKey: string, barrierData: any) => {
    onChange({ [barrierKey]: barrierData })
  }

  const isBarrierComplete = (barrierKey: string) => {
    const d = data[barrierKey]
    return d && Object.keys(d).length > 0
  }

  const getCategoryProgress = (barriers: { key: string }[]) => {
    return barriers.filter((b) => isBarrierComplete(b.key)).length
  }

  const activeBarriers = barrierCategories.find((c) => c.id === activeCategory)?.barriers ?? []

  const totalCompleted = barrierCategories.reduce((acc, cat) => acc + getCategoryProgress(cat.barriers), 0)
  const totalBarriers = 15

  return (
    <div className="space-y-5">
      {/* Overall progress */}
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs text-muted-foreground">
          <span className="mono text-foreground font-semibold">{totalCompleted}</span>/{totalBarriers} barriers filled
        </span>
        <span className="text-xs text-muted-foreground mono">{Math.round((totalCompleted / totalBarriers) * 100)}%</span>
      </div>
      <div className="h-1 bg-muted rounded-full overflow-hidden -mt-1 mb-3">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{
            width: `${(totalCompleted / totalBarriers) * 100}%`,
            background: "linear-gradient(90deg, #1D4ED8, #059669)",
          }}
        />
      </div>

      {/* Category tabs */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        {barrierCategories.map((cat) => {
          const completed = getCategoryProgress(cat.barriers)
          const total = cat.barriers.length
          const isActive = activeCategory === cat.id
          const allDone = completed === total

          return (
            <button
              key={cat.id}
              onClick={() => {
                setActiveCategory(cat.id)
                setExpandedBarrier(null)
              }}
              className={cn(
                "flex flex-col items-start gap-1 rounded-xl border p-3 text-left transition-all duration-200",
                isActive
                  ? "bg-primary/10 border-primary/40 shadow-sm shadow-primary/10"
                  : allDone
                    ? "border-secondary/25 bg-secondary/5 hover:border-secondary/40"
                    : "border-border/50 bg-muted/15 hover:border-border hover:bg-muted/30"
              )}
            >
              <div className="flex items-center justify-between w-full">
                <span className={cn(
                  "text-xs font-semibold leading-tight",
                  isActive ? "text-primary" : allDone ? "text-secondary" : "text-foreground/70"
                )}>
                  {cat.title}
                </span>
                <span className={cn(
                  "text-[10px] font-semibold rounded-full px-1.5 py-0.5 ml-1 mono",
                  isActive
                    ? "bg-primary/15 text-primary"
                    : allDone
                      ? "bg-secondary/15 text-secondary"
                      : "bg-muted text-muted-foreground"
                )}>
                  {completed}/{total}
                </span>
              </div>
              <span className={cn(
                "text-[10px] leading-tight hidden sm:block",
                isActive ? "text-primary/60" : "text-muted-foreground/60"
              )}>
                {cat.description}
              </span>
            </button>
          )
        })}
      </div>

      {/* Barrier list */}
      <div className="space-y-2">
        {activeBarriers.map((barrier) => {
          const done = isBarrierComplete(barrier.key)
          const isExpanded = expandedBarrier === barrier.key

          return (
            <div
              key={barrier.key}
              className={cn(
                "rounded-xl border overflow-hidden transition-all duration-200",
                done
                  ? "border-secondary/25 bg-secondary/5"
                  : isExpanded
                    ? "border-primary/30 bg-primary/5"
                    : "border-border/40 bg-muted/10 hover:border-border/70"
              )}
            >
              <button
                className="w-full flex items-center justify-between gap-3 px-4 py-3.5 text-left transition-colors hover:bg-white/[0.02]"
                onClick={() => setExpandedBarrier(isExpanded ? null : barrier.key)}
              >
                <div className="flex items-center gap-3 min-w-0">
                  {done ? (
                    <div className="w-5 h-5 rounded-full bg-secondary/15 border border-secondary/30 flex items-center justify-center flex-shrink-0">
                      <CheckCircle2 className="h-3 w-3 text-secondary" />
                    </div>
                  ) : (
                    <div className={cn(
                      "w-5 h-5 rounded-full border-2 flex-shrink-0 transition-colors",
                      isExpanded ? "border-primary/50" : "border-border/50"
                    )} />
                  )}
                  <span className="text-sm font-medium text-foreground/80 truncate">{barrier.title}</span>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  {done && (
                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full badge-green">Done</span>
                  )}
                  <ChevronDown className={cn(
                    "h-4 w-4 text-muted-foreground/50 transition-transform duration-200",
                    isExpanded && "rotate-180"
                  )} />
                </div>
              </button>

              {isExpanded && (
                <div className="px-4 pb-5 pt-2 border-t border-border/20">
                  <BarrierForm
                    barrierKey={barrier.key}
                    data={data[barrier.key] || {}}
                    onChange={(d) => updateBarrierData(barrier.key, d)}
                  />
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
