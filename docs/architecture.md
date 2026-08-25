# WasmBox Architecture

## 1. Project Overview

WasmBox is a secure multi-tenant WebAssembly plugin sandbox designed to execute untrusted customer Python plugins in an isolated environment.

The system separates compilation, runtime execution, security, frontend interaction, and backend integration into independent components.

---

## 2. Architecture Goals

The main architecture goals are:

- Secure execution of untrusted plugins.
- Isolation between plugin executions.
- Separation of compiler and runtime components.
- Clear API boundaries between components.
- Resource and execution control.
- Easy integration with the developer portal.
- Independent development of project modules.

---

## 3. High-Level Architecture

```text
User
 |
 v
React + Monaco Developer Portal
 |
 v
FastAPI Backend / Integration Layer
 |
 +----------------+----------------+----------------+
 |                |                |
 v                v                v
Compiler        Runtime          Plugin
Component       Component        Management
 |                |
 v                v
Python -> WASM   Security
                 Sandbox
                    |
                    v
                 Wasmtime
                    |
                    v
             Execution Result
                    |
                    v
              React Portal

---

## 4. Core Components

### 4.1 FastAPI Backend / Integration Layer

The FastAPI backend acts as the central integration layer of WasmBox.

Its responsibilities include:

- Exposing REST API endpoints.
- Receiving requests from the developer portal.
- Validating API request data.
- Routing requests to the appropriate service interface.
- Providing a consistent interface between frontend and backend components.
- Returning execution and integration results to the client.

The backend does not directly implement the compiler, WebAssembly runtime, or security sandbox logic.

---

### 4.2 Compiler Integration

The `/api/compile/` endpoint provides the interface for submitting Python plugin source code to the compilation component.

The current integration flow is:

```text
Python Plugin Code
 |
 v
POST /api/compile/
 |
 v
Compile Route
 |
 v
CompilerService
 |
 v
Compilation Component