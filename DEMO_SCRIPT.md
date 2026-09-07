# CUTLINE — 3-Minute Video Demo Script
> **Track:** Parallel | **Hackathon:** Agentic Cinema: The Blockbuster Hackathon (Google Cloud)

---

## Demo Overview
- **Duration:** 3 minutes (180 seconds)
- **Goal:** Prove runtime integration of **Parallel Search** and **Google Cloud Gemini**, demonstrate the deterministic **5-stage pipeline**, showcase unbroken **evidence provenance**, and highlight actionable **director rewrites** in the Production Command Center.
- **Screenplay:** *"Neon Driftwood"* (original fictional script, zero copyright issues) with brief generalization showcase via *"The Lakefront Cipher"* (Chicago, IL).

---

## Timed Walkthrough

### [0:00 – 0:35] The Problem & The One-Line Pitch
**Visual:** Open on the CutLine Production Command Center at `http://localhost:8000/`. The header displays `CUTLINE`, `PARALLEL TRACK`, `GOOGLE CLOUD GEMINI 3.6 FLASH`, and `PARALLEL SEARCH SDK RUNTIME`.

**Voiceover / Script:**
> *"Every year, independent filmmakers commit schedules and budgets before discovering real-world location constraints: municipal curfews, permit lead times, deck load limits, and conflicting street closures. Finding these out on shoot day costs thousands of dollars and ruins productions.*
> 
> *This is **CutLine**—an autonomous production-planning agent built for the Blockbuster Hackathon. CutLine reality-tests a screenplay against live municipal regulations, weather advisories, and local filming rules using live **Parallel Search** and **Google Cloud Gemini**, turning real-world constraints into actionable, director-ready solutions."*

---

### [0:35 – 1:15] Real-Time 5-Stage Agent Execution
**Visual:** 
1. Point to the preset switcher. Show *"Neon Driftwood"* in Santa Monica, CA ($75,000 budget; July 10–15).
2. Point out the script: Scene 1 is an interior diner dialogue; Scene 2 is a high-intensity chase onto the Santa Monica Pier with simulated blank gunfire, drone tracking, and late-night ocean spray at 1:30 AM.
3. Click **"EXECUTE PRODUCTION PLANNING AGENT"**.
4. The **Autonomous Agent Pipeline Active** panel lights up, showing live stage progression:
   - *Stage 1: Screenplay Breakdown* (Gemini 3.6 Flash)
   - *Stage 2: Parallel Web Research* (Official `parallel-web` SDK across 5 categories)
   - *Stage 3: Evidence Engine* (Grounding requirements to verified web evidence)
   - *Stage 4: Production Decision Engine* (Evaluating deterministic rules)
   - *Stage 5: Rewrite Strategist* (Gemini generating alternatives)

**Voiceover / Script:**
> *"Let's test our original neo-noir screenplay, 'Neon Driftwood', set in Santa Monica. Scene 1 is a quiet interior diner scene. Scene 2 is a high-stakes chase onto the Santa Monica Pier at 1:30 AM featuring live blank gunfire and drone cameras.*
> 
> *When we execute CutLine, the agent pipeline begins immediately:*
> - *Stage 1 uses Gemini 3.6 Flash to break down screenplay requirements.*
> - *Stage 2 calls the official Parallel Search API at runtime across exactly five categories: filming permits, location restrictions, weather patterns, public events, and regional safety.*
> - *Stages 3 and 4 ground the retrieved evidence and evaluate deterministic production rules.*
> - *And Stage 5 drafts concrete production rewrites."*

---

