"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Building2, BarChart3, DollarSign, Target, Download, FileText, Zap } from "lucide-react"
import type { FormData } from "../isri-assessment-form"

interface ReviewStepProps {
  data: FormData
  onSubmit: () => void
  isSubmitting: boolean
}

export function ReviewStep({ data, onSubmit, isSubmitting }: ReviewStepProps) {
  const getCompletedBarriers = () => {
    return Object.values(data.barriers).filter((barrier) => barrier && Object.keys(barrier).length > 0).length
  }

  const getCompletedCostFactors = () => {
    return Object.keys(data.cost_factor_inputs).length
  }

  const getCompletedKPIFactors = () => {
    return Object.values(data.kpi_factor_inputs).filter((value) => value !== undefined).length
  }

  const isFormComplete = () => {
    return (
      data.company_details.company_name &&
      data.company_details.industry &&
      data.company_details.num_employees > 0 &&
      data.company_details.annual_revenue > 0 &&
      getCompletedBarriers() === 15 &&
      getCompletedCostFactors() > 0 &&
      getCompletedKPIFactors() > 0
    )
  }

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-serif font-bold text-primary mb-2">Review & Generate Reports</h2>
        <p className="text-muted-foreground">
          Review your assessment data and generate comprehensive AI-powered IoT readiness reports.
        </p>
      </div>

      {/* Company Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building2 className="h-5 w-5 text-secondary" />
            Company Overview
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-muted-foreground">Company Name</p>
              <p className="font-medium">{data.company_details.company_name || "Not provided"}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Industry</p>
              <p className="font-medium">{data.company_details.industry || "Not provided"}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Employees</p>
              <p className="font-medium">{data.company_details.num_employees || 0}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Annual Revenue</p>
              <p className="font-medium">₹{data.company_details.annual_revenue || 0} Crores</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Assessment Summary */}
      <div className="grid md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-lg">
              <BarChart3 className="h-5 w-5 text-chart-1" />
              Barriers
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <span className="text-2xl font-bold">{getCompletedBarriers()}/15</span>
              <Badge variant={getCompletedBarriers() === 15 ? "default" : "secondary"}>
                {getCompletedBarriers() === 15 ? "Complete" : "Incomplete"}
              </Badge>
            </div>
            <p className="text-sm text-muted-foreground mt-2">IoT adoption barriers assessed</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-lg">
              <DollarSign className="h-5 w-5 text-chart-2" />
              Cost Factors
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <span className="text-2xl font-bold">{getCompletedCostFactors()}/20</span>
              <Badge variant={getCompletedCostFactors() > 0 ? "default" : "secondary"}>
                {getCompletedCostFactors() > 0 ? "Complete" : "Incomplete"}
              </Badge>
            </div>
            <p className="text-sm text-muted-foreground mt-2">Cost categories analyzed</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-lg">
              <Target className="h-5 w-5 text-chart-3" />
              KPI Factors
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <span className="text-2xl font-bold">{getCompletedKPIFactors()}/17</span>
              <Badge variant={getCompletedKPIFactors() > 0 ? "default" : "secondary"}>
                {getCompletedKPIFactors() > 0 ? "Complete" : "Incomplete"}
              </Badge>
            </div>
            <p className="text-sm text-muted-foreground mt-2">Performance indicators selected</p>
          </CardContent>
        </Card>
      </div>

      <Separator />

      {/* Report Generation */}
      <Card className="bg-gradient-to-r from-secondary/5 to-accent/5 border-secondary/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-xl">
            <Zap className="h-6 w-6 text-secondary" />
            AI-Powered Report Generation
          </CardTitle>
          <CardDescription>Generate comprehensive reports with strategic insights and recommendations</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid md:grid-cols-2 gap-4">
            <div className="flex items-start gap-3 p-4 rounded-lg bg-background/50">
              <FileText className="h-5 w-5 text-chart-1 mt-0.5" />
              <div>
                <h4 className="font-medium text-primary">Barrier Analysis Report</h4>
                <p className="text-sm text-muted-foreground">
                  Detailed analysis of all 15 barriers with severity levels and impact assessment
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3 p-4 rounded-lg bg-background/50">
              <Target className="h-5 w-5 text-chart-2 mt-0.5" />
              <div>
                <h4 className="font-medium text-primary">Strategic Roadmap</h4>
                <p className="text-sm text-muted-foreground">
                  Action plan for addressing top 3 barriers with implementation guidance
                </p>
              </div>
            </div>
          </div>

          {!isFormComplete() && (
            <div className="p-4 rounded-lg bg-destructive/10 border border-destructive/20">
              <p className="text-sm text-destructive font-medium">
                Please complete all required sections before generating reports:
              </p>
              <ul className="text-sm text-destructive mt-2 space-y-1">
                {!data.company_details.company_name && <li>• Company details are incomplete</li>}
                {getCompletedBarriers() < 15 && <li>• Complete all 15 barrier assessments</li>}
                {getCompletedCostFactors() === 0 && <li>• Add cost factor data</li>}
                {getCompletedKPIFactors() === 0 && <li>• Select relevant KPI factors</li>}
              </ul>
            </div>
          )}

          <Button
            onClick={onSubmit}
            disabled={!isFormComplete() || isSubmitting}
            className="w-full bg-secondary hover:bg-secondary/90 text-lg py-6"
          >
            {isSubmitting ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                Generating AI Reports...
              </>
            ) : (
              <>
                <Download className="h-5 w-5 mr-2" />
                Generate ISRI Assessment Reports
              </>
            )}
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
