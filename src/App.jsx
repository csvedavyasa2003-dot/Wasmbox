import { useState } from "react"
import Editor from "@monaco-editor/react"

import { compileCode, runCode } from "./services/api"

function App() {
  const [code, setCode] = useState(
    "# Write your Python code here\nprint('Hello, WasmBox!')"
  )

  const [output, setOutput] = useState("Output will appear here.")

  const [isCompiling, setIsCompiling] = useState(false)
  const [isRunning, setIsRunning] = useState(false)

  const handleCompile = async () => {
  setIsCompiling(true)
  setOutput("Compiling...")

  try {
    const result = await compileCode(code)

    if (result.success) {
      setOutput(`Compilation successful:\n\n${result.output || "No output"}`)
    } else {
      setOutput(`Compilation failed:\n\n${result.error || "Unknown error"}`)
    }
  } catch (error) {
    setOutput(`Compilation failed:\n\n${error.message}`)
  } finally {
    setIsCompiling(false)
  }
}

  const handleRun = async () => {
    setIsRunning(true)
    setOutput("Running...")

    try {
      const result = await runCode("test.wasm", 10, 20)

      if (result.stderr) {
        setOutput(
          `stdout:\n${result.stdout || ""}\n\nstderr:\n${result.stderr}`
        )
      } else {
        setOutput(`stdout:\n${result.stdout || ""}`)
      }
    } catch (error) {
      setOutput(`Execution failed:\n${error.message}`)
    } finally {
      setIsRunning(false)
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>WasmBox</h1>

        <div className="actions">
          <button
            onClick={handleCompile}
            disabled={isCompiling || isRunning}
          >
            {isCompiling ? "Compiling..." : "Compile"}
          </button>

          <button
            onClick={handleRun}
            disabled={isCompiling || isRunning}
          >
            {isRunning ? "Running..." : "Run"}
          </button>
        </div>
      </header>

      <main className="main-content">
        <div className="workspace">
          <div className="editor-container">
            <Editor
              height="100%"
              language="python"
              theme="vs-dark"
              value={code}
              onChange={(value) => setCode(value || "")}
            />
          </div>

          <div className="output-panel">
            <div className="output-header">
              Output
            </div>

            <div className="output-content">
              <pre>{output}</pre>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App