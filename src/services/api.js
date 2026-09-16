const API_BASE_URL = "http://localhost:8000/api";

export async function compileCode(code) {
  const response = await fetch(`${API_BASE_URL}/compile`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ code }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Compilation failed");
  }

  return data;
}

export async function runCode(moduleId, a = 10, b = 20) {
  const response = await fetch(`${API_BASE_URL}/run`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      module_id: moduleId,
      a,
      b,
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Execution failed");
  }

  return data;
}