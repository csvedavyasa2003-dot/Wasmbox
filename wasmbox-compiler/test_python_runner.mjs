import { executePython } from "./python_runner.mjs"

const result = await executePython(`
print("Before error")
print(10 / 0)
print("This should not execute")
`)

console.log("Execution result:")
console.log(result)