"use client"

import { Suspense } from "react"
import { useSearchParams, useRouter } from "next/navigation"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import {
  Download, ExternalLink, ArrowLeft, RefreshCw,
  FileBarChart2, Map, CheckCircle2, Loader2,
  Cpu, Sparkles, BarChart3
} from "lucide-react"
import Link from "next/link"
import { useToast } from "@/hooks/use-toast"
import { motion } from "framer-motion"
import { cn } from "@/lib/utils"

function PreviewContent() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const sessionId = searchParams.get("session")
  const [downloading, setDownloading] = useState<string | null>(null)
  const [previewing, setPreviewing] = useState<string | null>(null)
  const [isRetrying, setIsRetrying] = useState(false)
  const { toast } = useToast()

  const handleRetry = async () => {
    setIsRetrying(true)
    try {
      const payloadString = localStorage.getItem("isri_last_payload")
      if (!payloadString) throw new Error("No previous assessment data found to retry.")
      const apiPayload = JSON.parse(payloadString)
      const API_BASE = process.env.NEXT_PUBLIC_API_URL || ""
      const endpoint = API_BASE ? `${API_BASE}/generate_report_async` : "/api/generate-report"
      const response = await fetch(endpoint, {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(apiPayload),
      })
      if (!response.ok) throw new Error("Failed to restart report generation")
      const result = await response.json()
      router.push(`/loading?session=${result.session_id}`)
    } catch (error: any) {
      toast({ title: "Retry failed", description: error.message || "Please try again.", variant: "destructive" })
    } finally {
      setIsRetrying(false)
    }
  }

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
        a.download = type === "comprehensive" ? "Comprehensive_Barrier_Analysis.pdf" : "Strategic_Roadmap_Top_3.pdf"
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
        toast({ title: "Download started", description: "Your report is downloading." })
      } else {
        toast({ title: "Download failed", description: "Could not fetch the report.", variant: "destructive" })
      }
    } catch {
      toast({ title: "Download failed", description: "Network error.", variant: "destructive" })
    } finally {
      setDownloading(null)
    }
  }

  const handlePreview = async (type: "comprehensive" | "roadmap") => {
    if (!sessionId) return
    const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
    setPreviewing(type)
    try {
      const response = await fetch(`${API_BASE}/download/${sessionId}/${type}`)
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        window.open(url, "_blank")
      } else {
        toast({ title: "Preview failed", description: "Could not load the report.", variant: "destructive" })
      }
    } catch {
      toast({ title: "Preview failed", description: "Network error.", variant: "destructive" })
    } finally {
      setPreviewing(null)
    }
  }

  if (!sessionId) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background px-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-center">
          <div className="w-16 h-16 rounded-2xl bg-muted border border-border flex items-center justify-center mx-auto mb-5">
            <FileBarChart2 className="h-7 w-7 text-muted-foreground" />
          </div>
          <h2 className="font-serif font-bold text-xl text-foreground mb-2">No session found</h2>
          <p className="text-sm text-muted-foreground mb-6">Please generate a report first.</p>
          <Link href="/">
            <Button className="bg-primary hover:bg-primary/90 text-primary-foreground">Go to Assessment</Button>
          </Link>
        </motion.div>
      </div>
    )
  }

  const reports = [
    {
      type: "comprehensive" as const,
      icon: FileBarChart2,
      label: "Report 01",
      title: "Comprehensive Barrier Analysis",
      subtitle: "All 15 barriers in full detail",
      description: "In-depth evaluation of every IoT adoption barrier — severity levels, root-cause analysis, impact scores, and tailored strategic recommendations.",
      bullets: [
        "Executive readiness summary",
        "Analysis of all 15 barriers",
        "Barrier prioritisation matrix",
        "AI-generated recommendations",
      ],
      accentClass: "text-primary",
      borderClass: "border-primary/20 hover:border-primary/40",
      bgClass: "bg-primary/5",
      iconBg: "bg-primary/10",
      btnClass: "bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg shadow-primary/20 hover:shadow-primary/35",
    },
    {
      type: "roadmap" as const,
      icon: Map,
      label: "Report 02",
      title: "Strategic Roadmap",
      subtitle: "Top 3 priority barriers",
      description: "A phased 18-month implementation plan targeting the highest-impact barriers, with milestones, KPI targets, and risk mitigation strategies.",
      bullets: [
        "Phased timeline: 0–3, 4–9, 10–18 months",
        "KPI targets per phase",
        "Risk mitigation strategies",
        "Quick-win action items",
      ],
      accentClass: "text-secondary",
      borderClass: "border-secondary/20 hover:border-secondary/40",
      bgClass: "bg-secondary/5",
      iconBg: "bg-secondary/10",
      btnClass: "bg-secondary hover:bg-secondary/90 text-secondary-foreground shadow-lg shadow-secondary/20 hover:shadow-secondary/35",
    },
  ]

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* Background */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{ background: "radial-gradient(ellipse 70% 50% at 50% 0%, rgba(29,78,216,0.05) 0%, transparent 60%)" }}
      />
      <div className="bg-dot-grid absolute inset-0 pointer-events-none opacity-20" />

      <div className="relative z-10 max-w-5xl mx-auto px-6 py-10">

        {/* ── Header ──────────────────────────────────────────────────── */}
        <motion.div initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }} className="mb-12">
          <Link href="/">
            <button className="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-primary mb-8 transition-colors group">
              <ArrowLeft className="h-3.5 w-3.5 group-hover:-translate-x-0.5 transition-transform" />
              Back to Assessment
            </button>
          </Link>

          <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-5">
            <div>
              {/* Success badge */}
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full badge-green mb-4 text-xs font-semibold">
                <motion.div
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                  className="w-1.5 h-1.5 rounded-full bg-secondary"
                />
                Reports Generated Successfully
              </div>

              <h1 className="font-serif font-extrabold text-3xl sm:text-4xl text-foreground mb-2">
                Your ISRI Reports Are Ready
              </h1>
              <p className="text-sm text-muted-foreground">
                Preview or download your AI-generated IoT readiness reports below.
              </p>
            </div>

            <Button
              variant="outline"
              size="sm"
              onClick={handleRetry}
              disabled={isRetrying}
              className="gap-2 flex-shrink-0 border-border hover:border-primary/30 hover:text-primary transition-all"
            >
              <RefreshCw className={cn("h-3.5 w-3.5", isRetrying && "animate-spin")} />
              {isRetrying ? "Starting…" : "Regenerate"}
            </Button>
          </div>
        </motion.div>

        {/* ── Report cards ─────────────────────────────────────────────── */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {reports.map((report, i) => {
            const Icon = report.icon
            const isDownloading = downloading === report.type
            const isPreviewing = previewing === report.type

            return (
              <motion.div
                key={report.type}
                initial={{ opacity: 0, y: 24 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.12 }}
                className={cn(
                  "glass-card rounded-3xl overflow-hidden border transition-all duration-300",
                  report.borderClass
                )}
              >
                {/* Card header */}
                <div className={cn("px-7 py-6 border-b border-border/60", report.bgClass)}>
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-start gap-3.5">
                      <div className={cn("w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0", report.iconBg)}>
                        <Icon className={cn("h-5 w-5", report.accentClass)} />
                      </div>
                      <div>
                        <div className={cn("text-[10px] font-bold tracking-widest uppercase mb-1 mono", report.accentClass)}>
                          {report.label}
                        </div>
                        <h2 className="font-serif font-bold text-base text-foreground leading-tight">{report.title}</h2>
                        <p className="text-xs text-muted-foreground mt-0.5">{report.subtitle}</p>
                      </div>
                    </div>
                    <CheckCircle2 className={cn("h-5 w-5 flex-shrink-0 mt-1", report.accentClass)} />
                  </div>
                </div>

                {/* Card body */}
                <div className="px-7 py-6 space-y-5">
                  <p className="text-sm text-muted-foreground leading-relaxed">{report.description}</p>

                  <ul className="space-y-2">
                    {report.bullets.map((bullet, j) => (
                      <li key={j} className="flex items-start gap-2.5 text-sm text-foreground/75">
                        <div className={cn("w-1.5 h-1.5 rounded-full flex-shrink-0 mt-2", report.accentClass.replace("text-", "bg-"))} />
                        {bullet}
                      </li>
                    ))}
                  </ul>

                  <div className="flex gap-2.5 pt-2">
                    <button
                      className="flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl border border-border hover:border-primary/30 text-sm text-muted-foreground hover:text-foreground transition-all duration-200 bg-muted/30 hover:bg-muted/60 disabled:opacity-50"
                      onClick={() => handlePreview(report.type)}
                      disabled={isPreviewing || isDownloading}
                    >
                      {isPreviewing ? <Loader2 className="h-4 w-4 animate-spin" /> : <ExternalLink className="h-4 w-4" />}
                      {isPreviewing ? "Loading…" : "Preview"}
                    </button>
                    <button
                      className={cn(
                        "flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl text-sm font-semibold transition-all duration-200 disabled:opacity-50",
                        report.btnClass
                      )}
                      onClick={() => handleDownload(report.type)}
                      disabled={isDownloading || isPreviewing}
                    >
                      {isDownloading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Download className="h-4 w-4" />}
                      {isDownloading ? "Downloading…" : "Download PDF"}
                    </button>
                  </div>
                </div>
              </motion.div>
            )
          })}
        </div>

        {/* ── Info strip ───────────────────────────────────────────────── */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35 }}
          className="glass-card rounded-2xl px-7 py-5"
        >
          <div className="grid sm:grid-cols-3 gap-5">
            {[
              { icon: BarChart3, label: "Data-driven", detail: "Based on your barrier, cost & KPI inputs" },
              { icon: Sparkles, label: "AI-powered", detail: "Generated with state-of-the-art language models" },
              { icon: Cpu, label: "ISRI Framework", detail: "Based on Indian SME IoT Readiness survey data" },
            ].map((item, i) => (
              <div key={i} className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-lg bg-primary/8 border border-primary/15 flex items-center justify-center flex-shrink-0">
                  <item.icon className="h-3.5 w-3.5 text-primary/70" />
                </div>
                <div>
                  <div className="text-sm font-semibold text-foreground">{item.label}</div>
                  <div className="text-xs text-muted-foreground mt-0.5">{item.detail}</div>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

      </div>
    </div>
  )
}

export default function PreviewPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-7 w-7 animate-spin text-primary" />
          <p className="text-sm text-muted-foreground">Loading…</p>
        </div>
      </div>
    }>
      <PreviewContent />
    </Suspense>
  )
}
