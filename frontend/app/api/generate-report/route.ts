import { type NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  try {
    const formData = await request.json()

    // Transform the form data to match the backend API structure
    const apiPayload = {
      company_details: formData.company_details,
      barrier1: formData.barriers.barrier1,
      barrier2: formData.barriers.barrier2,
      barrier3: formData.barriers.barrier3,
      barrier4: formData.barriers.barrier4,
      barrier5: formData.barriers.barrier5,
      barrier6: formData.barriers.barrier6,
      barrier7: formData.barriers.barrier7,
      barrier8: formData.barriers.barrier8,
      barrier9: formData.barriers.barrier9,
      barrier10: formData.barriers.barrier10,
      barrier11: formData.barriers.barrier11,
      barrier12: formData.barriers.barrier12,
      barrier13: formData.barriers.barrier13,
      barrier14: formData.barriers.barrier14,
      barrier15: formData.barriers.barrier15,
      cost_factor_inputs: formData.cost_factor_inputs,
      kpi_factor_inputs: formData.kpi_factor_inputs,
    }

    // Make request to the Python FastAPI backend
    const response = await fetch("https://impact-value-1.onrender.com/generate_full_report", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(apiPayload),
    })

    if (!response.ok) {
      throw new Error(`Backend API error: ${response.status}`)
    }

    // Get the ZIP file as a blob
    const blob = await response.blob()

    // Return the blob as a response
    return new NextResponse(blob, {
      headers: {
        "Content-Type": "application/x-zip-compressed",
        "Content-Disposition": 'attachment; filename="ISRI_AI_Reports.zip"',
      },
    })
  } catch (error) {
    console.error("Error generating report:", error)
    return NextResponse.json({ error: "Failed to generate report" }, { status: 500 })
  }
}
