
const COMPILER_URL = "http://localhost:8001/api";

async function apiRequest(url, options, fallbackMessage) {
  let response;

  try {
    response = await fetch(url, options);
  } catch {
    throw new Error(
      "Cannot connect to the compiler service. Make sure it is running on port 8001."
    );
  }

  let data;

  try {
    data = await response.json();
  } catch {
    throw new Error(`Invalid server response (HTTP ${response.status}).`);
  }

  if (!response.ok) {
    const message =
      data.detail || data.error || data.message || fallbackMessage;

    throw new Error(
      typeof message === "string" ? message : JSON.stringify(message)
    );
  }

  return data;
}

function createCodeRequest(code) {
  if (!code || !code.trim()) {
    throw new Error("Please enter Python code first.");
  }

  return {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ code }),
  };
}

export async function compileCode(code) {
  const options = createCodeRequest(code);

  return apiRequest(
    `${COMPILER_URL}/compile`,
    options,
    "Python validation failed."
  );
}

export async function runCode(code) {
  const options = createCodeRequest(code);

  return apiRequest(
    `${COMPILER_URL}/run`,
    options,
    "Python execution failed."
  );
}