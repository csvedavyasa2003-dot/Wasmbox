import { executePython } from "./python_runner.mjs"

const chunks = []

process.stdin.setEncoding("utf8")

process.stdin.on("data", (chunk) => {
  chunks.push(chunk)
})

process.stdin.on("end", async () => {
  try {
    const code = chunks.join("")

    const result = await executePython(code)

    process.stdout.write(JSON.stringify(result))
  } catch (error) {
    process.stdout.write(
      JSON.stringify({
        success: false,
        output: "",
        error: error.message
      })
    )

    process.exitCode = 1
  }
})