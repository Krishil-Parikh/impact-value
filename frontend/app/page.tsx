import { ISRIAssessmentForm } from "@/components/isri-assessment-form"

export default function Home() {
  return (
    <main className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-6 sm:py-8">
        <div className="text-center mb-8 sm:mb-12">
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-serif font-bold text-primary mb-3 sm:mb-4 text-balance px-2">
            ISRI Assessment Platform
          </h1>
          <p className="text-base sm:text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto text-pretty px-4">
            Evaluate your Indian SME's readiness for IoT adoption with our comprehensive assessment tool. Get AI-powered
            insights and strategic recommendations tailored to your business.
          </p>
        </div>
        <ISRIAssessmentForm />
      </div>
    </main>
  )
}
