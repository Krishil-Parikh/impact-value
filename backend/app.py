"""
Main FastAPI application
Centralized endpoint for ISRI calculation and report generation
Using OpenRouter API for AI-powered analysis
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse, Response
from fastapi.middleware.cors import CORSMiddleware
import io
import zipfile
import asyncio
import json
import os
from typing import Dict, List
from datetime import datetime
import pdfplumber

from models.input_models import ComprehensiveInput
from services.barrier_service import calculate_barrier_scores
from services.cost_service import calculate_cost_factor_scores
from services.kpi_service import calculate_kpi_scores
from services.isri_service import calculate_impact_values, get_top_n_barriers
from services.ai_service import generate_comprehensive_barrier_analysis, generate_strategic_roadmap
from utils.pdf_utils import create_pdf_from_markdown
from config.settings import OUTPUT_DIR, BARRIER_ANALYSIS_DIR

# Get CORS origins from environment variable
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

# Store for tracking report generation status
report_status: Dict[str, Dict] = {}

# Initialize FastAPI app
app = FastAPI(
    title="ISRI Calculation and Reporting API",
    description="Indian SME Readiness Index (ISRI) calculation with AI-powered analysis and strategic roadmaps",
    version="3.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def generate_reports_background(session_id: str, inputs: ComprehensiveInput):
    """Background task to generate reports with progress tracking"""
    try:
        report_status[session_id] = {
            "status": "processing",
            "progress": 5,
            "message": "Initializing report generation...",
            "comprehensive_pdf": None,
            "roadmap_pdf": None,
            "error": None
        }
        
        # Extract company details
        company_details = inputs.company_details.dict()
        
        # Prepare barriers dictionary
        barriers = {
            f"barrier{i}": getattr(inputs, f"barrier{i}")
            for i in range(1, 16)
        }
        
        # STEP 1: Calculate barrier scores
        report_status[session_id]["progress"] = 15
        report_status[session_id]["message"] = "Calculating barrier scores..."
        barrier_scores = calculate_barrier_scores(barriers)
        
        # STEP 2: Calculate cost factor scores
        report_status[session_id]["progress"] = 25
        report_status[session_id]["message"] = "Calculating cost impacts..."
        cost_scores = calculate_cost_factor_scores(inputs.cost_factor_inputs)
        
        # STEP 3: Calculate KPI scores
        report_status[session_id]["progress"] = 35
        report_status[session_id]["message"] = "Calculating KPI impacts..."
        kpi_scores = calculate_kpi_scores(inputs.kpi_factor_inputs)
        
        # STEP 4: Calculate impact values
        report_status[session_id]["progress"] = 45
        report_status[session_id]["message"] = "Computing impact values..."
        impact_values = calculate_impact_values(barrier_scores, cost_scores, kpi_scores)
        
        # STEP 5: Generate comprehensive analysis
        report_status[session_id]["progress"] = 50
        report_status[session_id]["message"] = "Generating comprehensive barrier analysis (AI)..."
        comprehensive_analysis = await generate_comprehensive_barrier_analysis(
            company_details=company_details,
            barrier_scores=barrier_scores,
            impact_values=impact_values
        )
        
        # STEP 6: Convert comprehensive analysis to PDF
        report_status[session_id]["progress"] = 60
        report_status[session_id]["message"] = "Converting comprehensive analysis to PDF..."
        analysis_pdf = create_pdf_from_markdown(
            markdown_content=comprehensive_analysis,
            report_title="Comprehensive Barrier Analysis Report"
        )
        report_status[session_id]["comprehensive_pdf"] = analysis_pdf
        report_status[session_id]["message"] = "✅ Comprehensive analysis ready"
        
        # STEP 7: Get top 3 barriers
        report_status[session_id]["progress"] = 70
        report_status[session_id]["message"] = "Identifying top 3 critical barriers..."
        top_3_barriers = get_top_n_barriers(impact_values, n=3)
        
        # STEP 8: Generate strategic roadmap
        report_status[session_id]["progress"] = 80
        report_status[session_id]["message"] = "Generating strategic roadmap (AI)..."
        strategic_roadmap = await generate_strategic_roadmap(
            company_details=company_details,
            top_barriers=top_3_barriers,
            barrier_scores=barrier_scores
        )
        
        # STEP 9: Convert roadmap to PDF
        report_status[session_id]["progress"] = 90
        report_status[session_id]["message"] = "Converting strategic roadmap to PDF..."
        roadmap_pdf = create_pdf_from_markdown(
            markdown_content=strategic_roadmap,
            report_title="Strategic Roadmap Report"
        )
        report_status[session_id]["roadmap_pdf"] = roadmap_pdf
        
        # Done!
        report_status[session_id]["status"] = "completed"
        report_status[session_id]["progress"] = 100
        report_status[session_id]["message"] = "✅ All reports generated successfully"
        
    except Exception as e:
        report_status[session_id]["status"] = "error"
        report_status[session_id]["error"] = str(e)
        report_status[session_id]["message"] = f"Error: {str(e)}"

def extract_pdf_text(file_path: str) -> str:
    """Extract plain text from a PDF using pdfplumber."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF not found at {file_path}")
    pages: list[str] = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            pages.append(text)
    return "\n\n".join(pages)

