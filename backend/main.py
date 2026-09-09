"""
CutLine FastAPI Application
Provides endpoints for Phase 1 verification, production planning pipeline,
and real-time SSE streaming for live pipeline progress.
"""

import os
import re
import json
import queue
import logging
import threading
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse

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


def _parse_stage_from_message(msg: str) -> int:
    """Extract stage number from pipeline log messages."""
    if "STAGE 1" in msg or "SCREENPLAY" in msg.upper() and "STAGE" not in msg.upper():
        return 1
    if "STAGE 2" in msg or "PARALLEL" in msg.upper():
        return 2
    if "STAGE 3" in msg or "EVIDENCE ENGINE" in msg.upper():
        return 3
    if "STAGE 4" in msg or "DECISION ENGINE" in msg.upper():
        return 4
    if "STAGE 5" in msg or "REWRITE" in msg.upper():
        return 5
    # Check for "Parallel search [n/5]" pattern (still stage 2)
    if re.search(r"Parallel search \[\d+/\d+\]", msg):
        return 2
    # Check for generic stage mentions
    stage_match = re.search(r"STAGE (\d)", msg)
    if stage_match:
        return int(stage_match.group(1))
    return 0


@app.api_route("/health", methods=["GET", "HEAD"])
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


@app.post("/api/pipeline/stream")
async def stream_production_pipeline(request: PipelineRequest):
    """
    Real-time SSE streaming endpoint for the 5-stage production pipeline.
    Sends live step progress events as each pipeline stage executes,
    enabling the frontend to show real-time search category names and stage transitions.
    """
    event_queue: queue.Queue = queue.Queue()

    def step_callback(msg: str):
        """Called by the pipeline for each progress step; enqueues an SSE event."""
        stage = _parse_stage_from_message(msg)
        event_queue.put(("step", {"stage": stage, "message": msg}))

    def pipeline_worker():
        """Runs the synchronous pipeline in a background thread."""
        try:
            plan = run_complete_pipeline(request, step_callback=step_callback)
            event_queue.put(("complete", plan.model_dump()))
        except Exception as e:
            logger.exception("SSE pipeline execution error")
            event_queue.put(("error", {"message": sanitize_error_message(e)}))

    # Start pipeline in a background thread
    worker = threading.Thread(target=pipeline_worker, daemon=True)
    worker.start()

    async def event_generator():
        """Yields SSE-formatted events from the pipeline queue."""
        import asyncio
        while True:
            try:
                # Poll queue without blocking the event loop
                event_type, data = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: event_queue.get(timeout=1.0)
                )
                payload = json.dumps(data, default=str)
                yield f"event: {event_type}\ndata: {payload}\n\n"

                if event_type in ("complete", "error"):
                    break
            except queue.Empty:
                # Send keepalive comment to prevent connection timeout
                yield ": keepalive\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# Mount built frontend assets if dist directory exists (Cloud Run single-container support)
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))
if os.path.isdir(frontend_dist):
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.api_route("/", methods=["GET", "HEAD"])
    def serve_frontend_root():
        """Serves the built CutLine command center frontend."""
        return FileResponse(os.path.join(frontend_dist, "index.html"))

    @app.get("/cutline.svg")
    def serve_cutline_favicon():
        """Serves the CutLine SVG favicon."""
        svg_path = os.path.join(frontend_dist, "cutline.svg")
        if os.path.isfile(svg_path):
            return FileResponse(svg_path, media_type="image/svg+xml")
        raise HTTPException(status_code=404, detail="Favicon not found")
