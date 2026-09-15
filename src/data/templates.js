export const pluginTemplates = [
  {
    name: "Hello World",
    code: `# Basic Python plugin
print("Hello, WasmBox!")`,
  },
  {
    name: "Addition",
    code: `# Add two numbers
a = 10
b = 20
print(a + b)`,
  },
  {
    name: "Multiplication",
    code: `# Multiply two numbers
a = 10
b = 5
print(a * b)`,
  },
  {
    name: "Loop Example",
    code: `# Simple loop
for i in range(1, 6):
    print(i)`,
  },
  {
    name: "Security Test",
    code: `# Sandbox security test
import os

print(os.listdir("."))`,
  },
]
