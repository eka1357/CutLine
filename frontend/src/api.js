/**
 * API client connecting CutLine Frontend to FastAPI Backend
 */

const API_BASE = ""

export async function fetchHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`)
    if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`)
    return await res.json()
  } catch (err) {
    console.error("API Health error:", err)
    return { status: "offline", error: err.message }
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

  const response = await fetch(`${API_BASE}/api/pipeline/run`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    const errData = await response.json().catch(() => ({}))
    throw new Error(errData.detail || `Pipeline failed with status ${response.status}: ${response.statusText}`)
  }

  return await response.json()
}
