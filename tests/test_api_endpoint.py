"""
Test FastAPI Endpoints (TestClient)
Verifies:
1. GET /health returns status and masked secret confirmations.
2. POST /api/phase1/analyze processes payload and returns validated Phase1Response.
"""

import sys
import os

# Ensure UTF-8 output encoding for terminal on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from backend.main import app
from tests.test_original_screenplay import (
    NEON_DRIFTWOOD_SCREENPLAY,
    TEST_LOCATION,
    TEST_START_DATE,
    TEST_END_DATE,
    TEST_BUDGET,
)

client = TestClient(app)


def test_health():
    print("Testing GET /health ...")
    response = client.get("/health")
    assert response.status_code == 200, f"Health check failed: {response.text}"
    data = response.json()
    assert data["status"] == "healthy"
    assert data["gemini_configured"] is True
    assert data["parallel_configured"] is True
    assert "****" in data["gemini_key_masked"] or "..." in data["gemini_key_masked"]
    assert "****" in data["parallel_key_masked"] or "..." in data["parallel_key_masked"]
    print(" [PASS] /health endpoint healthy and secrets properly masked.")


def test_phase1_analyze():
    print("\nTesting POST /api/phase1/analyze ...")
    payload = {
        "screenplay": NEON_DRIFTWOOD_SCREENPLAY,
        "location": TEST_LOCATION,
        "shoot_start_date": TEST_START_DATE,
        "shoot_end_date": TEST_END_DATE,
        "budget": TEST_BUDGET,
    }
    response = client.post("/api/phase1/analyze", json=payload)
    assert response.status_code == 200, f"API analyze failed: {response.text}"
    data = response.json()
    assert data["status"] == "success"
    assert len(data["screenplay_analysis"]["scenes"]) >= 2
    assert len(data["research_facts"]) >= 5
    assert len(data["category_summary"]) == 5
    print(" [PASS] /api/phase1/analyze returned 200 with full Phase 1 payload!")


def test_pipeline_run():
    print("\nTesting POST /api/pipeline/run (Master Pipeline Endpoint) ...")
    payload = {
        "screenplay": NEON_DRIFTWOOD_SCREENPLAY,
        "location": TEST_LOCATION,
        "shoot_start_date": TEST_START_DATE,
        "shoot_end_date": TEST_END_DATE,
        "budget": TEST_BUDGET,
    }
    response = client.post("/api/pipeline/run", json=payload)
    assert response.status_code == 200, f"Pipeline run failed: {response.text}"
    data = response.json()
    assert "project_title" in data
    assert data["overall_decision"] in ("GO", "RISK", "BLOCKED")
    assert len(data["scenes"]) >= 2
    assert len(data["all_evidence"]) > 0

    scene_1 = next(s for s in data["scenes"] if "SCENE_1" in s["scene_id"])
    assert scene_1["decision"] == "GO"

    scene_2 = next(s for s in data["scenes"] if "SCENE_2" in s["scene_id"])
    assert scene_2["decision"] in ("RISK", "BLOCKED")
    assert len(scene_2["alternatives"]) >= 2
    print(" [PASS] /api/pipeline/run returned 200 with full master ProductionPlan!")


def test_frontend_root():
    print("\nTesting GET / (Frontend Static Root) ...")
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "CUTLINE" in response.text
    print(" [PASS] GET / serves built CutLine command center frontend HTML!")


def test_cutline_svg():
    print("\nTesting GET /cutline.svg (Favicon Endpoint) ...")
    response = client.get("/cutline.svg")
    assert response.status_code == 200
    assert "image/svg+xml" in response.headers.get("content-type", "")
    assert "<svg" in response.text
    print(" [PASS] GET /cutline.svg serves CutLine branded SVG favicon!")


if __name__ == "__main__":
    test_health()
    test_frontend_root()
    test_cutline_svg()
    test_phase1_analyze()
    test_pipeline_run()
