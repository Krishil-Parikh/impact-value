"use client"

import { Suspense } from "react"
import { useSearchParams } from "next/navigation"
import { ReportLoading } from "@/components/report-loading"
import { Card, CardContent } from "@/components/ui/card"

function LoadingContent() {
  const searchParams = useSearchParams()
  const sessionId = searchParams.get("session")

  if (!sessionId) {
    return (
      <div className="max-w-3xl mx-auto py-12 px-4">
        <Card>
          <CardContent className="pt-6">
            <p className="text-center text-muted-foreground">No session found. Please start a new assessment.</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return <ReportLoading sessionId={sessionId} />
}

export default function LoadingPage() {
  return (
    <Suspense
      fallback={
        <div className="max-w-3xl mx-auto py-12 px-4">
          <Card>
            <CardContent className="pt-6">
              <p className="text-center">Initializing...</p>
            </CardContent>
          </Card>
        </div>
      }
    >
      <LoadingContent />
    </Suspense>
  )
}
