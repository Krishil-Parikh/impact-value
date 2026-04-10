import type React from "react"
import { Syne, DM_Sans, JetBrains_Mono } from "next/font/google"
import Script from "next/script"
import "./globals.css"
import { structuredData, faqSchema, serviceSchema } from "@/lib/seo-schema"

const syne = Syne({
  subsets: ["latin"],
  variable: "--font-syne",
  display: "swap",
  weight: ["400", "500", "600", "700", "800"],
})

const dmSans = DM_Sans({
  subsets: ["latin"],
  variable: "--font-dm-sans",
  display: "swap",
})

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains-mono",
  display: "swap",
  weight: ["400", "500", "600"],
})

export const metadata = {
  title: "ISRI Assessment Platform | IoT Readiness Assessment for Indian SMEs",
  description: "Comprehensive Indian SME Readiness Index assessment for IoT adoption. Get AI-powered analysis, strategic roadmaps, and barrier evaluations. Perfect for manufacturing and technology businesses.",
  keywords: "IoT readiness, SME assessment, Industry 4.0, ISRI, Indian businesses, digital transformation",
  authors: [{ name: "ISRI Platform" }],
  creator: "ISRI Team",
  publisher: "ISRI Platform",
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  openGraph: {
    type: "website",
    url: "https://impact-value.vercel.app",
    title: "ISRI Assessment Platform | IoT Readiness Assessment for Indian SMEs",
    description: "Evaluate your SME's readiness for IoT adoption with comprehensive AI-powered analysis and strategic recommendations.",
    images: [
      {
        url: "https://impact-value.vercel.app/og-image.png",
        width: 1200,
        height: 630,
        alt: "ISRI Assessment Platform",
        type: "image/png",
      },
    ],
    locale: "en_IN",
    siteName: "ISRI Assessment Platform",
  },
  twitter: {
    card: "summary_large_image",
    title: "ISRI Assessment Platform | IoT Readiness Assessment for Indian SMEs",
    description: "Evaluate your SME's readiness for IoT adoption with AI-powered analysis.",
    images: ["https://impact-value.vercel.app/og-image.png"],
    creator: "@ISRIAssessment",
  },
  verification: {
    google: "google-site-verification-code",
  },
  robots: {
    index: true,
    follow: true,
    nocache: false,
    googleBot: {
      index: true,
      follow: true,
      noimageindex: false,
      "max-snippet": -1,
      "max-image-preview": "large",
      "max-video-preview": -1,
    },
  },
  alternates: {
    canonical: "https://impact-value.vercel.app",
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${syne.variable} ${dmSans.variable} ${jetbrainsMono.variable} antialiased`}>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        <link rel="canonical" href="https://impact-value.vercel.app" />

        {/* Structured Data - JSON-LD */}
        <Script
          id="organization-schema"
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
        />
        <Script
          id="faq-schema"
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
        />
        <Script
          id="service-schema"
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(serviceSchema) }}
        />

        {/* Google Analytics */}
        <Script src="https://www.googletagmanager.com/gtag/js?id=YOUR_GA_ID" strategy="afterInteractive" />
        <Script
          id="google-analytics"
          strategy="afterInteractive"
          dangerouslySetInnerHTML={{
            __html: `window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','YOUR_GA_ID');`,
          }}
        />
      </head>
      <body className="min-h-screen bg-background text-foreground">{children}</body>
    </html>
  )
}
