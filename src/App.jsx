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
        <div className="editor-placeholder">
          Editor
        </div>
      </main>
    </div>
  )
}

export default App