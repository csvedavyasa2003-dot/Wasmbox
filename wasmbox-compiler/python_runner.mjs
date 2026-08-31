import { loadPyodide } from "./pyodide/pyodide.mjs"

let pyodide = null

async function getPyodide() {
  if (!pyodide) {
    pyodide = await loadPyodide()
  }

  return pyodide
}

export async function executePython(code) {
  const runtime = await getPyodide()

  let output = ""

  runtime.setStdout({
    batched: (msg) => {
      output += msg + "\n"
    }
  })

  try {
    runtime.runPython(code)

    return {
      success: true,
      output: output
    }
  } catch (error) {
    return {
      success: false,
      output: output,
      error: error.message
    }
  }
}