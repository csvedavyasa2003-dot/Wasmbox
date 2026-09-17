import { useState } from "react"
import Editor from "@monaco-editor/react"

import {
  compileComponent,
  runComponent,
} from "./services/api"

function App() {
  const [code, setCode] = useState(
    `import wit_world


class WitWorld(wit_world.WitWorld):
    def greet(self, name: str) -> str:
        return f"Hello, {name}!"
`
  )

  const [moduleId, setModuleId] = useState("hello")
  const [name, setName] = useState("Vedavyasa")
  const [output, setOutput] = useState("Output will appear here.")

  const [isCompiling, setIsCompiling] = useState(false)
  const [isRunning, setIsRunning] = useState(false)
  const [isCompiled, setIsCompiled] = useState(false)

  const handleCompile = async () => {
    setIsCompiling(true)
    setIsCompiled(false)
    setOutput("Compiling component...")

    try {
      const result = await compileComponent(code, moduleId)

      if (result.success) {
        setOutput(
          `Compilation successful:

Module: ${result.module_id}
Size: ${result.size_bytes} bytes

You can now run the component.`
        )

        setIsCompiled(true)
      } else {
        setOutput(
          `Compilation failed:

${result.error || "Unknown compilation error"}`
        )

        setIsCompiled(false)
      }
    } catch (error) {
      setOutput(
        `Compilation failed:

${error.message}`
      )

      setIsCompiled(false)
    } finally {
      setIsCompiling(false)
    }
  }

  const handleRun = async () => {
    if (!isCompiled) {
      setOutput(
        "Please compile the current code successfully before running."
      )
      return
    }

    setIsRunning(true)
    setOutput("Running component...")

    try {
      const compiledModuleId = moduleId.endsWith(".wasm")
        ? moduleId
        : `${moduleId}.wasm`

      const result = await runComponent(compiledModuleId, name)

      setOutput(
        `Result:
${result.result}

Status: ${result.status}
Execution time: ${result.execution_time_ms} ms`
      )
    } catch (error) {
      setOutput(
        `Execution failed:

${error.message}`
      )
    } finally {
      setIsRunning(false)
    }
  }

  const handleCodeChange = (value) => {
    setCode(value || "")
    setIsCompiled(false)
  }

  const handleModuleIdChange = (event) => {
    setModuleId(event.target.value)
    setIsCompiled(false)
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
            disabled={!isCompiled || isCompiling || isRunning}
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
            <div className="output-header">
              Output
            </div>

            <div className="output-content">
              <pre>{output}</pre>
            </div>
          </div>
        </div>

        <div className="component-settings">
          <label>
            Module ID
            <input
              type="text"
              value={moduleId}
              onChange={handleModuleIdChange}
              placeholder="hello"
              disabled={isCompiling || isRunning}
            />
          </label>

          <label>
            Name
            <input
              type="text"
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="Vedavyasa"
              disabled={isCompiling || isRunning}
            />
          </label>
        </div>
      </main>
    </div>
  )
}

export default App