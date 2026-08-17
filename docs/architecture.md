# WasmBox Architecture

## 1. Project Overview

WasmBox is a secure multi-tenant WebAssembly plugin sandbox designed to execute untrusted customer Python plugins in an isolated environment.

The system uses WebAssembly and Wasmtime to provide controlled plugin execution while restricting access to sensitive host resources such as the filesystem and network.

---

## 2. Project Goals

The main goals of WasmBox are:

- Safely execute untrusted Python plugins.
- Compile Python plugins into WebAssembly.
- Execute WebAssembly modules using Wasmtime.
- Isolate plugin execution from the host system.
- Restrict filesystem and network access.
- Apply execution and resource limits.
- Provide a developer portal for creating and testing plugins.
- Manage saved plugins and execution results.
- Provide a clean API for integrating the compiler, runtime, security and frontend components.

---

## 3. High-Level Architecture

```text
                    User
                     │
                     ▼
          React + Monaco Portal
                     │
                     ▼
              FastAPI Backend
             / Integration API
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
    Compiler      Runtime     Plugin Manager
        │            │
        │            ▼
        │         Security
        │         Sandbox
        │            │
        │            ▼
        │         Wasmtime
        │            │
        └────────────┤
                     ▼
              Execution Result
                     │
                     ▼
                React Portal