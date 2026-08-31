import { loadPyodide } from "./pyodide/pyodide.mjs"

const pyodide = await loadPyodide()

let output = ""

pyodide.setStdout({
  batched: (msg) => {
    output += msg + "\n"
  }
})

pyodide.runPython(`
print("Hello from WasmBox!")
print(2 + 3)
print("Python execution successful")
`)

console.log("Pyodide version:", pyodide.version)
console.log("Captured output:")
console.log(output)