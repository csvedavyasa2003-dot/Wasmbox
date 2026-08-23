import { useState } from "react"
import Editor from "@monaco-editor/react"

function App() {
  const [code, setCode] = useState(
    "# Write your Python code here\nprint('Hello, WasmBox!')"
  )

  const [output, setOutput] = useState("Output will appear here.")

  const handleCompile = () => {
    setOutput("Compile button clicked.\nCode is ready for compilation.")
  }

  const handleRun = () => {
    setOutput("Run button clicked.\nExecution will be connected later.")
  }

  return (
    <div className="app">
      <header className="header">
        <h1>WasmBox</h1>

        <div className="actions">
          <button onClick={handleCompile}>Compile</button>
          <button onClick={handleRun}>Run</button>
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