"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import { CheckCircle2, Loader2, FileText, AlertCircle } from "lucide-react"
import { useRouter } from "next/navigation"

interface ReportLoadingProps {
  sessionId: string
}

interface StatusResponse {
  status: "processing" | "completed" | "error"
  progress: number
  message: string
  comprehensive_ready: boolean
  roadmap_ready: boolean
  error?: string
}

export function ReportLoading({ sessionId }: ReportLoadingProps) {
  const router = useRouter()
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
  const [status, setStatus] = useState<StatusResponse>({
    status: "processing",
    progress: 0,
    message: "Starting report generation...",
    comprehensive_ready: false,
    roadmap_ready: false,
  })

  useEffect(() => {
    const pollStatus = async () => {
      try {
        const response = await fetch(`${API_BASE}/status/${sessionId}`)
        if (response.ok) {
          const data = await response.json()
          setStatus(data)

          if (data.status === "completed") {
            // Redirect to preview page after 2 seconds
            setTimeout(() => {
              router.push(`/preview?session=${sessionId}`)
            }, 2000)
          }
        }
      } catch (error) {
        console.error("Error polling status:", error)
      }
    }

    // Poll every 2 seconds
    const interval = setInterval(pollStatus, 2000)

    // Initial poll
    pollStatus()

    return () => clearInterval(interval)
  }, [sessionId, router])

  return (
    <div className="max-w-3xl mx-auto py-12 px-4">
      <Card className="shadow-lg">
        <CardHeader className="text-center">
          <CardTitle className="text-3xl font-serif text-primary">Generating Your ISRI Reports</CardTitle>
          <CardDescription className="text-base mt-2">
            Our AI is analyzing your data and creating comprehensive reports. This may take a few minutes.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-8">
          {/* Progress Bar */}
          <div className="space-y-3">
            <div className="flex items-center justify-between text-sm">
              <span className="font-medium">{status.message}</span>
              <span className="text-muted-foreground">{status.progress}%</span>
            </div>
            <Progress value={status.progress} className="h-3" />
          </div>

          {/* Status Cards */}
          <div className="grid gap-4 md:grid-cols-2">
            {/* Comprehensive Analysis */}
            <Card className={status.comprehensive_ready ? "border-green-500 bg-green-50" : ""}>
              <CardContent className="pt-6">
                <div className="flex items-start gap-3">
                  {status.comprehensive_ready ? (
                    <CheckCircle2 className="h-6 w-6 text-green-600 mt-0.5" />
                  ) : (
                    <Loader2 className="h-6 w-6 text-primary animate-spin mt-0.5" />
                  )}
                  <div className="flex-1">
                    <h3 className="font-semibold flex items-center gap-2">
                      <FileText className="h-4 w-4" />
                      Comprehensive Analysis
                    </h3>
                    <p className="text-sm text-muted-foreground mt-1">
                      {status.comprehensive_ready
                        ? "✓ Ready to view and download"
                        : "Analyzing all 15 barriers..."}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Strategic Roadmap */}
            <Card className={status.roadmap_ready ? "border-green-500 bg-green-50" : ""}>
              <CardContent className="pt-6">
                <div className="flex items-start gap-3">
                  {status.roadmap_ready ? (
                    <CheckCircle2 className="h-6 w-6 text-green-600 mt-0.5" />
                  ) : (
                    <Loader2 className="h-6 w-6 text-primary animate-spin mt-0.5" />
                  )}
                  <div className="flex-1">
                    <h3 className="font-semibold flex items-center gap-2">
                      <FileText className="h-4 w-4" />
                      Strategic Roadmap
                    </h3>
                    <p className="text-sm text-muted-foreground mt-1">
                      {status.roadmap_ready ? "✓ Ready to view and download" : "Creating roadmap for top 3 barriers..."}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Error Display */}
          {status.status === "error" && (
            <Card className="border-red-500 bg-red-50">
              <CardContent className="pt-6">
                <div className="flex items-start gap-3">
                  <AlertCircle className="h-6 w-6 text-red-600" />
                  <div>
                    <h3 className="font-semibold text-red-900">Error Generating Reports</h3>
                    <p className="text-sm text-red-700 mt-1">{status.error}</p>
                    <Button variant="outline" className="mt-3" onClick={() => router.push("/")}>
                      Return to Form
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Info Message */}
          {status.status === "processing" && (
            <div className="text-center text-sm text-muted-foreground bg-muted/50 p-4 rounded-lg">
              <p>
                💡 <strong>Tip:</strong> We're using advanced AI to analyze your data in multiple parts to provide the
                most detailed insights. Each part is being generated and stitched together for you.
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
