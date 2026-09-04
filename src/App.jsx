import { useState } from "react"
import Editor from "@monaco-editor/react"
import { Clock, MemoryStick, ShieldCheck } from "lucide-react"
import { compileCode, runCode } from "./services/api"

function App() {
  const [code, setCode] = useState(
    "# Write your Python code here\nprint('Hello, WasmBox!')"
  )

  const [output, setOutput] = useState("Output will appear here.")
  const [isCompiling, setIsCompiling] = useState(false)
  const [isRunning, setIsRunning] = useState(false)
  const [moduleId, setModuleId] = useState(null)

  // Phase 3 - Day 1: Execution Metrics
  const [metrics, setMetrics] = useState({
    executionTimeMs: 0,
    memoryUsedMb: 0,
    memoryLimitMb: 128,
    status: "Ready",
  })

  const handleCompile = async () => {
    setIsCompiling(true)
    setOutput("Compiling...")

    try {
      const result = await compileCode(code)

      if (result.success) {
        // Temporary WASM module provided by the backend
        setModuleId("test.wasm")

        setOutput(
          `Compilation successful.\n\nCompiler output:\n${
            result.stdout || ""
          }`
        )
      } else {
        setOutput(
          `Compilation failed.\n\n${
            result.error || result.stderr || "Unknown error"
          }`
        )
      }
    } catch (error) {
      setOutput(`Compilation failed:\n${error.message}`)
    } finally {
      setIsCompiling(false)
    }
  }

  const handleRun = async () => {
    if (!moduleId) {
      setOutput("Please compile the code first.")
      return
    }

    setIsRunning(true)
    setOutput("Running...")

    // Reset metrics before execution
    setMetrics({
      executionTimeMs: 0,
      memoryUsedMb: 0,
      memoryLimitMb: 128,
      status: "Running",
    })

    try {
      const result = await runCode(moduleId, 10, 20)

      if (result.stderr) {
        setOutput(
          `stdout:\n${result.stdout || ""}\n\nstderr:\n${result.stderr}`
        )
      } else {
        setOutput(`stdout:\n${result.stdout || ""}`)
      }

      // Phase 3 - Day 1
      // Backend metrics will be connected in Day 3.
      // For now, show a basic completed state.
      setMetrics((previous) => ({
        ...previous,
        status: "Completed",
      }))
    } catch (error) {
      setOutput(`Execution failed:\n${error.message}`)

      setMetrics((previous) => ({
        ...previous,
        status: "Failed",
      }))
    } finally {
      setIsRunning(false)
    }
  }

  // Reset metrics whenever Monaco code is edited
  const handleCodeChange = (value) => {
    setCode(value || "")

    setMetrics({
      executionTimeMs: 0,
      memoryUsedMb: 0,
      memoryLimitMb: 128,
      status: "Ready",
    })
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
            disabled={isCompiling || isRunning || !moduleId}
          >
            {isRunning ? "Running..." : "Run"}
          </button>
        </div>
      </header>

      <main className="main-content">
        <div className="workspace">

          {/* Monaco Editor */}
          <div className="editor-container">
            <Editor
              height="100%"
              language="python"
              theme="vs-dark"
              value={code}
              onChange={handleCodeChange}
            />
          </div>

          {/* Output / Terminal Section */}
          <div className="output-panel">

            {/* Phase 3 - Day 1: Metrics Banner */}
            <div className="metrics-banner">

              <div className="metric-item">
                <Clock size={18} />
                <div>
                  <span className="metric-label">
                    Execution Time
                  </span>
                  <span className="metric-value">
                    {metrics.executionTimeMs} ms
                  </span>
                </div>
              </div>

              <div className="metric-item">
                <MemoryStick size={18} />
                <div>
                  <span className="metric-label">
                    Memory
                  </span>
                  <span className="metric-value">
                    {metrics.memoryUsedMb} MB /{" "}
                    {metrics.memoryLimitMb} MB
                  </span>
                </div>
              </div>

              <div className="metric-item">
                <ShieldCheck size={18} />
                <div>
                  <span className="metric-label">
                    Sandbox
                  </span>
                  <span className="metric-value">
                    {metrics.status}
                  </span>
                </div>
              </div>

            </div>

            {/* Output Header */}
            <div className="output-header">
              Output
            </div>

            {/* Output Content */}
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