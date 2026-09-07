"""
CutLine FastAPI Application
Provides endpoints for Phase 1 verification and production planning pipeline.
"""

import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.config import mask_secret, GEMINI_API_KEY, PARALLEL_API_KEY
from backend.schemas import (
    Phase1Request,
    Phase1Response,
    PipelineRequest,
    ProductionPlan,
)
from backend.pipeline import run_phase1_pipeline, run_complete_pipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("cutline.api")

app = FastAPI(
    title="CutLine API",
    description="Autonomous production-planning agent for Agentic Cinema Hackathon (Parallel track)",
    version="0.1.0",
)

# Enable CORS for local development and future web client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def sanitize_error_message(err: Exception) -> str:
    """Ensure raw exceptions never expose API keys or secrets in error responses."""
    msg = str(err)
    if GEMINI_API_KEY and GEMINI_API_KEY in msg:
        msg = msg.replace(GEMINI_API_KEY, mask_secret(GEMINI_API_KEY))
    if PARALLEL_API_KEY and PARALLEL_API_KEY in msg:
        msg = msg.replace(PARALLEL_API_KEY, mask_secret(PARALLEL_API_KEY))
    return msg


@app.get("/health")
def health_check():
    """Health check endpoint confirming API readiness and masked secret presence."""
    return {
        "status": "healthy",
        "service": "CutLine Production Planning Agent",
        "gemini_configured": bool(GEMINI_API_KEY),
        "gemini_key_masked": mask_secret(GEMINI_API_KEY),
        "parallel_configured": bool(PARALLEL_API_KEY),
        "parallel_key_masked": mask_secret(PARALLEL_API_KEY),
    }


@app.post("/api/phase1/analyze", response_model=Phase1Response)
def analyze_phase1(request: Phase1Request):
    """
    Phase 1 Test Endpoint:
    Processes screenplay with Stage 1 (Gemini) and runs Stage 2 (Parallel Search) across 5 categories.
    """
    try:
        logger.info(
            f"Received Phase 1 request for location '{request.location}' "
            f"({request.shoot_start_date} to {request.shoot_end_date})"
        )
        response = run_phase1_pipeline(request)
        return response
    except Exception as e:
        logger.exception("Error executing Phase 1 pipeline")
        raise HTTPException(status_code=500, detail=sanitize_error_message(e))


@app.post("/api/pipeline/run", response_model=ProductionPlan)
@app.post("/api/plan", response_model=ProductionPlan)
def run_production_pipeline(request: PipelineRequest):
    """
    Master 5-Stage Production Planning Endpoint:
    Runs Screenplay Breakdown -> Parallel Research -> Evidence Engine -> Decision Engine -> Rewrite Strategist.
    Returns complete frontend-ready ProductionPlan with verified evidence provenance and alternatives.
    """
    try:
        logger.info(
            f"Starting complete production pipeline for '{request.location}' "
            f"({request.shoot_start_date} to {request.shoot_end_date}) budget: ${request.budget:,.2f}"
        )
        plan = run_complete_pipeline(request)
        return plan
    except Exception as e:
        logger.exception("Error executing master production pipeline")
        raise HTTPException(status_code=500, detail=sanitize_error_message(e))


# Mount built frontend assets if dist directory exists (Cloud Run single-container support)
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))
if os.path.isdir(frontend_dist):
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/")
    def serve_frontend_root():
        """Serves the built CutLine command center frontend."""
        return FileResponse(os.path.join(frontend_dist, "index.html"))
