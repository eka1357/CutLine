# CUTLINE: Final Pre-Submission Audit

> **Auditor perspective:** Senior staff engineer, product designer, AI-agent architect, and extremely skeptical Parallel-track hackathon judge.
>
> **Repository:** [github.com/eka1357/CutLine](https://github.com/eka1357/CutLine) | Commit: `6d6d7fa`
>
> **Audit date:** 2026-09-07 | All 10 adversarial tests: **PASS (100%)**

---

## Audit Summary

CutLine is in strong shape. The 5-stage deterministic pipeline is well-architected, the Parallel integration is genuine and multi-call, the evidence provenance chain is unbroken, and the adversarial test suite is one of the strongest I've seen in a hackathon entry. The UI is purposeful and avoids most generic AI-dashboard traps.

That said, there are specific issues a sharp judge will notice. This audit focuses exclusively on changes that could **lose you points** or **fail during the live demo**.

---

## P0: Must Fix (Demo Fragility or Rule Violation)

### P0-1: Em dashes in UI copy violate AGENTS.md

**AGENTS.md explicitly says:** *"no em dashes in UI copy."*

Three visible UI em dashes exist right now:

| File | Line | Content |
|---|---|---|
| `Header.jsx` | 14 | `Autonomous Production-Planning Agent --- Reality-Testing Screenplays...` |
| `PipelineProgress.jsx` | 60 | `{s.agent} --- {s.desc}` |
| `index.html` | 8 | `<title>CUTLINE --- Autonomous Production Planning Agent</title>` |

**Fix:** Replace each em dash with ` / ` or restructure the sentence. The screenplay text in `presets.js` (line 52) is story text, not UI copy, and is fine. The CSS comment is also fine.

**Risk if unfixed:** A judge reading AGENTS.md and then scanning the UI will see this as a direct violation of your own stated design rules. It signals sloppiness.

---

### P0-2: Colored left-border card accents violate AGENTS.md

**AGENTS.md explicitly says:** *"never do: colored left-border card accents"*

`index.css` lines 476-495 define:

```css
.scene-summary-box {
  border-left: 3px solid var(--border-strong);
}
.scene-summary-box.GO {
  border-left-color: var(--status-go);
}
.scene-summary-box.RISK {
  border-left-color: var(--status-risk);
}
.scene-summary-box.BLOCKED {
  border-left-color: var(--status-blocked);
}
```

This is the exact pattern AGENTS.md calls out. The scene cards already have prominent `status-badge` elements (GO/RISK/BLOCKED pill) in the header, so the colored left border is redundant decoration.

**Fix:** Remove `border-left` from `.scene-summary-box` and its status variants. The status badge already communicates state clearly.

---

### P0-3: Vite dev proxy doesn't cover `/health`

`vite.config.js` only proxies `/api`:

```js
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  },
},
```

But `api.js` line 9 calls `/health` directly:

```js
const res = await fetch(`${API_BASE}/health`)
```

In dev mode (`npm run dev` on port 3000), this request goes to `localhost:3000/health` and 404s. The health badge permanently shows "CONNECTING...".

**Fix:** Add `/health` to the Vite proxy:
```js
proxy: {
  '/api': { target: 'http://localhost:8000', changeOrigin: true },
  '/health': { target: 'http://localhost:8000', changeOrigin: true },
},
```

**Risk if unfixed:** If the demo is run via Option B (dev mode) instead of Option A (production build), the system health indicator is permanently broken. A judge starting the app the "developer way" sees "CONNECTING..." forever.

---

### P0-4: No request timeout on the frontend API call

`api.js` uses `fetch()` with no `AbortController` timeout. The full pipeline takes 15-30+ seconds. If the backend hangs (Gemini 503 retry exhaustion, Parallel rate limit), the UI spinner runs indefinitely with no user feedback.

**Fix:** Add a 90-second `AbortController` timeout and surface a specific timeout error message like `"Pipeline timed out after 90 seconds. The Gemini or Parallel APIs may be temporarily unavailable."` This is critical for the live demo where API quotas are shared with other hackathon participants.

---

### P0-5: Pipeline progress indicator is fake (hardcoded timers, not server-driven)

`PipelineProgress.jsx` lines 14-31 advance stages via fixed `setTimeout` durations (2.5s, 12s, 16s, 20s). These timers have zero connection to actual backend execution. If Gemini is slow (10s for Stage 1), Stage 2 will visually "start" while Stage 1 is still running. If the pipeline finishes in 8 seconds, Stage 2 will still be "active" for 4 more seconds.

A technical judge watching the pipeline progress will notice the mismatch between the visual indicator and the actual API response timing.

**Fix (minimum viable):** When the API returns (loading transitions from true to false), immediately set all stages to "completed" so the indicator is at least consistent with the result. Don't leave timers ticking after the response arrives.

---

## P1: High Value (Judge Will Notice or Ask About)

### P1-1: The `evidence_text` often duplicates `claim` verbatim

In `parallel_researcher.py` line 78, when a clean excerpt is found, both `claim` and `evidence_text` are set to the same `cleaned` string. When a judge opens the Evidence Drawer, they see the "Claim" and the "Verbatim Excerpt from Parallel Search" showing identical text. This looks like the system is echoing itself rather than showing independent corroboration.

**Fix:** Store the full raw excerpt paragraph (pre-truncation) in `evidence_text` and the cleaned/truncated version in `claim`, so the drawer shows distinctly different content.

---

### P1-2: EvidenceDrawer `category` display uses `replace('_', ' ')` (first occurrence only)

`EvidenceDrawer.jsx` line 23 uses JavaScript's `String.replace('_', ' ')` which only replaces the first underscore. While the current 5 categories all work fine, `weather_climate` would display as `"weather climate"` which is fine, but the code has a latent bug.

**Fix:** Use `.replace(/_/g, ' ')` or `.replaceAll('_', ' ')`.

---

### P1-3: `RewritePanel` strategy formatter misses `procedural_mitigation`

`RewritePanel.jsx` `formatStrategyType` has cases for `timing_shift`, `technical_rewrite`, `location_swap`, but the schema defines a fourth type: `procedural_mitigation`. Gemini could emit this, and it would display as raw lowercase text.

**Fix:** Add `case 'procedural_mitigation': return 'Procedural Mitigation'` to the switch.

---

### P1-4: Rewrite sanitization in `rewrite_strategist.py` is brittle

Line 107 has:
```python
cleaned_impact = alt.estimated_impact.replace("40%", "measurable").replace("30ft jib crane", "camera crane")
```

This only catches exactly `"40%"` and `"30ft jib crane"`. Gemini could say "35%", "50%", "$15,000", or "20-foot dolly" and bypass it entirely.

**Fix:** Use a regex to strip numeric percentages (`\d+%`), dollar amounts (`\$[\d,]+`), and specific dimension claims (`\d+\s*ft`) from the impact field.

---

### P1-5: README is missing live Cloud Run URL and demo video link

AGENTS.md requires: *"README: what it does, tech used, how to run locally, live Cloud Run URL, demo video link."*

The current README has Cloud Run deploy *instructions* but no actual live URL. There's also no demo video link. Before submission, these must be populated.

---

### P1-6: No graceful handling if backend returns `null` arrays

The frontend does null-checks like `scene.findings && scene.findings.length > 0`, which would throw if `findings` is `null` rather than an empty array. Pydantic's `default_factory=list` makes this unlikely, but network truncation could produce `null` values.

**Fix:** Use optional chaining: `scene.findings?.length > 0`.

---

## P2: Optional Polish (Nice to Have)

### P2-1: Default Vite favicon

`index.html` references `/vite.svg`. A judge opening the browser tab sees the generic Vite logo.

### P2-2: No keyboard Escape to close EvidenceDrawer

The drawer closes on backdrop click and "CLOSE" button, but not on Escape key.

### P2-3: `httpx` dependency appears unused

`requirements.txt` includes `httpx>=0.28.0` but no backend file imports it. May be a transitive dependency of `google-genai` but doesn't need explicit pinning.

### P2-4: Docker image includes unnecessary docs

Consider excluding `suggestions.md`, `DEMO_SCRIPT.md`, and `AGENTS.md` from the Docker build.

### P2-5: `run_phase1_pipeline` and `/api/phase1/analyze` are dead code

These were for Phase 1 testing and are no longer needed for the demo. They add unnecessary API surface.

---

## What NOT to Change

| Item | Reason |
|---|---|
| The 5-stage pipeline architecture | Clean, deterministic, exactly what AGENTS.md specifies. Don't add a 6th stage. |
| Decision Engine being pure Python (no LLM) | The project's strongest technical differentiator. Never make Stage 4 an LLM call. |
| The 5 evidence categories | AGENTS.md is explicit. Don't add music rights, union rates, etc. |
| Pydantic schema enforcement on Gemini | Correctly implemented and a strong signal of rigor. |
| The adversarial test suite | 10 scenarios, 100% pass, covering all edge cases. Don't simplify. |
| The dark editorial visual identity | Distinctive and avoids the generic AI-dashboard trap. Keep it. |
| Courier Prime screenplay excerpts | Correct typographic choice for film industry credibility. |
| The two preset screenplays | They demonstrate generalization (Santa Monica vs Chicago). Keep both. |

---

## Provenance Chain Trace

Tracing the complete chain for Scene 2 (EXT. SANTA MONICA PIER - NIGHT) through the codebase:

```
Scene 2 requirements (from gemini_analyzer.py Stage 1 Gemini extraction)
  e.g. "drone filming", "simulated blank gunfire", "night exterior lighting"
        |
parallel_researcher.py runs 5 client.search() calls (Stage 2)
  -> filming_permits query -> returns facts with source_url + evidence_text
  -> location_restrictions query -> returns facts
  -> weather_climate query -> returns facts
  -> public_events query -> returns facts
  -> regional_regulations query -> returns facts
        |
evidence_engine.py matches_profile() (Stage 3)
  -> requirement "simulated blank gunfire" matches profile "pyrotechnics_and_weapons"
  -> evidence_text containing "fire safety officer" or "armorer" matches evidence_keywords
  -> Creates EvidenceItem(scene_id, requirement_name, claim, source_url, source_domain)
        |
decision_engine.py evaluate_special_effects_weapons() (Stage 4)
  -> Finds evidence with "fire safety officer" or "armorer" in evidence_text
  -> Creates DecisionFinding(consequence=RISK, rule_name="Mandatory Safety Personnel...")
  -> supporting_evidence contains the EvidenceItem with source_url
        |
rewrite_strategist.py (Stage 5 - Gemini)
  -> Only runs because decision != GO
  -> Receives findings_brief with rule names and evidence citations
  -> Returns ProductionAlternative with rewritten_scene_excerpt
        |
Frontend FindingCard.jsx renders:
  REQUIREMENT -> RULE -> CONSEQUENCE
  SOURCE: {ev.source_domain} (clickable -> opens EvidenceDrawer)
```

**Verdict on provenance:** The chain is complete and unbroken from Parallel search results to the final UI. Every finding traces back to a stored `source_url` and `evidence_text`. No claim exists without a source.

---

## Parallel Integration Authenticity Assessment

| Signal | Status | Details |
|---|---|---|
| SDK import | VERIFIED | `from parallel import Parallel` in `parallel_researcher.py` line 10 |
| Client instantiation | VERIFIED | `Parallel(api_key=PARALLEL_API_KEY)` at line 200 |
| Runtime `client.search()` call | VERIFIED | Line 131 with `search_queries`, `objective`, `mode="turbo"` |
| Multiple distinct calls | VERIFIED | 5 sequential calls, one per category, each with different query and objective |
| Results consumed (not discarded) | VERIFIED | Excerpts extracted, cleaned, stored as `ResearchFact` objects flowing through Stages 3-5 |
| Dependency pinned | VERIFIED | `parallel-web>=0.1.0` in requirements.txt |
| No synthetic fallback | VERIFIED | On failure: `return [], err_msg` (no fake facts manufactured) |

**Verdict on Parallel:** The integration is genuine, deep, and central to the pipeline. This is not a cosmetic reference. A judge can verify by reading a single file.

---

## Top 5 Changes (Ranked by Impact on Winning)

1. **P0-1 + P0-2:** Fix the AGENTS.md design violations (em dashes + left-border accents). Self-inflicted wounds that undermine your own spec.
2. **P0-5:** Fix the fake pipeline progress indicator. Either connect it to real backend events or snap to "completed" when the API returns.
3. **P0-4:** Add an API timeout with a clear error message. A hanging spinner during a live demo is the #1 way to lose a judge's attention.
4. **P1-4:** Harden the rewrite sanitization to catch percentages/dollar amounts via regex, not exact string matching.
5. **P1-5:** Populate the Cloud Run URL and demo video link in README before submission.

---

## Final Verdict

> **Judge's One-Sentence Verdict:** CutLine is a technically rigorous, well-scoped entry with a genuine Parallel integration, a defensible deterministic pipeline, and strong adversarial test coverage that would place in the top tier of the Parallel track, provided the small but visible AGENTS.md design violations and the fake progress indicator are fixed before submission.

**Grade: A-** (A after the P0 fixes)
