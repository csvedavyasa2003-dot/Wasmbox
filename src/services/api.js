const API_BASE_URL = "http://localhost:8000"

export async function compileComponent(code, moduleId) {
  const response = await fetch(`${API_BASE_URL}/api/compile-component`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      code,
      module_id: moduleId,
    }),
  })

  const result = await response.json()

  if (!response.ok || result.success === false) {
    throw new Error(result.error || `Compilation failed: ${response.status}`)
  }

  return result
}

export async function runComponent(moduleId, name) {
  const response = await fetch(`${API_BASE_URL}/api/run-component`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      module_id: moduleId,
      name,
    }),
  })

  const result = await response.json()

  if (!response.ok) {
    throw new Error(result.detail || `Execution failed: ${response.status}`)
  }

  return result
}

export async function listPlugins() {
  const response = await fetch(`${API_BASE_URL}/api/plugins/`)

  if (!response.ok) {
    throw new Error(`Failed to load plugins: ${response.status}`)
  }

  return response.json()
}
export async function runPython(code) {
  const response = await fetch(`${API_BASE_URL}/api/run-python`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ code }),
  })

  const result = await response.json()

  if (!response.ok || result.success === false) {
    throw new Error(result.error || `Python execution failed: ${response.status}`)
  }

  return result
}