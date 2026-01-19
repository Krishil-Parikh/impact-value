export const structuredData = {
  "@context": "https://schema.org",
  "@type": "Organization",
  name: "ISRI Assessment Platform",
  url: "https://impact-value.vercel.app",
  logo: "https://impact-value.vercel.app/logo.png",
  description: "Comprehensive Indian SME Readiness Index assessment for IoT adoption",
  sameAs: [
    "https://twitter.com/ISRIAssessment",
    "https://www.linkedin.com/company/isri-assessment",
  ],
  contactPoint: {
    "@type": "ContactPoint",
    contactType: "Customer Support",
    telephone: "+91-XXXXXX",
    email: "support@isri-assessment.com",
  },
}

export const faqSchema = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  mainEntity: [
    {
      "@type": "Question",
      name: "How long does the ISRI assessment take?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "The assessment typically takes 15-20 minutes to complete all sections.",
      },
    },
    {
      "@type": "Question",
      name: "What do I get after completing the assessment?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "You receive a comprehensive report with detailed scores, analysis across 15 barriers, and AI-powered strategic roadmap tailored to your business.",
      },
    },
    {
      "@type": "Question",
      name: "Is my data secure with ISRI?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "Yes, we use enterprise-grade encryption and comply with all data protection regulations including GDPR and India's data protection standards.",
      },
    },
    {
      "@type": "Question",
      name: "Can I retake the assessment?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "Absolutely! You can retake the assessment anytime to track your progress and measure improvements in your IoT readiness.",
      },
    },
  ],
}

export const serviceSchema = {
  "@context": "https://schema.org",
  "@type": "Service",
  name: "ISRI Assessment Platform",
  description: "Comprehensive IoT readiness assessment for Indian SMEs",
  provider: {
    "@type": "Organization",
    name: "ISRI Assessment Platform",
  },
  areaServed: "IN",
  serviceType: "Business Assessment",
  offers: {
    "@type": "Offer",
    price: "0",
    priceCurrency: "INR",
    availability: "https://schema.org/InStock",
  },
}
