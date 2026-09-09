# CUTLINE

> **Autonomous Production-Planning Agent for Agentic Cinema: The Blockbuster Hackathon (Google Cloud, Parallel Track)**

[![Live Application](https://img.shields.io/badge/Live%20Application-Render-00c853?style=for-the-badge&logo=render&logoColor=white)](https://cutline-27fg.onrender.com/)
[![Track](https://img.shields.io/badge/Hackathon%20Track-Parallel%20Track-3b82f6?style=for-the-badge)](https://cutline-27fg.onrender.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Google Cloud Gemini](https://img.shields.io/badge/AI-Gemini%203.6%20Flash%20(Google%20Cloud)-4285f4?style=for-the-badge&logo=googlecloud&logoColor=white)](https://cloud.google.com/)
[![Parallel Search](https://img.shields.io/badge/Search%20Engine-Parallel%20Search%20SDK-6366f1?style=for-the-badge)](https://parallel.ai/)

CutLine turns a screenplay into a production plan that can survive reality. It investigates real-world constraints around a proposed shoot location and date window using live web research via **Parallel Search**, and maps those findings to individual screenplay requirements using **Gemini on Google Cloud** and a **deterministic production decision engine**.

- **Live Application:** [https://cutline-27fg.onrender.com/](https://cutline-27fg.onrender.com/)
- **Demo Video:** *[Update with your YouTube demo URL]*
- **Official Demo Script:** [`DEMO_SCRIPT.md`](DEMO_SCRIPT.md)

---

## Executive Summary for Hackathon Judges

### What Problem Does CutLine Solve?
Independent filmmakers routinely commit hundreds of thousands of dollars to production dates, crew travel, and gear rentals before discovering municipal restrictions, permit lead times, seasonal hazards, or street closures. Discovering these on shoot day halts production and costs upwards of $10,000 an hour. 

### Why CutLine Stands Apart from Typical LLM Wrappers
1. **Active Parallel Search at Runtime (Not a Claim):** CutLine actively calls the official `parallel-web` Python SDK across **five discrete regulatory and environmental categories** per run. Every finding carries a verifiable municipal citation and verbatim excerpt.
2. **Zero-Hallucination Deterministic Decision Engine:** Most AI tools guess feasibility or hallucinate arbitrary percentages (e.g., "84% feasible"). CutLine evaluates evidence using a **deterministic Python rule engine** outputting:
   $$\text{Requirement} \longrightarrow \text{Evidence} \longrightarrow \text{Rule} \longrightarrow \text{Consequence (GO / RISK / BLOCKED)}$$
3. **Actionable Rewrites (Not Just a Warning Report):** When a scene is flagged `BLOCKED` or `RISK`, Stage 5 (*Rewrite Strategist*) deploys Gemini to generate three concrete operational pivots and drafts a **director-ready screenplay excerpt** preserving dramatic stakes while bypassing the legal or physical obstacle.
4. **Aesthetic Discipline:** Built as a real film production command center with monospace telemetry, clickable provenance drawer, and zero generic AI fluff (no loud gradients, no fake bento boxes, no decorative emojis).

---

## 5-Stage Agentic Architecture

```
                       SCREENPLAY TEXT & SHOOT PARAMETERS
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STAGE 1: Screenplay Breakdown (Gemini 3.6 Flash via google-genai)            │
│ Extracts structured scenes, location types, times of day, & risk vectors    │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STAGE 2: Parallel Research Agent (parallel-web SDK runtime)                 │
│ Concurrent live searches across 5 bounded regulatory & environmental vectors │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STAGE 3: Evidence Engine (Provenance & Grounding)                           │
│ Maps verified web claims & source URLs directly to affected scene specs     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STAGE 4: Production Decision Engine (Deterministic Python Rules)            │
│ Requirement -> Evidence -> Rule -> Consequence [GO / RISK / BLOCKED]        │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STAGE 5: Rewrite Strategist (Gemini 3.6 Flash via google-genai)             │
│ Generates 3 operational pivots + director-ready screenplay draft excerpt    │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
                         PRODUCTION COMMAND CENTER UI
```

---

## Verifiable Runtime Integrations (Code Audit Guide)

This repository strictly complies with the hackathon rules. Tooling is restricted to **Google Cloud Gemini** and the **Parallel Search SDK**. No prohibited AI SDKs (OpenAI, Anthropic, AWS, or Azure) exist in the codebase.

| Component | Technology | Source File & Runtime Lines |
| :--- | :--- | :--- |
| **Stage 1: Screenplay Breakdown** | `google-genai` (v2.22.0+) | [`backend/services/gemini_analyzer.py`](backend/services/gemini_analyzer.py#L50)<br>`client.models.generate_content(...)` with Pydantic JSON schema |
| **Stage 2: Parallel Web Research** | `parallel-web` (v1.3.3+) | [`backend/services/parallel_researcher.py`](backend/services/parallel_researcher.py#L131)<br>`client.search(...)` called across 5 dedicated categories |
| **Stage 3: Evidence Engine** | Pure Python Logic | [`backend/services/evidence_engine.py`](backend/services/evidence_engine.py)<br>Links facts to scenes; enforces strict source URL presence |
| **Stage 4: Decision Engine** | Deterministic Python Rules | [`backend/services/decision_engine.py`](backend/services/decision_engine.py)<br>10/10 adversarial rules evaluated without LLM guesswork |
| **Stage 5: Rewrite Strategist** | `google-genai` (v2.22.0+) | [`backend/services/rewrite_strategist.py`](backend/services/rewrite_strategist.py#L92)<br>`client.models.generate_content(...)` with structured schemas |

---

## The 5 Grounded Evidence Categories

To guarantee reliability and prevent open-web hallucinations, CutLine restricts live Parallel searches strictly to five verifiable categories:

1. **Municipal Filming & Permit Lead-Time Requirements:** Turnaround timelines, municipal permit desk procedures, and non-refundable fees.
2. **Location-Type Filming Restrictions:** Regulations governing public piers, beaches, drone airspace (FAA Part 107), and municipal curfews.
3. **Seasonal & Marine Weather Patterns:** Tidal surges, wind advisories, fog patterns, and historical climate risks.
4. **Public Events & Street Closures:** Parades, marathons, summer festivals, and access blackouts in the shoot window.
5. **Regional Safety & Armorer Regulations:** Mandated police details, fire safety officers (FSO), and blank ammunition oversight.

---

## Interactive Demo Jurisdictions Built-In

The command center includes three pre-configured test scenarios based on genuine original scenes:

* **Santa Monica Pier (Neon Driftwood):** Coastal foot chase, drone operations, blank gunfire, and tidal hazard. Flags municipal street closures, night curfews, and weapons armorer rules.
* **Chicago Loop (The Lakefront Cipher):** River promenade pursuit, drone sweep, freezing fog, and drawbridge operations. Flags winter weather advisories and maritime coordination rules.
* **New York Manhattan (Empire Lockdown):** Brooklyn Bridge pedestrian walkway, simulated blank discharge, and UN security zone boundaries. Flags mayoral permit lead times and security perimeters.

*Users can also freely enter any custom city, date window, crew scale, and screenplay.*

---

## Local Installation & Quick Start

### 1. Prerequisites
* Python 3.11+ (Python 3.13 tested)
* Node.js 18+ and npm
* API Keys: `GEMINI_API_KEY`, `PARALLEL_API_KEY`

### 2. Clone & Setup Environment
```bash
git clone https://github.com/eka1357/CutLine.git
cd CutLine

# Setup Python virtual environment
python -m venv .venv

# On Windows:
.\.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY="your-gemini-api-key"
PARALLEL_API_KEY="your-parallel-api-key"
GEMINI_MODEL="gemini-3.6-flash"
```

### 4. Run Unified Production Server
Build the frontend and run FastAPI (which serves both the API and the Command Center at `/`):
```bash
# Build React frontend
cd frontend
npm install
npm run build
cd ..

# Start unified server
uvicorn backend.main:app --port 8000
```
* **Command Center:** `http://localhost:8000/`
* **Health Check & Telemetry:** `http://localhost:8000/health`
* **Swagger API Documentation:** `http://localhost:8000/docs`

---

## Automated Verification & Test Suites

The codebase includes comprehensive test suites covering unit logic, adversarial corner cases, and live pipeline integration:

```bash
# 1. Run the 10-Scenario Adversarial Test Suite
python tests/test_phase2_adversarial.py

# 2. Run the Full 5-Stage Live End-to-End Pipeline
python tests/run_phase2_test.py

# 3. Run FastAPI Endpoint & Static Hosting Verification
python tests/test_api_endpoint.py
```

---

## Cloud Deployment (Google Cloud Run / Render)

CutLine is packaged with a multi-stage `Dockerfile` serving both the compiled React frontend and the FastAPI backend in a high-performance single container.

### Deploying to Google Cloud Run
```bash
gcloud run deploy cutline \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY="your-gemini-key",PARALLEL_API_KEY="your-parallel-key",GEMINI_MODEL="gemini-3.6-flash"
```

---

## License & Compliance
* **License:** [MIT License](LICENSE) (Visible at repository root)
* **Code Copyright:** Copyright (c) 2026 CutLine Contributors.
* **Track:** Parallel Track — Agentic Cinema: The Blockbuster Hackathon (Google Cloud).
