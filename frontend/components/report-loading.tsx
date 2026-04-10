"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { useToast } from "@/hooks/use-toast"
import { CheckCircle2, AlertCircle, Sparkles, RefreshCw, FileBarChart2, Map, Cpu } from "lucide-react"
import { useRouter } from "next/navigation"
import { motion, AnimatePresence } from "framer-motion"
import { cn } from "@/lib/utils"

interface ReportLoadingProps { sessionId: string }

interface StatusResponse {
  status: "processing" | "completed" | "error"
  progress: number
  message: string
  comprehensive_ready: boolean
  roadmap_ready: boolean
  error?: string
}

const processingSteps = [
  { label: "Calculating barrier scores",        threshold: 20, icon: "⬡" },
  { label: "Computing cost factor impact",      threshold: 40, icon: "⬡" },
  { label: "Evaluating KPI correlations",       threshold: 55, icon: "⬡" },
  { label: "Generating comprehensive analysis", threshold: 75, icon: "⬡" },
  { label: "Building strategic roadmap",        threshold: 90, icon: "⬡" },
  { label: "Finalising your reports",           threshold: 100, icon: "⬡" },
]

/* ── Circular progress ring ───────────────────────────────────────── */
function CircularProgress({ progress }: { progress: number }) {
  const radius = 54
  const circumference = 2 * Math.PI * radius
  const strokeDashoffset = circumference - (progress / 100) * circumference

  return (
    <div className="relative w-36 h-36">
      <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
        {/* Track */}
        <circle
          cx="60" cy="60" r={radius}
          fill="none"
          stroke="rgba(29, 78, 216, 0.1)"
          strokeWidth="6"
        />
        {/* Progress */}
        <motion.circle
          cx="60" cy="60" r={radius}
          fill="none"
          stroke="url(#progressGradient)"
          strokeWidth="6"
          strokeLinecap="round"
          strokeDasharray={circumference}
          animate={{ strokeDashoffset }}
          transition={{ duration: 0.8, ease: "easeInOut" }}
        />
        <defs>
          <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#1D4ED8" />
            <stop offset="100%" stopColor="#6366F1" />
          </linearGradient>
        </defs>
      </svg>
      {/* Center content */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="mono text-3xl font-bold text-foreground">{progress}</span>
        <span className="text-[10px] text-muted-foreground font-semibold tracking-widest uppercase">%</span>
      </div>
    </div>
  )
}

export function ReportLoading({ sessionId }: ReportLoadingProps) {
  const router = useRouter()
  const { toast } = useToast()
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
  const [isRetrying, setIsRetrying] = useState(false)
  const [status, setStatus] = useState<StatusResponse>({
    status: "processing", progress: 0,
    message: "Starting report generation...",
    comprehensive_ready: false, roadmap_ready: false,
  })

  const handleRetry = async () => {
    setIsRetrying(true)
    try {
      const payloadString = localStorage.getItem("isri_last_payload")
      if (!payloadString) throw new Error("No previous assessment data found.")
      const apiPayload = JSON.parse(payloadString)
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || ""
      const endpoint = baseUrl ? `${baseUrl}/generate_report_async` : "/api/generate-report"
      const response = await fetch(endpoint, {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(apiPayload),
      })
      if (!response.ok) throw new Error("Failed to retry report generation")
      const result = await response.json()
      toast({ title: "Retry started", description: "Report generation restarted." })
      router.push(`/loading?session=${result.session_id}`)
    } catch (error: any) {
      toast({ title: "Retry failed", description: error.message || "Please try again.", variant: "destructive" })
    } finally {
      setIsRetrying(false)
    }
  }

  useEffect(() => {
    const pollStatus = async () => {
      try {
        const response = await fetch(`${API_BASE}/status/${sessionId}`)
        if (response.ok) {
          const data = await response.json()
          setStatus(data)
          if (data.status === "completed") {
            setTimeout(() => router.push(`/preview?session=${sessionId}`), 2000)
          }
        }
      } catch (error) {
        console.error("Error polling status:", error)
      }
    }
    const interval = setInterval(pollStatus, 2000)
    pollStatus()
    return () => clearInterval(interval)
  }, [sessionId, router, API_BASE])

  const activeStepIndex = processingSteps.findIndex(s => status.progress <= s.threshold)

  const isCompleted = status.status === "completed"
  const isError = status.status === "error"

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4 py-12 relative overflow-hidden">
      {/* Background glow */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{ background: "radial-gradient(ellipse 80% 60% at 50% 30%, rgba(29,78,216,0.05) 0%, transparent 70%)" }}
      />
      <div className="bg-dot-grid absolute inset-0 pointer-events-none opacity-25" />

      {/* Scan line during processing */}
      {status.status === "processing" && <div className="scan-line" />}

      <div className="relative z-10 w-full max-w-md">

        {/* ── Header ──────────────────────────────────────────────────── */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-10"
        >
          {/* Logo/icon */}
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-primary/10 border border-primary/20 mb-6 relative">
            {isCompleted ? (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 200 }}
              >
                <CheckCircle2 className="h-7 w-7 text-secondary" />
              </motion.div>
            ) : isError ? (
              <AlertCircle className="h-7 w-7 text-destructive" />
            ) : (
              <>
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
                >
                  <Cpu className="h-7 w-7 text-primary" />
                </motion.div>
                {/* Pulsing ring */}
                <motion.div
                  className="absolute inset-0 rounded-2xl border border-primary/30"
                  animate={{ scale: [1, 1.15, 1], opacity: [0.5, 0, 0.5] }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
              </>
            )}
          </div>

          <h1 className="font-serif font-bold text-2xl sm:text-3xl text-foreground mb-2">
            {isCompleted ? "Reports Ready!" : isError ? "Generation Failed" : "Generating Your Reports"}
          </h1>
          <p className="text-sm text-muted-foreground">
            {isCompleted
              ? "Redirecting you to your reports…"
              : isError
                ? "An error occurred during generation."
                : "Our AI is analysing your data. This takes 2–4 minutes."}
          </p>
        </motion.div>

        {/* ── Processing card ──────────────────────────────────────────── */}
        {!isError && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
            className="glass-card rounded-3xl p-8 mb-5"
          >
            {/* Circular progress + step label */}
            <div className="flex flex-col items-center mb-8">
              <AnimatePresence mode="wait">
                {isCompleted ? (
                  <motion.div
                    key="complete"
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="w-36 h-36 rounded-full bg-secondary/10 border-2 border-secondary/30 flex flex-col items-center justify-center glow-green"
                  >
                    <CheckCircle2 className="h-12 w-12 text-secondary mb-1" />
                    <span className="text-xs font-semibold text-secondary">Complete</span>
                  </motion.div>
                ) : (
                  <motion.div key="progress">
                    <CircularProgress progress={status.progress} />
                  </motion.div>
                )}
              </AnimatePresence>

              {!isCompleted && (
                <motion.p
                  key={activeStepIndex}
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -6 }}
                  className="mt-4 text-sm text-muted-foreground text-center font-medium max-w-[200px]"
                >
                  {activeStepIndex >= 0 ? processingSteps[activeStepIndex].label : "Finalising your reports"}
                </motion.p>
              )}
            </div>

            {/* Progress bar (slim, under the circle) */}
            {!isCompleted && (
              <div className="mb-6">
                <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                  <motion.div
                    className="h-full rounded-full progress-glow"
                    style={{ background: "linear-gradient(90deg, #1D4ED8, #6366F1)" }}
                    animate={{ width: `${status.progress}%` }}
                    transition={{ duration: 0.7, ease: "easeInOut" }}
                  />
                </div>
              </div>
            )}

            {/* Step checklist */}
            <div className="space-y-2.5">
              {processingSteps.map((step, i) => {
                const done = status.progress > step.threshold
                const active = !done && (i === 0 || status.progress > processingSteps[i - 1].threshold)
                return (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0.3 }}
                    animate={{ opacity: done || active ? 1 : 0.35 }}
                    className="flex items-center gap-3 text-sm"
                  >
                    {done ? (
                      <div className="w-5 h-5 rounded-full bg-secondary/15 border border-secondary/30 flex items-center justify-center flex-shrink-0">
                        <CheckCircle2 className="h-3 w-3 text-secondary" />
                      </div>
                    ) : active ? (
                      <div className="w-5 h-5 rounded-full bg-primary/10 border border-primary/30 flex items-center justify-center flex-shrink-0">
                        <motion.div
                          className="w-1.5 h-1.5 rounded-full bg-primary"
                          animate={{ scale: [1, 1.4, 1], opacity: [1, 0.5, 1] }}
                          transition={{ duration: 1, repeat: Infinity }}
                        />
                      </div>
                    ) : (
                      <div className="w-5 h-5 rounded-full border border-border/40 flex-shrink-0" />
                    )}
                    <span className={cn(
                      "transition-colors",
                      done ? "text-foreground" : active ? "text-primary font-medium" : "text-muted-foreground/50"
                    )}>
                      {step.label}
                    </span>
                  </motion.div>
                )
              })}
            </div>
          </motion.div>
        )}

        {/* ── Report status cards ──────────────────────────────────────── */}
        <div className="grid grid-cols-2 gap-3 mb-5">
          {[
            {
              label: "Barrier Analysis",
              desc: "All 15 barriers",
              ready: status.comprehensive_ready,
              icon: FileBarChart2,
              color: "primary",
            },
            {
              label: "Strategic Roadmap",
              desc: "Top 3 priorities",
              ready: status.roadmap_ready,
              icon: Map,
              color: "secondary",
            },
          ].map((card, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, scale: 0.92 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.25 + i * 0.1 }}
              className={cn(
                "rounded-2xl p-4 border transition-all duration-300",
                card.ready
                  ? card.color === "primary"
                    ? "bg-primary/10 border-primary/25"
                    : "bg-secondary/10 border-secondary/25"
                  : "glass-card"
              )}
            >
              <div className="flex items-start gap-2.5">
                {card.ready ? (
                  <div className={cn(
                    "w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0",
                    card.color === "primary" ? "bg-primary/15" : "bg-secondary/15"
                  )}>
                    <card.icon className={cn("h-4 w-4", card.color === "primary" ? "text-primary" : "text-secondary")} />
                  </div>
                ) : (
                  <div className="w-8 h-8 rounded-lg bg-muted flex items-center justify-center flex-shrink-0">
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                    >
                      <card.icon className="h-4 w-4 text-muted-foreground" />
                    </motion.div>
                  </div>
                )}
                <div>
                  <div className={cn(
                    "text-xs font-semibold",
                    card.ready
                      ? card.color === "primary" ? "text-primary" : "text-secondary"
                      : "text-foreground/60"
                  )}>
                    {card.label}
                  </div>
                  <div className="text-[10px] text-muted-foreground mt-0.5">{card.desc}</div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* ── Error state ──────────────────────────────────────────────── */}
        <AnimatePresence>
          {isError && (
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass-card rounded-2xl p-6 border border-destructive/20 mb-5"
            >
              <div className="flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-destructive flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-semibold text-destructive mb-1">Error generating reports</h3>
                  <p className="text-sm text-destructive/70 mb-4">{status.error}</p>
                  <div className="flex gap-2">
                    <Button size="sm" onClick={handleRetry} disabled={isRetrying} className="gap-2">
                      <RefreshCw className={cn("h-3.5 w-3.5", isRetrying && "animate-spin")} />
                      {isRetrying ? "Retrying…" : "Try Again"}
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => router.push("/")}>
                      Back
                    </Button>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* ── Processing tip ───────────────────────────────────────────── */}
        {status.status === "processing" && (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="text-[11px] text-center text-muted-foreground/50 leading-relaxed"
          >
            <Sparkles className="h-3 w-3 inline mr-1.5 text-primary/50" />
            AI is generating contextualised multi-part reports — please keep this tab open.
          </motion.p>
        )}
      </div>
    </div>
  )
}
