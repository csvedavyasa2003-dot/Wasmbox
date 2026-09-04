const API_BASE_URL = "http://127.0.0.1:8000"

export async function compileCode(code) {
  const response = await fetch(`${API_BASE_URL}/api/compile/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ code }),
  })

  if (!response.ok) {
    throw new Error(`Compilation failed: ${response.status}`)
  }

  return response.json()
}

export async function runCode(moduleId) {
  const response = await fetch(`${API_BASE_URL}/api/execute/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      module_id: moduleId,
    }),
  })

  if (!response.ok) {
    throw new Error(`Execution failed: ${response.status}`)
  }

  return response.json()
}