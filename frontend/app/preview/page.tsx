"use client"

import { useEffect, useState, Suspense } from "react"
import { useSearchParams } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Download, FileText, ArrowLeft, ExternalLink } from "lucide-react"
import Link from "next/link"

function PreviewContent() {
  const searchParams = useSearchParams()
  const sessionId = searchParams.get("session")
  const [downloading, setDownloading] = useState<string | null>(null)

  const handleDownload = async (type: "comprehensive" | "roadmap") => {
    if (!sessionId) return
    const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

    setDownloading(type)
    try {
      const response = await fetch(`${API_BASE}/download/${sessionId}/${type}`)
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement("a")
        a.href = url
        a.download =
          type === "comprehensive" ? "Comprehensive_Barrier_Analysis.pdf" : "Strategic_Roadmap_Top_3.pdf"
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      }
    } catch (error) {
      console.error("Download error:", error)
    } finally {
      setDownloading(null)
    }
  }

  const handlePreview = async (type: "comprehensive" | "roadmap") => {
    if (!sessionId) return
    const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

    try {
      const response = await fetch(`${API_BASE}/download/${sessionId}/${type}`)
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        window.open(url, "_blank")
      }
    } catch (error) {
      console.error("Preview error:", error)
    }
  }

  if (!sessionId) {
    return (
      <div className="max-w-3xl mx-auto py-12 px-4">
        <Card>
          <CardContent className="pt-6">
            <p className="text-center text-muted-foreground">No session found. Please generate a report first.</p>
            <div className="flex justify-center mt-4">
              <Link href="/">
                <Button>Go to Assessment</Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="max-w-5xl mx-auto py-12 px-4">
      <div className="mb-8">
        <Link href="/">
          <Button variant="ghost" className="mb-4">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Assessment
          </Button>
        </Link>
        <h1 className="text-4xl font-serif font-bold text-primary mb-2">Your ISRI Reports Are Ready!</h1>
        <p className="text-lg text-muted-foreground">
          Preview and download your comprehensive IoT readiness assessment reports.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Comprehensive Analysis */}
        <Card className="shadow-lg hover:shadow-xl transition-shadow">
          <CardHeader className="bg-gradient-to-br from-primary/5 to-primary/10">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-primary/10 rounded-lg">
                <FileText className="h-6 w-6 text-primary" />
              </div>
              <div>
                <CardTitle className="text-xl">Comprehensive Barrier Analysis</CardTitle>
                <CardDescription className="mt-1">All 15 barriers analyzed in detail</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="pt-6 space-y-4">
            <div className="space-y-2 text-sm">
              <p className="flex items-start gap-2">
                <span className="text-primary">•</span>
                <span>Executive summary of IoT readiness</span>
              </p>
              <p className="flex items-start gap-2">
                <span className="text-primary">•</span>
                <span>Detailed analysis of each barrier</span>
              </p>
              <p className="flex items-start gap-2">
                <span className="text-primary">•</span>
                <span>Prioritization matrix</span>
              </p>
              {/* Strategic recommendations are part of the Strategic Roadmap, not the comprehensive barrier analysis */}
            </div>

            <div className="flex gap-2 pt-4">
              <Button
                className="flex-1"
                onClick={() => handlePreview("comprehensive")}
                variant="outline"
                disabled={downloading === "comprehensive"}
              >
                <ExternalLink className="h-4 w-4 mr-2" />
                Preview
              </Button>
              <Button
                className="flex-1"
                onClick={() => handleDownload("comprehensive")}
                disabled={downloading === "comprehensive"}
              >
                <Download className="h-4 w-4 mr-2" />
                {downloading === "comprehensive" ? "Downloading..." : "Download"}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Strategic Roadmap */}
        <Card className="shadow-lg hover:shadow-xl transition-shadow">
          <CardHeader className="bg-gradient-to-br from-secondary/5 to-secondary/10">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-secondary/10 rounded-lg">
                <FileText className="h-6 w-6 text-secondary" />
              </div>
              <div>
                <CardTitle className="text-xl">Strategic Roadmap</CardTitle>
                <CardDescription className="mt-1">Actionable plan for top 3 barriers</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="pt-6 space-y-4">
            <div className="space-y-2 text-sm">
              <p className="flex items-start gap-2">
                <span className="text-secondary">•</span>
                <span>Phased implementation plan</span>
              </p>
              <p className="flex items-start gap-2">
                <span className="text-secondary">•</span>
                <span>Timeline: 0-3, 4-9, 10-18+ months</span>
              </p>
              <p className="flex items-start gap-2">
                <span className="text-secondary">•</span>
                <span>Includes strategic recommendations and impact values for top barriers</span>
              </p>
              <p className="flex items-start gap-2">
                <span className="text-secondary">•</span>
                <span>Key performance indicators</span>
              </p>
              <p className="flex items-start gap-2">
                <span className="text-secondary">•</span>
                <span>Risk mitigation strategies</span>
              </p>
            </div>

            <div className="flex gap-2 pt-4">
              <Button
                className="flex-1"
                onClick={() => handlePreview("roadmap")}
                variant="outline"
                disabled={downloading === "roadmap"}
              >
                <ExternalLink className="h-4 w-4 mr-2" />
                Preview
              </Button>
              <Button
                className="flex-1"
                onClick={() => handleDownload("roadmap")}
                disabled={downloading === "roadmap"}
              >
                <Download className="h-4 w-4 mr-2" />
                {downloading === "roadmap" ? "Downloading..." : "Download"}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Info Card */}
      <Card className="mt-8 bg-muted/50">
        <CardContent className="pt-6">
          <div className="flex items-start gap-3">
            <div className="p-2 bg-primary/10 rounded-lg">
              <FileText className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h3 className="font-semibold mb-2">About Your Reports</h3>
              <p className="text-sm text-muted-foreground mb-3">
                Your ISRI assessment reports have been generated using advanced AI analysis. Each report provides
                actionable insights tailored to your organization's specific context.
              </p>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>
                  📊 <strong>Data-driven insights:</strong> Based on your actual barrier, cost, and KPI inputs
                </li>
                <li>
                  🤖 <strong>AI-powered analysis:</strong> Generated using state-of-the-art language models
                </li>
                <li>
                  🎯 <strong>Actionable recommendations:</strong> Practical steps you can implement immediately
                </li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default function PreviewPage() {
  return (
    <Suspense
      fallback={
        <div className="max-w-3xl mx-auto py-12 px-4">
          <Card>
            <CardContent className="pt-6">
              <p className="text-center">Loading preview...</p>
            </CardContent>
          </Card>
        </div>
      }
    >
      <PreviewContent />
    </Suspense>
  )
}
