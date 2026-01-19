"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { BarrierForm } from "./barrier-form"

interface BarriersStepProps {
  data: any
  onChange: (data: any) => void
}

const barrierCategories = [
  {
    id: "human-capital",
    title: "Human Capital",
    description: "Training, skills, and workforce readiness",
    barriers: [
      { key: "barrier1", title: "Lack of training for workers and managers", color: "bg-chart-1" },
      { key: "barrier2", title: "Resistance to change", color: "bg-chart-2" },
      { key: "barrier3", title: "Lack of digital culture and training", color: "bg-chart-3" },
      { key: "barrier4", title: "Higher investment in employees' training", color: "bg-chart-4" },
      { key: "barrier5", title: "Lack of knowledge management systems", color: "bg-chart-5" },
    ],
  },
  {
    id: "regulatory-standards",
    title: "Regulatory & Standards",
    description: "Compliance and standardization challenges",
    barriers: [
      { key: "barrier6", title: "Regulatory compliance issues", color: "bg-chart-1" },
      { key: "barrier7", title: "Lack of Standards and Reference Architecture", color: "bg-chart-2" },
      { key: "barrier13", title: "Compliance with Sector-Specific Regulations", color: "bg-chart-3" },
      { key: "barrier14", title: "Lack of Regulations and Standards", color: "bg-chart-4" },
    ],
  },
  {
    id: "infrastructure-financial",
    title: "Infrastructure & Financial",
    description: "Technology infrastructure and funding challenges",
    barriers: [
      { key: "barrier8", title: "Lack of Internet coverage and IT facilities", color: "bg-chart-1" },
      { key: "barrier9", title: "Limited Access to Funding and Credit", color: "bg-chart-2" },
      { key: "barrier10", title: "Future viability & profitability", color: "bg-chart-3" },
      { key: "barrier12", title: "High Implementation Cost", color: "bg-chart-4" },
    ],
  },
  {
    id: "operational",
    title: "Operational",
    description: "Vendor dependencies and customer relations",
    barriers: [
      { key: "barrier11", title: "Dependency on External Vendors", color: "bg-chart-1" },
      { key: "barrier15", title: "Customers are hesitant to share data", color: "bg-chart-2" },
    ],
  },
]

export function BarriersStep({ data, onChange }: BarriersStepProps) {
  const [activeCategory, setActiveCategory] = useState("human-capital")

  const updateBarrierData = (barrierKey: string, barrierData: any) => {
    onChange({ [barrierKey]: barrierData })
  }

  const getCompletedBarriers = (categoryBarriers: any[]) => {
    return categoryBarriers.filter((barrier) => {
      const barrierData = data[barrier.key]
      return barrierData && Object.keys(barrierData).length > 0
    }).length
  }

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-serif font-bold text-primary mb-2">Barrier Assessment</h2>
        <p className="text-muted-foreground">
          Evaluate your organization across 15 key barriers to IoT adoption. Complete all sections for accurate
          analysis.
        </p>
      </div>

      <Tabs value={activeCategory} onValueChange={setActiveCategory}>
        <TabsList className="grid w-full grid-cols-2 sm:grid-cols-4 gap-1 h-auto p-1">
          {barrierCategories.map((category) => {
            const completed = getCompletedBarriers(category.barriers)
            const total = category.barriers.length

            return (
              <TabsTrigger key={category.id} value={category.id} className="relative data-[state=active]:bg-secondary py-2 sm:py-3 px-2">
                <div className="flex flex-col items-center gap-0.5 sm:gap-1">
                  <span className="text-[10px] sm:text-xs font-medium leading-tight text-center">{category.title}</span>
                  <Badge variant={completed === total ? "default" : "secondary"} className="text-[9px] sm:text-xs px-1.5 py-0">
                    {completed}/{total}
                  </Badge>
                </div>
              </TabsTrigger>
            )
          })}
        </TabsList>

        {barrierCategories.map((category) => (
          <TabsContent key={category.id} value={category.id} className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="font-serif">{category.title}</CardTitle>
                <CardDescription>{category.description}</CardDescription>
              </CardHeader>
            </Card>

            <div className="space-y-4 sm:space-y-6">
              {category.barriers.map((barrier) => (
                <Card key={barrier.key}>
                  <CardHeader className="p-4 sm:p-6">
                    <CardTitle className="flex items-center gap-2 sm:gap-3 text-base sm:text-lg">
                      <div className={`w-2.5 h-2.5 sm:w-3 sm:h-3 rounded-full ${barrier.color}`} />
                      <span className="text-sm sm:text-base leading-tight">{barrier.title}</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="p-4 sm:p-6 pt-0">
                    <BarrierForm
                      barrierKey={barrier.key}
                      data={data[barrier.key] || {}}
                      onChange={(barrierData) => updateBarrierData(barrier.key, barrierData)}
                    />
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>
        ))}
      </Tabs>
    </div>
  )
}
