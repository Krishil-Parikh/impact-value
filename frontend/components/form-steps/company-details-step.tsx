"use client"

import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Building2, DollarSign, Factory } from "lucide-react"

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
      onChange({ [field]: clamp(value) })
    } else {
      onChange({ [field]: value })
    }
  }

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-serif font-bold text-primary mb-2">Tell us about your company</h2>
        <p className="text-muted-foreground">
          This information helps us provide more accurate assessments and recommendations.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center gap-2 text-lg">
              <Building2 className="h-5 w-5 text-secondary" />
              Company Information
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="company_name" className="text-sm font-medium">
                Company Name *
              </Label>
              <Input
                id="company_name"
                value={data.company_name}
                onChange={(e) => handleChange("company_name", e.target.value)}
                placeholder="Enter your company name"
                className="mt-1"
                required
              />
            </div>
            <div>
              <Label htmlFor="industry" className="text-sm font-medium">
                Industry *
              </Label>
              <Input
                id="industry"
                value={data.industry}
                onChange={(e) => handleChange("industry", e.target.value)}
                placeholder="e.g., Manufacturing, Automotive, Textiles"
                className="mt-1"
                required
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center gap-2 text-lg">
              <Factory className="h-5 w-5 text-secondary" />
              Business Metrics
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="num_employees" className="text-sm font-medium">
                Number of Employees *
              </Label>
              <Input
                id="num_employees"
                type="number"
                value={data.num_employees || ""}
                onChange={(e) => handleChange("num_employees", Number.parseInt(e.target.value) || 0)}
                placeholder="Enter total number of employees (0-1000)"
                className="mt-1"
                min={0}
                max={1000}
                required
              />
            </div>
            <div>
              <Label htmlFor="annual_revenue" className="text-sm font-medium">
                Annual Revenue (in Crores) *
              </Label>
              <Input
                id="annual_revenue"
                type="number"
                step="0.01"
                value={data.annual_revenue || ""}
                onChange={(e) => handleChange("annual_revenue", Number.parseFloat(e.target.value) || 0)}
                placeholder="Enter annual revenue in crores (0-1000)"
                className="mt-1"
                min={0}
                max={1000}
                required
              />
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="bg-muted/50">
        <CardContent className="pt-6">
          <div className="flex items-start gap-3">
            <div className="bg-secondary/10 p-2 rounded-lg">
              <DollarSign className="h-5 w-5 text-secondary" />
            </div>
            <div>
              <h3 className="font-medium text-primary mb-1">Data Privacy & Security</h3>
              <p className="text-sm text-muted-foreground">
                Your company information is encrypted and used solely for generating your IoT readiness assessment. We
                do not share your data with third parties and all reports are generated securely.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