@app.post("/generate_report_async", summary="Start async report generation")
async def generate_report_async(inputs: ComprehensiveInput, background_tasks: BackgroundTasks):
    """
    Start async report generation and return session ID for tracking
    Frontend can poll /status/{session_id} to check progress
    """
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    # Start background task
    background_tasks.add_task(generate_reports_background, session_id, inputs)
    
    return {
        "session_id": session_id,
        "message": "Report generation started",
        "status_url": f"/status/{session_id}"
    }


@app.get("/status/{session_id}", summary="Check report generation status")
async def get_status(session_id: str):
    """Get the current status of report generation"""
    if session_id not in report_status:
        raise HTTPException(status_code=404, detail="Session not found")
    
    status_data = report_status[session_id].copy()
    # Don't send the PDF data in status check, just indicate if ready
    status_data["comprehensive_ready"] = status_data.pop("comprehensive_pdf") is not None
    status_data["roadmap_ready"] = status_data.pop("roadmap_pdf") is not None
    
    return status_data


@app.get("/download/{session_id}/comprehensive", summary="Download comprehensive analysis PDF")
async def download_comprehensive(session_id: str):
    """Download the comprehensive analysis PDF"""
    if session_id not in report_status:
        raise HTTPException(status_code=404, detail="Session not found")
    
    pdf_data = report_status[session_id].get("comprehensive_pdf")
    if not pdf_data:
        raise HTTPException(status_code=404, detail="PDF not ready yet")
    
    return Response(
        content=pdf_data,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=Comprehensive_Barrier_Analysis.pdf"}
    )


@app.get("/download/{session_id}/roadmap", summary="Download strategic roadmap PDF")
async def download_roadmap(session_id: str):
    """Download the strategic roadmap PDF"""
    if session_id not in report_status:
        raise HTTPException(status_code=404, detail="Session not found")
    
    pdf_data = report_status[session_id].get("roadmap_pdf")
    if not pdf_data:
        raise HTTPException(status_code=404, detail="PDF not ready yet")
    
    return Response(
        content=pdf_data,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=Strategic_Roadmap_Top_3.pdf"}
    )


@app.post("/strategic_plan_from_pdfs", summary="Generate strategic plan using existing barrier PDFs")
async def strategic_plan_from_pdfs(payload: Dict[str, List[int]]):
    """
    Build a strategic plan using text extracted from pre-generated barrier_analysis PDFs.
    This avoids re-running any calculations and only consumes existing PDF content.
    Request body: {"barrier_ids": [int, int, int]} (defaults to top 3 IDs [1,2,3]).
    """
    barrier_ids = payload.get("barrier_ids") or [1, 2, 3]
    sections: list[str] = []

    for bid in barrier_ids:
        file_path = os.path.join(BARRIER_ANALYSIS_DIR, f"barrier_{bid}_report.pdf")
        try:
            text = extract_pdf_text(file_path)
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to read PDF for barrier {bid}: {e}")

        sections.append(f"## Barrier {bid} Strategic Insights\n\n{text}")

    markdown_content = "\n\n---\n\n".join(sections)
    try:
        pdf_bytes = create_pdf_from_markdown(markdown_content, "Strategic Plan From PDFs")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate strategic plan PDF: {e}")

    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=Strategic_Plan_From_PDFs.pdf"},
    )


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "ISRI API is running",
        "version": "3.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "ai_service": "configured"
    }


