# AGENTS.md — CUTLINE

## What this is
**Cutline** is an autonomous production-planning agent for the **Agentic Cinema:
The Blockbuster Hackathon** (Google Cloud, **Parallel track**).

**One-line pitch:** Cutline turns a screenplay into a production plan that can
survive reality — it investigates real-world constraints around a proposed
shoot location and date, and turns what it finds into concrete, actionable
changes, not just a report.

**The problem:** filmmakers commit money and schedules before discovering
production constraints (location restrictions, seasonal weather, conflicting
public events, filming regulations). Discovering these late costs real money
and real time. Cutline surfaces them early and proposes the cheapest fix.

**Audience:** independent producers and small production companies who can't
afford a full location-scouting and legal-clearance team.

## Hackathon constraints (do not violate)
- Track: **Parallel**. Must actively call **Parallel's Search API at
  runtime** — via the official `parallel-web` SDK (Python or TypeScript), or
  a supported integration (Vercel AI SDK's `@parallel-web/ai-sdk-tools`,
  LangChain's `ParallelWebSearchTool`), or a Grounding config using Parallel
  as the search provider. Referencing Parallel in the README is not enough —
  it must be imported and called in code.
- AI/agent tooling restricted to **Google Cloud only**: Gemini via
  `google-genai` or `google-cloud-aiplatform`, Google Cloud Agent Builder /
  ADK. No OpenAI, Anthropic, AWS, or Azure AI SDKs anywhere in the shipped
  runtime code.
- Must run on web (browser-accessible), publicly reachable, and function
  exactly as shown in the demo video.
- Public repo (GitHub/GitLab/Bitbucket) with an OSI-approved license file
  (MIT) visible at the top of the repo's About section.
- README must make Gemini/Google Cloud and Parallel usage obvious and
  verifiable in code, not just claimed.
- Test/demo script must be an original scene or a genuinely public-domain
  text — never a real copyrighted screenplay, since the demo video is public.

## Tech stack
- **Frontend:** React (Vite), plain CSS — no heavy component library that
  imposes its own visual identity (see Design system below).
- **Backend:** Python (FastAPI).
- **Models:** Gemini via `google-genai`, structured JSON via forced function
  calling for every agent step — no free-text parsing between stages.
- **Search:** `parallel-web` SDK, called at runtime, multiple times per run
  (one call family per evidence category, not one generic call).
- **Storage:** in-memory / local files for the demo. No database needed.
- **Deployment:** Google Cloud Run (single container serving both API and
  built frontend, or two Cloud Run services if simpler to reason about).

## Agent pipeline (deterministic, five stages)

1. **Screenplay Analyzer** (Gemini) — script → structured JSON: scenes,
   each with location type (interior/exterior), time of day, and any
   real-world-relevant requirements (crowd scenes, vehicles, specific
   settings).
2. **Parallel Research Agent** — for the user's proposed shoot location and
   date range, runs targeted Parallel searches across exactly these
   categories (no more):
   - Filming/permit requirements for the stated city/region
   - General location-type filming restrictions
   - Seasonal/weather patterns for the shoot window
   - Public events and holidays in the shoot window and area
   - General regional filming regulations
   Each search result is kept as a structured fact: `{claim, source_url,
   category}`. Do not add categories beyond this list (music rights, child
   performer law, union rates, permit *acquisition* status, and anything
   requiring private/current availability are explicitly out of scope — the
   open web cannot answer those reliably, and claiming otherwise is the
   fastest way to lose credibility with a judge).
3. **Evidence Engine** — attaches every fact to the specific scene(s) it
   affects. No fact is used in a decision without a stored source URL.
4. **Production Decision Engine** — plain deterministic code (not an LLM
   call) that evaluates each scene's facts against simple rules and outputs
   one of: GO, RISK, BLOCKED. Every output includes the rule that fired, in
   the form: `Requirement -> Evidence -> Rule -> Consequence`. Never output
   a numeric confidence score or percentage — it isn't backed by anything
   real and a technical judge will ask what it means.
5. **Rewrite Strategist** (Gemini, single call, only runs for RISK/BLOCKED
   scenes) — given the flagged conflict, proposes 2-3 concrete alternatives
   (move date, move to an alternative location type, rewrite the scene
   interior/exterior) with a one-line estimated impact for each. This is a
   single cheap call per flagged scene, not a full production re-simulation.

## Environment variables / secrets
- `GEMINI_API_KEY` (or Vertex AI service account credentials)
- `PARALLEL_API_KEY`
Both set via Cloud Run environment config / Secret Manager — never
hardcoded or committed.

## Design system — read before writing any CSS or component

Same rules as always for this project: avoid anything that reads as
generic AI-generated output. Where a rule is phrased as an absence ("no
X"), that absence is the actual flaw — include it instead.

**Never do:** harsh/loud gradients, decorative Lucide icons as the app's
visual identity, plain pure-white background, rainbow color schemes, heavy
default drop shadows, three-feature-cards-in-a-row layouts, emoji used as
UI decoration (the GO/RISK/BLOCKED status colors are functional, not
decorative -- keep those, skip decorative emoji elsewhere), glassmorphism/
"liquid glass" panels, em dashes in UI copy, Inter/Geist/Space Grotesk as
the typeface, colored left-border card accents, fake testimonials,
bento-grid layouts, fake terminal/code-window motifs, the "it's not X,
it's Y" copy pattern, overused checkmark-bullet lists, pricing tiers,
radial gradient orbs, dot-grid backgrounds, sparkle icons, animated arrows
at CTAs, neon accents, basic pastel gradients, uniform soft corner-radius
everywhere.

**Always do:** ship real working screens in the demo, real loading states
for each pipeline stage (screenplay parsing and live search both take real
time -- show what's happening, e.g. "Searching filming regulations for Los
Angeles..."), a distinct visual identity built around the theme -- think a
**production command center**: a scene-by-scene risk timeline, a clickable
evidence/source drawer per finding, a clear GO/RISK/BLOCKED state per
scene -- rather than generic SaaS dashboard chrome. Pick 2-3 deliberate
colors with a reason (e.g. a neutral paper/ink base with the GO/RISK/
BLOCKED colors doing all the accent work) rather than a trendy palette.

## What NOT to build (explicit scope traps -- do not add these)
- Music-rights clearance
- Child-performer legal analysis
- Union-rate calculations
- Actual permit acquisition/filing
- Full budget simulation or counterfactual re-runs at different budgets
- More than 5 agents/stages
- Any numeric "feasibility score" out of 100
- More than the 5 evidence categories listed in stage 2

## Repo hygiene
- MIT license file at repo root, visible in GitHub's About section
- README: what it does, tech used, how to run locally, live Cloud Run URL,
  demo video link, and an explicit note on which lines of code call Gemini
  and which call Parallel
- No secrets committed
