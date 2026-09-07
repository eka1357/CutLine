/**
 * API client connecting CutLine Frontend to FastAPI Backend
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

export async function runProductionPipeline({ screenplay, location, shoot_start_date, shoot_end_date, budget }) {
  const payload = {
    screenplay,
    location,
    shoot_start_date,
    shoot_end_date,
    budget: Number(budget) || 50000,
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
