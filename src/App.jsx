
import { useEffect, useState } from "react"
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
import { loadDraft, saveDraft } from "./utils/draftStorage"

const DEFAULT_CODE =
  "# Write your Python code here\nprint('Hello, WasmBox!')"

const DEFAULT_METRICS = {
  executionTimeMs: 0,
  memoryUsedMb: 0,
  memoryLimitMb: 128,
  status: "Ready",
}

function App() {
  const [initialDraft] = useState(() => {
    try {
      return loadDraft()
    } catch {
      return null
    }
  })

  const [code, setCode] = useState(
    initialDraft?.code ?? DEFAULT_CODE
  )

  const [pluginTitle, setPluginTitle] = useState(
    initialDraft?.title ?? "Untitled Plugin"
  )

  const [selectedTemplate, setSelectedTemplate] = useState("")
  const [output, setOutput] = useState("Output will appear here.")
  const [isCompiling, setIsCompiling] = useState(false)
  const [isRunning, setIsRunning] = useState(false)
  const [metrics, setMetrics] = useState(DEFAULT_METRICS)
  const [violationDetail, setViolationDetail] = useState(null)

  useEffect(() => {
    try {
      saveDraft(code, pluginTitle)
    } catch (error) {
      console.error("Could not save draft:", error)
    }
  }, [code, pluginTitle])

  const resetResults = () => {
    setMetrics(DEFAULT_METRICS)
    setViolationDetail(null)
    setOutput("Code changed. Compile or run it to see the result.")
  }

  const handleTemplateChange = (event) => {
    const templateName = event.target.value
    setSelectedTemplate(templateName)

    if (!templateName) return

    const selected = pluginTemplates.find(
      (template) => template.name === templateName
    )

    if (!selected) return

    setCode(selected.code)
    setPluginTitle(selected.name)
    setMetrics(DEFAULT_METRICS)
    setViolationDetail(null)
    setOutput("Template loaded. Click Compile to validate the code.")
  }

  const handleCompile = async () => {
    setIsCompiling(true)
    setOutput("Validating Python code...")
    setMetrics({
      ...DEFAULT_METRICS,
      status: "Compiling",
    })
    setViolationDetail(null)

    try {
      const result = await compileCode(code)

      if (result.success) {
        setOutput(
          result.message || "Python code validation successful."
        )
        setMetrics({
          ...DEFAULT_METRICS,
          status: "Valid",
        })
      } else {
        const message =
          result.error ||
          result.stderr ||
          "Python code validation failed."

        setOutput(`Validation failed:\n${message}`)
        setMetrics({
          ...DEFAULT_METRICS,
          status: "BLOCKED",
        })

        if (message.toLowerCase().includes("restricted")) {
          setViolationDetail({
            type: "BLOCKED",
            message,
          })
        }
      }
    } catch (error) {
      setOutput(`Validation failed:\n${error.message}`)
      setMetrics({
        ...DEFAULT_METRICS,
        status: "ERROR",
      })
    } finally {
      setIsCompiling(false)
    }
  }

  const handleRun = async () => {
    setIsRunning(true)
    setOutput("Running Python code...")
    setMetrics({
      ...DEFAULT_METRICS,
      status: "Running",
    })
    setViolationDetail(null)

    try {
      const result = await runCode(code)
      const stdout = result.stdout || ""
      const stderr = result.stderr || ""
      const errorMessage = result.error || ""

      if (result.success) {
        setOutput(
          `stdout:\n${stdout || "(No output)"}${
            stderr ? `\n\nstderr:\n${stderr}` : ""
          }`
        )

        setMetrics({
          ...DEFAULT_METRICS,
          status: "Completed",
        })
      } else {
        const details =
          errorMessage || stderr || "Python execution failed."

        setOutput(
          `Execution failed:\n${stdout ? `${stdout}\n` : ""}${details}`
        )

        setMetrics({
          ...DEFAULT_METRICS,
          status: "ERROR",
        })

        if (details.toLowerCase().includes("restricted")) {
          setViolationDetail({
            type: "BLOCKED",
            message: details,
          })
          setMetrics({
            ...DEFAULT_METRICS,
            status: "BLOCKED",
          })
        }
      }
    } catch (error) {
      setOutput(`Execution failed:\n${error.message}`)
      setMetrics({
        ...DEFAULT_METRICS,
        status: "ERROR",
      })
    } finally {
      setIsRunning(false)
    }
  }

  const handleCodeChange = (value) => {
    setCode(value || "")
    setSelectedTemplate("")
    setMetrics(DEFAULT_METRICS)
    setViolationDetail(null)
  }

  const isBusy = isCompiling || isRunning

  return (
    <div className="app">
      <header className="header">
        <h1>WasmBox</h1>

        <div className="actions">
          <input
            className="plugin-title-input"
            type="text"
            value={pluginTitle}
            onChange={(event) =>
              setPluginTitle(event.target.value)
            }
            placeholder="Plugin title"
            aria-label="Plugin title"
            title="Enter or edit your plugin title"
            disabled={isBusy}
          />

          <select
            className="template-selector"
            value={selectedTemplate}
            onChange={handleTemplateChange}
            title="Choose a preset Python code template"
            aria-label="Select code template"
            disabled={isBusy}
          >
            <option value="">Select Template</option>

            {pluginTemplates.map((template) => (
              <option
                key={template.name}
                value={template.name}
              >
                {template.name}
              </option>
            ))}
          </select>

          <button
            onClick={handleCompile}
            title="Validate your Python code"
            disabled={isBusy}
          >
            {isCompiling ? "Compiling..." : "Compile"}
          </button>

          <button
            onClick={handleRun}
            title="Run the Python code in the editor"
            disabled={isBusy}
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
                    Execution Status
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
                    Restricted Operation Blocked
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
