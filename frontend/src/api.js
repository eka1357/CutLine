/**
 * API client connecting CutLine Frontend to FastAPI Backend
 * Supports both synchronous and SSE-streaming pipeline execution.
 */

const API_BASE = ""

export async function fetchHealth() {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), 5000)

  try {
    const res = await fetch(`${API_BASE}/health`, { signal: controller.signal })
    if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`)
    return await res.json()
  } catch (err) {
    console.error("API Health error:", err)
    return { status: "offline", error: err.name === 'AbortError' ? 'Health check timed out' : err.message }
  } finally {
    clearTimeout(timeoutId)
  }
}

export async function runProductionPipeline({ screenplay, location, shoot_start_date, shoot_end_date, budget, production_type, crew_size }) {
  const payload = {
    screenplay,
    location,
    shoot_start_date,
    shoot_end_date,
    budget: Number(budget) || 50000,
    production_type: production_type || "Independent Feature",
    crew_size: crew_size || "Medium (11-30 crew)",
  }

  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), 90000)

  try {
    const response = await fetch(`${API_BASE}/api/pipeline/run`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
      signal: controller.signal,
    })

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}))
      throw new Error(errData.detail || `Pipeline failed with status ${response.status}: ${response.statusText}`)
    }

    return await response.json()
  } catch (err) {
    if (err.name === 'AbortError') {
      throw new Error("Pipeline execution timed out after 90 seconds. The Gemini or Parallel APIs may be experiencing high latency. Please retry.")
    }
    throw err
  } finally {
    clearTimeout(timeoutId)
  }
}


/**
 * Streams the production pipeline via SSE, calling onStep for each progress event.
 * Returns the final ProductionPlan result.
 * Falls back to non-streaming endpoint on connection failure.
 *
 * @param {Object} formData - Pipeline request payload
 * @param {function} onStep - Callback receiving { stage: number, message: string }
 * @returns {Promise<Object>} The complete ProductionPlan
 */
export async function streamProductionPipeline(formData, onStep) {
  const payload = {
    screenplay: formData.screenplay,
    location: formData.location,
    shoot_start_date: formData.shoot_start_date,
    shoot_end_date: formData.shoot_end_date,
    budget: Number(formData.budget) || 50000,
    production_type: formData.production_type || "Independent Feature",
    crew_size: formData.crew_size || "Medium (11-30 crew)",
  }

  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), 120000)

  try {
    const response = await fetch(`${API_BASE}/api/pipeline/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal: controller.signal,
    })

    if (!response.ok) {
      // Fall back to non-streaming endpoint
      console.warn("SSE stream endpoint failed, falling back to synchronous endpoint")
      clearTimeout(timeoutId)
      return await runProductionPipeline(formData)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ""
    let result = null
    let currentEventType = null
    let currentDataLines = []

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })

      // Parse SSE events from the buffer
      const lines = buffer.split("\n")
      buffer = lines.pop() || "" // Keep incomplete line in buffer

      for (const line of lines) {
        if (line.startsWith("event: ")) {
          currentEventType = line.slice(7).trim()
        } else if (line.startsWith("data: ")) {
          currentDataLines.push(line.slice(6))
        } else if (line.startsWith(":")) {
          // SSE comment (keepalive), ignore
        } else if (line.trim() === "") {
          // Empty line signals end of an event
          if (currentEventType && currentDataLines.length > 0) {
            const dataStr = currentDataLines.join("\n")
            try {
              const parsed = JSON.parse(dataStr)
              if (currentEventType === "step" && onStep) {
                onStep(parsed)
              } else if (currentEventType === "complete") {
                result = parsed
              } else if (currentEventType === "error") {
                throw new Error(parsed.message || "Pipeline execution failed")
              }
            } catch (parseErr) {
              if (currentEventType === "error") throw parseErr
              console.warn("SSE parse error:", parseErr)
            }
          }
          currentEventType = null
          currentDataLines = []
        }
      }

      if (result) break
    }

    if (!result) {
      throw new Error("SSE stream ended without a complete result")
    }

    return result
  } catch (err) {
    if (err.name === 'AbortError') {
      throw new Error("Pipeline execution timed out after 120 seconds. The Gemini or Parallel APIs may be experiencing high latency. Please retry.")
    }
    throw err
  } finally {
    clearTimeout(timeoutId)
  }
}
