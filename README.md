# CUTLINE

> **Autonomous Production-Planning Agent for Agentic Cinema: The Blockbuster Hackathon (Google Cloud, Parallel Track)**

CutLine turns a screenplay into a production plan that can survive reality. It investigates real-world constraints around a proposed shoot location and date window using live web research via **Parallel Search**, and maps those findings to individual screenplay requirements using **Gemini on Google Cloud** and a **deterministic production decision engine**.

---

## The Core Pipeline

```
SCREENPLAY (Text)
   ↓
[Stage 1: Screenplay Breakdown] (Gemini 3.6 Flash via google-genai)
   ↓ Structured scenes, settings, & production requirements
[Stage 2: Parallel Research Agent] (Parallel Search API via parallel-web)
   ↓ Targeted research across 5 mandatory categories
[Stage 3: Evidence Engine]
   ↓ Attaches verified web facts & URLs to specific scenes & requirements
[Stage 4: Production Decision Engine] (Deterministic Python Rules)
   ↓ Requirement -> Evidence -> Rule -> Consequence (GO / RISK / BLOCKED)
[Stage 5: Rewrite Strategist] (Gemini 3.6 Flash via google-genai)
   ↓ Actionable production rewrites for RISK/BLOCKED scenes
COMMAND CENTER UI (React + Plain CSS)
```

---

## Verifiable Runtime Integrations

This repository uses **Google Cloud Gemini** and **Parallel Search** actively at runtime. No prohibited AI providers (OpenAI, Anthropic, AWS, or Azure) are present in the codebase or dependency tree.

| Provider | SDK / Package | Runtime Calls in Code |
| :--- | :--- | :--- |
| **Google Cloud Gemini** | `google-genai` (v2.22.0+) | [`backend/services/gemini_analyzer.py`](backend/services/gemini_analyzer.py) (Line 50: `client.models.generate_content`) |
| **Parallel Web** | `parallel-web` (v1.3.3+) | [`backend/services/parallel_researcher.py`](backend/services/parallel_researcher.py) (Line 96: `client.search`) |

### Models Used
- **Gemini**: `gemini-3.6-flash` (with fallback to `gemini-3.5-flash` / `gemini-3.8-flash` on high demand) via Google GenAI API with forced Pydantic JSON schema output (`response_mime_type="application/json"`).
- **Parallel**: Official Parallel Search API (`mode="turbo"`) querying 5 canonical filming categories.

---

## The 5 Evidence Categories
1. **Filming/permit requirements** (turnaround timelines, municipal permit desks, fees)
2. **General location-type filming restrictions** (public piers, beaches, drone airspace, noise curfews)
3. **Seasonal/weather patterns** (tidal conditions, wind, fog, historical temperature)
4. **Public events and holidays** (festivals, marathons, street closures)
5. **General regional filming regulations** (fire safety officers, liability insurance thresholds)

---

## Getting Started

### 1. Prerequisites
- Python 3.11+ (Python 3.13 tested)
- API Keys: `GEMINI_API_KEY`, `PARALLEL_API_KEY`

### 2. Setup Virtual Environment
```bash
python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory:
```bash
GEMINI_API_KEY="your-gemini-api-key"
PARALLEL_API_KEY="your-parallel-api-key"
GEMINI_MODEL="gemini-3.6-flash"
```

### 4. Run Developer Verification Test
```bash
python tests/run_phase1_test.py
```

### 5. Run Backend API Server
```bash
uvicorn backend.main:app --reload --port 8000
```
- Health check: `http://localhost:8000/health`
- API docs: `http://localhost:8000/docs`

---

## License
[MIT License](LICENSE) — Copyright (c) 2026 CutLine Contributors.
