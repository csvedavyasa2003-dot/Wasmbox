import Editor from "@monaco-editor/react"

function App() {
  return (
    <div className="app">
      <header className="header">
        <h1>WasmBox</h1>

        <div className="actions">
          <button>Compile</button>
          <button>Run</button>
        </div>
      </header>

      <main className="main-content">
        <div className="editor-container">
          <Editor
            height="100%"
            language="python"
            theme="vs-dark"
            defaultValue="# Write your Python code here\nprint('Hello, WasmBox!')"
          />
        </div>
      </main>
    </div>
  )
}

export default App