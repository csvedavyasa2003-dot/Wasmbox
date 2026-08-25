import { useState } from "react"
import Editor from "@monaco-editor/react"

function App() {
  const [code, setCode] = useState(
    "# Write your Python code here\nprint('Hello, WasmBox!')"
  )

  const [output, setOutput] = useState("Output will appear here.")

  const [isCompiling, setIsCompiling] = useState(false)
  const [isRunning, setIsRunning] = useState(false)

  const handleCompile = () => {
    setIsCompiling(true)
    setOutput("Compiling...")

    setTimeout(() => {
      setIsCompiling(false)
      setOutput("Compilation completed.")
    }, 1000)
  }

  const handleRun = () => {
    setIsRunning(true)
    setOutput("Running...")

    setTimeout(() => {
      setIsRunning(false)
      setOutput("Execution completed.")
    }, 1000)
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