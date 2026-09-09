# CUTLINE

> **Autonomous Production-Planning Agent for Agentic Cinema: The Blockbuster Hackathon (Google Cloud, Parallel Track)**

CutLine turns a screenplay into a production plan that can survive reality. It investigates real-world constraints around a proposed shoot location and date window using live web research via **Parallel Search**, and maps those findings to individual screenplay requirements using **Gemini on Google Cloud** and a **deterministic production decision engine**.

- **Live Application:** [https://cutline-27fg.onrender.com/](https://cutline-27fg.onrender.com/)
- **Demo Video:** *[Update with your YouTube demo URL]*

---

## The Problem CutLine Solves

Independent producers commit money and crew schedules before discovering that their shoot location has a permit lead-time they can't meet, a festival that closes the streets they need, or a noise curfew that blocks their night exterior. Discovering these late costs real money and real time.

**Concrete example:** A producer plans a 3-day exterior shoot on the Santa Monica Pier starting July 10. Without CutLine, they might not discover until arrival that:

- The City of Santa Monica requires commercial filming applications submitted 10+ business days in advance, with mandatory police and fire coordination
- The Independence Day holiday aftermath and summer festival season create partial pier closures and crowd conflicts during their window
- High surf advisories are historically common on the Southern California coast in mid-July, introducing equipment and actor safety hazards on the pier deck

CutLine surfaces all of these before a single dollar is spent on travel, crew, or equipment rental. Each finding is backed by a verifiable source URL from live Parallel Search, and flagged scenes receive concrete rewrite alternatives that preserve the director's cinematic intent.

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
| **Google Cloud Gemini** (Stage 1: Screenplay Breakdown) | `google-genai` (v2.22.0+) | [`backend/services/gemini_analyzer.py`](backend/services/gemini_analyzer.py#L50) (Line 50: `client.models.generate_content`) |
| **Parallel Web Search** (Stage 2: 5 Categories) | `parallel-web` (v1.3.3+) | [`backend/services/parallel_researcher.py`](backend/services/parallel_researcher.py#L131) (Line 131: `client.search`) |
| **Google Cloud Gemini** (Stage 5: Rewrite Strategist) | `google-genai` (v2.22.0+) | [`backend/services/rewrite_strategist.py`](backend/services/rewrite_strategist.py#L92) (Line 92: `client.models.generate_content`) |

### Models Used
- **Gemini**: `gemini-3.6-flash` (with automated fallback to `gemini-3.5-flash` / `gemini-3.7-flash` / `gemini-3.8-flash` on high demand) via Google GenAI API with forced Pydantic JSON schema output (`response_mime_type="application/json"`).
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

### 4. Build and Run the Application

#### Option A: Unified Self-Contained Server (Production Mode)
Build the React frontend and run FastAPI (which serves both the API and the Command Center UI at `/`):
```bash
# Build frontend
cd frontend
npm install
npm run build
cd ..

# Start unified server
uvicorn backend.main:app --port 8000
```
- Open Command Center: `http://localhost:8000/`
- Health check: `http://localhost:8000/health`
- Interactive API docs: `http://localhost:8000/docs`

#### Option B: Full-Stack Development Mode
Run backend and Vite dev server simultaneously:
```bash
# Terminal 1: Backend
uvicorn backend.main:app --reload --port 8000

# Terminal 2: Frontend Vite Dev Server
cd frontend
npm run dev
```
- Vite Dev Server runs at `http://localhost:3000/` with proxying to port 8000.

---

## Verification & Test Suites

```bash
# 1. Run 10-Scenario Adversarial Test Suite
python tests/test_phase2_adversarial.py

# 2. Run Master 5-Stage Live Pipeline Test
python tests/run_phase2_test.py

# 3. Run FastAPI Endpoint & Static Hosting Verification
python tests/test_api_endpoint.py
```

## Google Cloud Run Deployment

CutLine includes a multi-stage `Dockerfile` that packages both the built React frontend and the FastAPI backend into a single container:

```bash
# Deploy directly to Cloud Run using Google Cloud Build
gcloud run deploy cutline \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY="your-gemini-key",PARALLEL_API_KEY="your-parallel-key",GEMINI_MODEL="gemini-3.6-flash"
```

---

## License
[MIT License](LICENSE) | Copyright (c) 2026 CutLine Contributors.
