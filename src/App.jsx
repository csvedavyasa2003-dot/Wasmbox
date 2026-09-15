import { useState } from "react"
import Editor from "@monaco-editor/react"

import {
  compileComponent,
  runComponent,
} from "./services/api"

function App() {
  const [code, setCode] = useState(
    "# Write your Python code here\n\ndef greet(name):\n    return f'Hello, {name}!'\n"
  )

  const [moduleId, setModuleId] = useState("hello")
  const [name, setName] = useState("Vedavyasa")
  const [output, setOutput] = useState("Output will appear here.")

  const [isCompiling, setIsCompiling] = useState(false)
  const [isRunning, setIsRunning] = useState(false)

  const handleCompile = async () => {
    setIsCompiling(true)
    setOutput("Compiling component...")

    try {
      const result = await compileComponent(code, moduleId)

      if (result.success) {
        setOutput(
          `Compilation successful:\n\nModule: ${result.module_id}\nSize: ${result.size_bytes} bytes`
        )
      } else {
        setOutput(
          `Compilation failed:\n\n${result.error || "Unknown error"}`
        )
      }
    } catch (error) {
      setOutput(`Compilation failed:\n\n${error.message}`)
    } finally {
      setIsCompiling(false)
    }
  }

  const handleRun = async () => {
    setIsRunning(true)
    setOutput("Running component...")

    try {
      const compiledModuleId = moduleId.endsWith(".wasm")
        ? moduleId
        : `${moduleId}.wasm`

      const result = await runComponent(compiledModuleId, name)

      setOutput(
        `Result:\n${result.result}\n\nStatus: ${result.status}\nExecution time: ${result.execution_time_ms} ms`
      )
    } catch (error) {
      setOutput(`Execution failed:\n\n${error.message}`)
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