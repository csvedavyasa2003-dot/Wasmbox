import { useState } from "react"
import "./App.css"
import Editor from "@monaco-editor/react"
import {
  Clock,
  MemoryStick,
  ShieldCheck,
  ShieldAlert,
} from "lucide-react"
import { compileCode, runCode } from "./services/api"
import { pluginTemplates } from "./data/templates"

function App() {
  const [code, setCode] = useState(
    "# Write your Python code here\nprint('Hello, WasmBox!')"
  )

  const [selectedTemplate, setSelectedTemplate] =
    useState("")

  const [output, setOutput] = useState(
    "Output will appear here."
  )

  const [isCompiling, setIsCompiling] =
    useState(false)

  const [isRunning, setIsRunning] =
    useState(false)

  const [moduleId, setModuleId] =
    useState(null)

  const [metrics, setMetrics] = useState({
    executionTimeMs: 0,
    memoryUsedMb: 0,
    memoryLimitMb: 128,
    status: "Ready",
  })

  const [violationDetail, setViolationDetail] =
    useState(null)

  const handleTemplateChange = (event) => {
    const templateName = event.target.value

    setSelectedTemplate(templateName)

    if (!templateName) {
      return
    }

    const selected = pluginTemplates.find(
      (template) =>
        template.name === templateName
    )

    if (!selected) {
      return
    }

    setCode(selected.code)
    setModuleId(null)

    setOutput(
      "Template loaded. Click Compile to continue."
    )

    setMetrics({
      executionTimeMs: 0,
      memoryUsedMb: 0,
      memoryLimitMb: 128,
      status: "Ready",
    })

    setViolationDetail(null)
  }

  const handleCompile = async () => {
    setIsCompiling(true)
    setOutput("Compiling...")
    setViolationDetail(null)

    try {
      const result = await compileCode(code)

      if (result.success) {
        setModuleId("test.wasm")

        setOutput(
          `Compilation successful.\n\nCompiler output:\n${
            result.stdout || ""
          }`
        )

        setMetrics((previous) => ({
          ...previous,
          status: "Ready",
        }))
      } else {
        setOutput(
          `Compilation failed.\n\n${
            result.error ||
            result.stderr ||
            "Unknown error"
          }`
        )

        if (
          result.error
            ?.toLowerCase()
            .includes("restricted") ||
          result.stderr
            ?.toLowerCase()
            .includes("restricted")
        ) {
          setViolationDetail({
            type: "BLOCKED",
            message:
              result.error ||
              result.stderr ||
              "Restricted operation blocked.",
          })

          setMetrics((previous) => ({
            ...previous,
            status: "BLOCKED",
          }))
        }
      }
    } catch (error) {
      setOutput(
        `Compilation failed:\n${error.message}`
      )
    } finally {
      setIsCompiling(false)
    }
  }

  const handleRun = async () => {
    if (!moduleId) {
      setOutput(
        "Please compile the code first."
      )
      return
    }

    setIsRunning(true)
    setOutput("Running...")
    setViolationDetail(null)

    setMetrics({
      executionTimeMs: 0,
      memoryUsedMb: 0,
      memoryLimitMb: 128,
      status: "Running",
    })

    try {
      const result = await runCode(
        moduleId,
        10,
        20
      )

      const executionTimeMs =
        Number(result.execution_time_ms) || 0

      const memoryBytes =
        Number(result.memory_bytes) || 0

      const memoryUsedMb = Number(
        (
          memoryBytes /
          (1024 * 1024)
        ).toFixed(2)
      )

      const securityStatus =
        result.security_status || "CLEAN"

      setMetrics({
        executionTimeMs,
        memoryUsedMb,
        memoryLimitMb: 128,
        status: securityStatus,
      })

      if (result.stderr) {
        setOutput(
          `stdout:\n${
            result.stdout || ""
          }\n\nstderr:\n${result.stderr}`
        )
      } else {
        setOutput(
          `stdout:\n${
            result.stdout || ""
          }`
        )
      }

      if (securityStatus !== "CLEAN") {
        setViolationDetail({
          type: securityStatus,
          message:
            result.stderr ||
            result.error ||
            "Sandbox security policy was triggered.",
        })
      } else {
        setViolationDetail(null)
      }
    } catch (error) {
      setOutput(
        `Execution failed:\n${error.message}`
      )

      setViolationDetail({
        type: "BLOCKED",
        message: error.message,
      })

      setMetrics((previous) => ({
        ...previous,
        status: "BLOCKED",
      }))
    } finally {
      setIsRunning(false)
    }
  }

  const handleCodeChange = (value) => {
    setCode(value || "")
    setSelectedTemplate("")

    setMetrics({
      executionTimeMs: 0,
      memoryUsedMb: 0,
      memoryLimitMb: 128,
      status: "Ready",
    })

    setViolationDetail(null)
  }

  return (
    <div className="app">

      <header className="header">

        <h1>WasmBox</h1>

        <div className="actions">

          <select
            className="template-selector"
            value={selectedTemplate}
            onChange={handleTemplateChange}
            disabled={
              isCompiling || isRunning
            }
          >
            <option value="">
              Select Template
            </option>

            {pluginTemplates.map(
              (template) => (
                <option
                  key={template.name}
                  value={template.name}
                >
                  {template.name}
                </option>
              )
            )}
          </select>

          <button
            onClick={handleCompile}
            disabled={
              isCompiling || isRunning
            }
          >
            {isCompiling
              ? "Compiling..."
              : "Compile"}
          </button>

          <button
            onClick={handleRun}
            disabled={
              isCompiling ||
              isRunning ||
              !moduleId
            }
          >
            {isRunning
              ? "Running..."
              : "Run"}
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
              onChange={handleCodeChange}
              options={{
                minimap: {
                  enabled: false,
                },
                fontSize: 14,
                automaticLayout: true,
              }}
            />

          </div>

          <div className="output-panel">

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

              <div
                className={`metric-item ${
                  violationDetail
                    ? "sandbox-violation"
                    : "sandbox-clean"
                }`}
              >

                {violationDetail ? (
                  <ShieldAlert size={18} />
                ) : (
                  <ShieldCheck size={18} />
                )}

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

            {violationDetail && (
              <div className="security-alert">

                <div className="security-alert-icon">
                  <ShieldAlert size={20} />
                </div>

                <div className="security-alert-content">

                  <div className="security-alert-title">
                    Sandbox Violation Detected
                  </div>

                  <div className="security-alert-message">
                    {violationDetail.message}
                  </div>

                </div>

                <div className="security-badge">
                  {violationDetail.type}
                </div>

              </div>
            )}

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