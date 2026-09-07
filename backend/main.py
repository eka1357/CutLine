"""
CutLine FastAPI Application
Provides endpoints for Phase 1 verification and production planning pipeline.
"""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.config import mask_secret, GEMINI_API_KEY, PARALLEL_API_KEY
from backend.schemas import Phase1Request, Phase1Response
from backend.pipeline import run_phase1_pipeline

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
        raise HTTPException(status_code=500, detail=str(e))