### [1:15 – 1:55] The Production Plan & Unbroken Provenance
**Visual:** 
1. The completed plan appears. Show the **Overview Ribbon**: `NEON DRIFTWOOD | Santa Monica, CA | OVERALL: BLOCKED (GO: 1, BLOCKED: 1)`.
2. Scroll to **Scene 1 (INT. PACIFIC CREST DINER)**: Green `GO` badge. No curfews, standard interior location agreement applies. Stage 5 was skipped because clean scenes don't need rewrites.
3. Scroll to **Scene 2 (EXT. SANTA MONICA PIER)**: Red `BLOCKED` badge.
4. Show the findings:
   - `Mandatory Safety Personnel & Armorer Oversight for Weapons` [RISK]
   - `Municipal Nighttime Noise Ordinance & Curfew Compliance` [RISK]
   - `Historic Structure Load & Ballast Weighting Regulation` [RISK]
   - `Marine High Surf & Tidal Surge Advisory` [RISK]
   - `Municipal Event Total Street Closure & Access Blackout` [BLOCKED]
5. Click a source button (e.g., `SOURCE: filmsantamonica.com` or `SOURCE: film.ca.gov`).
6. The **Verified Web Evidence Drawer** slides open on the right:
   - Highlight the authentic claim, the direct clickable URL, and the verbatim excerpt returned by Parallel Search.
7. Click `CLOSE ✕`.

**Voiceover / Script:**
> *"Look at the results. Scene 1 is evaluated naturally as GO. But Scene 2 is flagged with real-world production barriers.*
> 
> *Notice: there are zero hallucinated rules and zero arbitrary 0–100 feasibility percentages. Every single decision is deterministic code following the strict chain: Requirement to Evidence to Rule to Consequence.*
> 
> *And every finding is backed by authentic web citations. When I click on this source, CutLine's Evidence Drawer displays the exact claim, the verbatim Parallel Search excerpt, and the live source URL from the California Film Commission and Film Santa Monica."*

---

### [1:55 – 2:35] Stage 5: Actionable Screenplay Rewrites
**Visual:**
1. Scroll down to Scene 2's **Stage 5: Actionable Production Alternatives**.
2. Click through the 3 tabs:
   - Tab 1: **Sunset Pier Foot Pursuit** (*Timing Shift*): Shifts shoot to golden hour; replaces live blanks with replica prop and physical tackle; eliminates night curfew and heavy lighting ballasts.
   - Tab 2: **Silent Pier Standoff with VFX Gunfire** (*Technical Rewrite*): Retains night setting; replaces blanks with prop replica for post VFX; uses ground-based jib arm on rubber mats to comply with pier deck load limits.
   - Tab 3: **Private Marina Dock Night Standoff** (*Location Swap*): Moves pursuit to a private gated dock under property agreement, bypassing public pier event blackouts.
3. Point out the screenplay excerpt box formatted in Courier Prime, showing rewritten sluglines, action, and dialogue ready for the director.

**Voiceover / Script:**
> *"A simple list of production risks isn't enough. Filmmakers need solutions. That's where Stage 5—the Rewrite Strategist—comes in.*
> 
> *For flagged scenes, Gemini produces three distinct, director-respecting alternatives:*
> - *A Timing Shift to sunset golden hour, bypassing the 10 PM quiet hours.*
> - *A Technical Rewrite using replica props and post VFX to eliminate weapons safety mandates and pier deck weight limits.*
> - *Or a Location Swap to a controlled private facility with owner agreement.*
> 
> *Each strategy includes the exact mechanism change, the trade-off, and a complete screenplay excerpt formatted in Courier Prime that preserves dramatic tension while eliminating the real-world blocker."*

---

### [2:35 – 3:00] Generalization & Cloud Run Architecture
**Visual:**
1. Click the preset button **"Chicago (Lakefront Cipher)"**.
2. Show that the location instantly switches to `Chicago, IL`, and the screenplay switches to the Harold Washington Library and Chicago Riverwalk.
3. Highlight that the backend rules are genuinely generalized across cities.
4. Show the clean terminal or Cloud Run command.

**Voiceover / Script:**
> *"CutLine isn't hardcoded to one location. If we switch to 'The Lakefront Cipher' set in Chicago, CutLine dynamically evaluates Chicago Riverwalk curfews and marathon route street closures.*
> 
> *CutLine uses Google Cloud Gemini and the official Parallel Search SDK, packages cleanly as a single-container Cloud Run deployment, and is fully open-source under the MIT License.*
> 
> *CutLine: Turning screenplays into production plans that can survive reality. Thank you."*
