"use client"

import { useState, useEffect, useRef } from "react"
import { ISRIAssessmentForm } from "@/components/isri-assessment-form"
import { motion, useInView, useMotionValue, useSpring } from "framer-motion"
import {
  ArrowRight, Brain, Target, TrendingUp, Shield,
  Network, BarChart3, Sparkles, CheckCircle,
  ChevronRight, Cpu, Layers, Zap, FileBarChart2, MapPin,
  ArrowLeft
} from "lucide-react"
import { cn } from "@/lib/utils"

/* ── Animated counter hook ─────────────────────────────────────────── */
function AnimatedCounter({ value, suffix = "" }: { value: number; suffix?: string }) {
  const ref = useRef<HTMLSpanElement>(null)
  const motionVal = useMotionValue(0)
  const spring = useSpring(motionVal, { duration: 1800, bounce: 0 })
  const inView = useInView(ref, { once: true })

  useEffect(() => {
    if (inView) motionVal.set(value)
  }, [inView, value, motionVal])

  useEffect(() => {
    return spring.on("change", (v) => {
      if (ref.current) ref.current.textContent = Math.round(v).toString() + suffix
    })
  }, [spring, suffix])

  return <span ref={ref}>0</span>
}

/* ── Navbar ────────────────────────────────────────────────────────── */
function Navbar({ onStart }: { onStart: () => void }) {
  const [scrolled, setScrolled] = useState(false)
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40)
    window.addEventListener("scroll", onScroll)
    return () => window.removeEventListener("scroll", onScroll)
  }, [])

  return (
    <motion.nav
      initial={{ opacity: 0, y: -16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={cn(
        "fixed top-0 left-0 right-0 z-50 transition-all duration-300",
        scrolled
          ? "bg-[#060E1C]/90 backdrop-blur-xl border-b border-[rgba(56,189,248,0.1)] shadow-lg shadow-black/30"
          : "bg-transparent"
      )}
    >
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center">
            <Cpu className="h-4 w-4 text-primary" />
          </div>
          <span className="font-serif font-bold text-foreground text-sm tracking-wide">ISRI</span>
          <span className="text-muted-foreground text-xs hidden sm:block">Assessment Platform</span>
        </div>
        <button
          onClick={onStart}
          className="flex items-center gap-2 px-5 py-2 rounded-lg bg-primary/10 border border-primary/20 text-primary text-sm font-medium hover:bg-primary/20 hover:border-primary/40 transition-all duration-200"
        >
          Start Assessment
          <ArrowRight className="h-3.5 w-3.5" />
        </button>
      </div>
    </motion.nav>
  )
}

/* ── Main page ─────────────────────────────────────────────────────── */
export default function Home() {
  const [showForm, setShowForm] = useState(false)

  const features = [
    {
      icon: Brain,
      title: "AI-Powered Analysis",
      description: "Advanced language models analyse your barrier data and generate strategic, context-aware recommendations.",
      color: "text-primary",
      bg: "bg-primary/10",
      border: "border-primary/20",
    },
    {
      icon: Target,
      title: "15 Barrier Assessment",
      description: "Evaluate readiness across every critical dimension — from training gaps to regulatory compliance.",
      color: "text-secondary",
      bg: "bg-secondary/10",
      border: "border-secondary/20",
    },
    {
      icon: TrendingUp,
      title: "Strategic Roadmap",
      description: "Receive a phased 18-month implementation plan with clear milestones and KPI targets.",
      color: "text-accent",
      bg: "bg-accent/10",
      border: "border-accent/20",
    },
    {
      icon: Shield,
      title: "Risk Identification",
      description: "Proactively surface financial, operational, and compliance risks before they become blockers.",
      color: "text-[#FBBF24]",
      bg: "bg-[#FBBF24]/10",
      border: "border-[#FBBF24]/20",
    },
  ]

  const processSteps = [
    { num: "01", icon: Layers, title: "Company Details", desc: "Enter your organisation's basic information and industry context" },
    { num: "02", icon: BarChart3, title: "Barrier Assessment", desc: "Evaluate 15 key IoT adoption barriers across 4 categories" },
    { num: "03", icon: TrendingUp, title: "Cost & KPI Factors", desc: "Input financial metrics and performance indicators" },
    { num: "04", icon: FileBarChart2, title: "AI Report Generation", desc: "Receive your personalised ISRI readiness reports" },
  ]

  const stats = [
    { value: 15, suffix: "", label: "Barrier\nCategories", icon: Network },
    { value: 20, suffix: "", label: "Cost\nMetrics", icon: BarChart3 },
    { value: 17, suffix: "", label: "KPI\nIndicators", icon: TrendingUp },
    { value: 2, suffix: " PDFs", label: "Generated\nReports", icon: FileBarChart2 },
  ]

  const reportItems = [
    "Detailed analysis of all 15 IoT adoption barriers",
    "Impact Value scoring with financial quantification",
    "Cost factor analysis across 20 financial categories",
    "KPI impact assessment for 17 performance metrics",
    "AI-generated strategic recommendations per barrier",
    "Phased 18-month implementation roadmap",
    "Risk identification and mitigation strategies",
    "Top 3 priority barriers with full action plans",
  ]

  if (showForm) {
    return (
      <main className="min-h-screen bg-background">
        <div className="bg-dot-grid fixed inset-0 opacity-30 pointer-events-none" />
        <div className="relative container mx-auto px-4 py-8 max-w-5xl">
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
            <div className="mb-8">
              <button
                onClick={() => setShowForm(false)}
                className="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-primary mb-6 transition-colors group"
              >
                <ArrowLeft className="h-3.5 w-3.5 group-hover:-translate-x-0.5 transition-transform" />
                Back to overview
              </button>
              <div className="text-center">
                <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full badge-cyan mb-5 text-xs font-semibold tracking-wide uppercase">
                  <Sparkles className="h-3 w-3" />
                  ISRI Assessment
                </div>
                <h1 className="font-serif font-bold text-3xl sm:text-4xl text-foreground mb-2">
                  IoT Readiness Assessment
                </h1>
                <p className="text-muted-foreground max-w-xl mx-auto text-sm">
                  Complete all sections to generate your comprehensive ISRI report.
                </p>
              </div>
            </div>
            <ISRIAssessmentForm />
          </motion.div>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-background overflow-x-hidden">
      <Navbar onStart={() => setShowForm(true)} />

      {/* ── Hero ──────────────────────────────────────────────────────── */}
      <section className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden">
        {/* Background layers */}
        <div className="hero-glow absolute inset-0 pointer-events-none" />
        <div className="bg-dot-grid absolute inset-0 pointer-events-none opacity-40" />

        {/* Floating orbs */}
        <motion.div
          animate={{ y: [0, -18, 0], opacity: [0.4, 0.6, 0.4] }}
          transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
          className="absolute top-1/4 right-1/4 w-64 h-64 rounded-full blur-3xl pointer-events-none"
          style={{ background: "radial-gradient(circle, rgba(29,78,216,0.1) 0%, transparent 70%)" }}
        />
        <motion.div
          animate={{ y: [0, 14, 0], opacity: [0.3, 0.5, 0.3] }}
          transition={{ duration: 8, repeat: Infinity, ease: "easeInOut", delay: 2 }}
          className="absolute bottom-1/3 left-1/4 w-80 h-80 rounded-full blur-3xl pointer-events-none"
          style={{ background: "radial-gradient(circle, rgba(99,102,241,0.08) 0%, transparent 70%)" }}
        />

        <div className="relative z-10 max-w-5xl mx-auto px-6 text-center pt-20 pb-16">
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, scale: 0.85 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full badge-cyan mb-8 text-xs font-semibold tracking-widest uppercase"
          >
            <motion.div
              animate={{ scale: [1, 1.3, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="w-1.5 h-1.5 rounded-full bg-primary"
            />
            Indian SME IoT Readiness Index
          </motion.div>

          {/* Main heading */}
          <motion.h1
            initial={{ opacity: 0, y: 28 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.2 }}
            className="font-serif font-extrabold text-5xl sm:text-6xl md:text-7xl leading-[1.05] tracking-tight mb-6"
          >
            <span className="text-foreground">Is Your SME</span>
            <br />
            <span className="gradient-text">Ready for</span>
            <br />
            <span className="text-foreground">Industry 4.0?</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.35 }}
            className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto mb-10 leading-relaxed"
          >
            Get a comprehensive IoT adoption readiness report — including AI‑generated barrier analysis,
            cost impact scores, and a prioritised 18‑month strategic roadmap.
          </motion.p>

          {/* CTAs */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.45 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-20"
          >
            <button
              onClick={() => setShowForm(true)}
              className="group relative flex items-center gap-2.5 px-8 py-4 rounded-xl bg-primary text-primary-foreground font-semibold text-base shadow-lg shadow-primary/20 hover:shadow-primary/40 hover:scale-[1.02] active:scale-[0.98] transition-all duration-200"
            >
              <Zap className="h-4.5 w-4.5" />
              Begin Your Assessment
              <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
            </button>

            <button
              onClick={() => setShowForm(true)}
              className="flex items-center gap-2 px-8 py-4 rounded-xl border border-border hover:border-primary/30 bg-card/50 backdrop-blur text-foreground/80 hover:text-foreground font-medium text-base transition-all duration-200 hover:bg-card"
            >
              View Sample Report
              <ChevronRight className="h-4 w-4" />
            </button>
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.55 }}
            className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-3xl mx-auto"
          >
            {stats.map((s, i) => (
              <div
                key={i}
                className="glass-card rounded-2xl p-5 flex flex-col items-center text-center card-lift"
              >
                <s.icon className="h-4 w-4 text-primary mb-3 opacity-70" />
                <div className="mono text-3xl font-semibold text-foreground mb-1">
                  <AnimatedCounter value={s.value} suffix={s.suffix} />
                </div>
                <div className="text-[10px] text-muted-foreground leading-tight whitespace-pre-line tracking-wide uppercase">
                  {s.label}
                </div>
              </div>
            ))}
          </motion.div>
        </div>

        {/* Scroll indicator */}
        <motion.div
          animate={{ y: [0, 6, 0], opacity: [0.4, 0.8, 0.4] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-1"
        >
          <div className="w-px h-8 bg-gradient-to-b from-transparent to-primary/40" />
          <div className="w-1.5 h-1.5 rounded-full bg-primary/40" />
        </motion.div>
      </section>

      {/* ── How It Works ──────────────────────────────────────────────── */}
      <section className="relative py-24 sm:py-32">
        <div className="section-divider absolute top-0 left-0 right-0" />
        <div className="max-w-6xl mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center mb-16"
          >
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full badge-cyan mb-5 text-[10px] font-bold tracking-widest uppercase">
              Process
            </div>
            <h2 className="font-serif font-bold text-3xl sm:text-4xl md:text-5xl text-foreground mb-4">
              How It Works
            </h2>
            <p className="text-muted-foreground max-w-lg mx-auto">
              Four steps to your complete IoT readiness report
            </p>
          </motion.div>

          <div className="relative grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {/* Connector line (desktop) */}
            <div className="hidden lg:block absolute top-[52px] left-[calc(12.5%+20px)] right-[calc(12.5%+20px)] h-px bg-gradient-to-r from-primary/40 via-primary/20 to-primary/40 pointer-events-none" />

            {processSteps.map((step, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 24 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
                className="glass-card rounded-2xl p-6 card-lift relative"
              >
                {/* Step number + icon */}
                <div className="flex items-center justify-between mb-5">
                  <div className="w-11 h-11 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center">
                    <step.icon className="h-5 w-5 text-primary" />
                  </div>
                  <span className="mono text-4xl font-bold text-primary/10">{step.num}</span>
                </div>
                <h3 className="font-serif font-bold text-base text-foreground mb-2">{step.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{step.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Features ──────────────────────────────────────────────────── */}
      <section className="relative py-24 sm:py-32">
        <div className="section-divider absolute top-0 left-0 right-0" />
        <div
          className="absolute inset-0 pointer-events-none"
          style={{ background: "radial-gradient(ellipse 80% 60% at 50% 50%, rgba(29,78,216,0.04) 0%, transparent 70%)" }}
        />
        <div className="relative max-w-6xl mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center mb-16"
          >
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full badge-cyan mb-5 text-[10px] font-bold tracking-widest uppercase">
              Capabilities
            </div>
            <h2 className="font-serif font-bold text-3xl sm:text-4xl md:text-5xl text-foreground mb-4">
              What You Get
            </h2>
            <p className="text-muted-foreground max-w-lg mx-auto">
              A complete picture of your IoT adoption readiness
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 gap-5 max-w-4xl mx-auto">
            {features.map((f, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
                className={cn("glass-card rounded-2xl p-6 flex gap-5 card-lift border", f.border)}
              >
                <div className={cn("flex-shrink-0 w-12 h-12 rounded-xl flex items-center justify-center", f.bg)}>
                  <f.icon className={cn("h-5.5 w-5.5", f.color)} />
                </div>
                <div>
                  <h3 className={cn("font-serif font-bold text-base mb-2", f.color)}>{f.title}</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">{f.description}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Report Includes ───────────────────────────────────────────── */}
      <section className="relative py-24 sm:py-32">
        <div className="section-divider absolute top-0 left-0 right-0" />
        <div className="max-w-5xl mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <div className="glass-card rounded-3xl p-8 sm:p-12">
              <div className="grid md:grid-cols-2 gap-12 items-start">
                <div>
                  <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full badge-cyan mb-5 text-[10px] font-bold tracking-widest uppercase">
                    Deliverables
                  </div>
                  <h2 className="font-serif font-bold text-3xl sm:text-4xl text-foreground mb-4">
                    Your Report Includes
                  </h2>
                  <p className="text-muted-foreground leading-relaxed mb-8">
                    Two comprehensive PDF reports generated by our AI, tailored to your organisation's specific data and context.
                  </p>
                  <div className="flex flex-col sm:flex-row gap-4">
                    <div className="flex items-center gap-3 p-4 rounded-xl bg-primary/5 border border-primary/20">
                      <FileBarChart2 className="h-5 w-5 text-primary flex-shrink-0" />
                      <div>
                        <div className="text-sm font-semibold text-foreground">Barrier Analysis</div>
                        <div className="text-xs text-muted-foreground">All 15 barriers</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 p-4 rounded-xl bg-secondary/5 border border-secondary/20">
                      <MapPin className="h-5 w-5 text-secondary flex-shrink-0" />
                      <div>
                        <div className="text-sm font-semibold text-foreground">Strategic Roadmap</div>
                        <div className="text-xs text-muted-foreground">Top 3 priorities</div>
                      </div>
                    </div>
                  </div>
                </div>

                <ul className="space-y-3">
                  {reportItems.map((item, i) => (
                    <motion.li
                      key={i}
                      initial={{ opacity: 0, x: 16 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      viewport={{ once: true }}
                      transition={{ duration: 0.4, delay: i * 0.05 }}
                      className="flex items-start gap-3"
                    >
                      <CheckCircle className="h-4 w-4 text-secondary flex-shrink-0 mt-0.5" />
                      <span className="text-sm text-foreground/80 leading-relaxed">{item}</span>
                    </motion.li>
                  ))}
                </ul>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* ── CTA ────────────────────────────────────────────────────────── */}
      <section className="relative py-24 sm:py-32">
        <div className="section-divider absolute top-0 left-0 right-0" />
        <div
          className="absolute inset-0 pointer-events-none"
          style={{ background: "radial-gradient(ellipse 60% 80% at 50% 50%, rgba(29,78,216,0.06) 0%, transparent 70%)" }}
        />
        <div className="relative max-w-3xl mx-auto px-6 text-center">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7 }}
          >
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full badge-cyan mb-8 text-[10px] font-bold tracking-widest uppercase">
              Get Started
            </div>
            <h2 className="font-serif font-extrabold text-4xl sm:text-5xl md:text-6xl text-foreground mb-5 leading-tight">
              Ready to Begin Your{" "}
              <span className="gradient-text">Assessment?</span>
            </h2>
            <p className="text-muted-foreground text-lg mb-10 max-w-xl mx-auto leading-relaxed">
              Takes around 15–20 minutes. Your data is used solely to generate your report and is never shared.
            </p>
            <button
              onClick={() => setShowForm(true)}
              className="group relative inline-flex items-center gap-3 px-10 py-5 rounded-2xl bg-primary text-primary-foreground font-bold text-base shadow-xl shadow-primary/25 hover:shadow-primary/45 hover:scale-[1.03] active:scale-[0.98] transition-all duration-200 glow-cyan"
            >
              <Zap className="h-5 w-5" />
              Start Free Assessment
              <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
            </button>
            <p className="mt-5 text-xs text-muted-foreground/60">No registration required · Instant AI-powered results</p>
          </motion.div>
        </div>
      </section>

      {/* ── Footer ─────────────────────────────────────────────────────── */}
      <footer className="relative py-8 px-6">
        <div className="section-divider absolute top-0 left-0 right-0" />
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-muted-foreground/50">
          <div className="flex items-center gap-2">
            <Cpu className="h-3.5 w-3.5" />
            <span>ISRI Assessment Platform</span>
          </div>
          <span>© {new Date().getFullYear()} Indian SME IoT Readiness Index · Confidential</span>
        </div>
      </footer>
    </main>
  )
}
