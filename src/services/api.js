const API_BASE_URL = "http://127.0.0.1:8000"

async function apiRequest(url, options, fallbackMessage) {
  let response

  try {
    response = await fetch(url, options)
  } catch {
    throw new Error(
      "Cannot connect to the WasmBox backend. Make sure it is running on port 8000."
    )
  }

  let data

  try {
    data = await response.json()
  } catch {
    throw new Error(`Invalid server response (HTTP ${response.status}).`)
  }

  if (!response.ok) {
    const message =
      data.detail || data.error || data.message || fallbackMessage

    throw new Error(
      typeof message === "string" ? message : JSON.stringify(message)
    )
  }

  return data
}

function createCodeRequest(code) {
  if (!code || !code.trim()) {
    throw new Error("Please enter Python code first.")
  }

  return {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ code }),
  }
}

export async function compileCode(code) {
  const options = createCodeRequest(code)

  return apiRequest(
    `${API_BASE_URL}/api/compile`,
    options,
    "Python validation failed."
  )
}

export async function runCode(code) {
  const options = createCodeRequest(code)

  const result = await apiRequest(
    `${API_BASE_URL}/api/run-python`,
    options,
    "Python execution failed."
  )

  return {
    ...result,
    stdout: result.output || "",
  }
}

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