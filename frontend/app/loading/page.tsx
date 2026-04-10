"use client"

import { Suspense } from "react"
import { useSearchParams } from "next/navigation"
import { ReportLoading } from "@/components/report-loading"
import { Loader2 } from "lucide-react"

function LoadingContent() {
  const searchParams = useSearchParams()
  const sessionId = searchParams.get("session")

  if (!sessionId) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background px-4">
        <div className="glass-card rounded-2xl p-8 text-center max-w-sm w-full">
          <p className="text-sm text-muted-foreground">No session found. Please start a new assessment.</p>
        </div>
      </div>
    )
  }

  return <ReportLoading sessionId={sessionId} />
}

export default function LoadingPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-background">
          <div className="flex flex-col items-center gap-4">
            <Loader2 className="h-7 w-7 animate-spin text-primary" />
            <p className="text-sm text-muted-foreground">Initializing…</p>
          </div>
        </div>
      }
    >
      <LoadingContent />
    </Suspense>
  )
}