@app.post("/generate_full_report", summary="Generate complete ISRI analysis with AI reports")
async def generate_full_report(inputs: ComprehensiveInput):
    """
    Complete ISRI analysis endpoint that:
    1. Calculates barrier scores for all 15 barriers
    2. Calculates cost factor impacts
    3. Calculates KPI factor impacts
    4. Computes final impact values (ISRI)
    5. Generates comprehensive AI barrier analysis for ALL 15 barriers
    6. Identifies top 3 critical barriers
    7. Generates detailed strategic roadmap for top 3 barriers
    8. Returns both reports as PDFs in a ZIP file
    
    Args:
        inputs: ComprehensiveInput model containing all company, barrier, cost, and KPI data
    
    Returns:
        ZIP file containing:
        - Comprehensive_Barrier_Analysis.pdf (all 15 barriers)
        - Strategic_Roadmap_Top_3.pdf (detailed roadmap for top 3)
    """
    try:
        # Extract company details
        company_details = inputs.company_details.dict()
        
        # Prepare barriers dictionary for calculation
        barriers = {
            "barrier1": inputs.barrier1,
            "barrier2": inputs.barrier2,
            "barrier3": inputs.barrier3,
            "barrier4": inputs.barrier4,
            "barrier5": inputs.barrier5,
            "barrier6": inputs.barrier6,
            "barrier7": inputs.barrier7,
            "barrier8": inputs.barrier8,
            "barrier9": inputs.barrier9,
            "barrier10": inputs.barrier10,
            "barrier11": inputs.barrier11,
            "barrier12": inputs.barrier12,
            "barrier13": inputs.barrier13,
            "barrier14": inputs.barrier14,
            "barrier15": inputs.barrier15,
        }
        
        # STEP 1: Calculate barrier scores for all 15 barriers
        print("📊 Calculating barrier scores...")
        barrier_scores = calculate_barrier_scores(barriers)
        
        # STEP 2: Calculate cost factor scores
        print("💰 Calculating cost factor scores...")
        cost_scores = calculate_cost_factor_scores(inputs.cost_factor_inputs)
        
        # STEP 3: Calculate KPI scores
        print("📈 Calculating KPI scores...")
        kpi_scores = calculate_kpi_scores(inputs.kpi_factor_inputs)
        
        # STEP 4: Calculate impact values (ISRI)
        print("🎯 Calculating impact values...")
        impact_values = calculate_impact_values(barrier_scores, cost_scores, kpi_scores)
        
        # STEP 5: Generate comprehensive barrier analysis for ALL 15 barriers
        print("🤖 Generating comprehensive barrier analysis (all 15 barriers)...")
        comprehensive_analysis = await generate_comprehensive_barrier_analysis(
            company_details=company_details,
            barrier_scores=barrier_scores,
            impact_values=impact_values
        )
        
        # STEP 6: Get top 3 barriers by impact value
        print("🔝 Identifying top 3 critical barriers...")
        top_3_barriers = get_top_n_barriers(impact_values, n=3)
        
        # Print top 3 for logging
        print("\nTop 3 Critical Barriers:")
        for rank, (barrier_key, data) in enumerate(top_3_barriers, 1):
            print(f"  {rank}. {data['barrier_name']} - Impact: {data['impact_value']:.4f}")
        
        # STEP 7: Generate strategic roadmap for top 3 barriers
        print("\n🗺️ Generating strategic roadmap (top 3 barriers)...")
        strategic_roadmap = await generate_strategic_roadmap(
            company_details=company_details,
            top_barriers=top_3_barriers,
            barrier_scores=barrier_scores
        )
        
        # STEP 8: Convert reports to PDFs
        print("📄 Converting reports to PDFs...")
        try:
            analysis_pdf = create_pdf_from_markdown(
                markdown_content=comprehensive_analysis,
                report_title="Comprehensive Barrier Analysis Report"
            )
            
            roadmap_pdf = create_pdf_from_markdown(
                markdown_content=strategic_roadmap,
                report_title="Strategic Roadmap Report"
            )
        except Exception as pdf_error:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate PDFs: {str(pdf_error)}"
            )
        
        # STEP 9: Create ZIP file containing both PDFs
        print("📦 Creating ZIP archive...")
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("01_Comprehensive_Barrier_Analysis.pdf", analysis_pdf)
            zf.writestr("02_Strategic_Roadmap_Top_3_Barriers.pdf", roadmap_pdf)
        
        zip_buffer.seek(0)
        
        print("✅ Report generation complete!")
        
        # Return ZIP file
        return StreamingResponse(
            iter([zip_buffer.read()]),
            media_type="application/x-zip-compressed",
            headers={
                'Content-Disposition': f'attachment; filename="ISRI_Analysis_{company_details.get("company_name", "Report").replace(" ", "_")}.zip"'
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Validation error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/barrier-definitions")
async def get_barrier_definitions():
    """
    Get definitions and metadata for all 15 barriers
    Useful for frontend to display barrier information
    """
    barrier_names = [
        "Lack of training for workers and managers",
        "Resistance to change",
        "Lack of digital culture and training",
        "Higher investment in employees' training.",
        "Lack of knowledge management systems",
        "Regulatory compliance issues",
        "Lack of Standards and Reference Architecture",
        "Lack of Internet coverage and IT facilities",
        "Limited Access to Funding and Credit",
        "Future viability & profitability",
        "Dependency on External Vendors",
        "High Implementation Cost",
        "Compliance with Sector-Specific Regulations",
        "Lack of Regulations and Standards",
        "Customers are hesitant to share data"
    ]
    
    return {
        "total_barriers": 15,
        "barriers": [
            {"id": i+1, "name": name}
            for i, name in enumerate(barrier_names)
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
