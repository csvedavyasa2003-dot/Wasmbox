# WasmBox API Contracts

## 1. Overview

This document defines the API contracts between the WasmBox
FastAPI integration layer and the other project components.

The API layer acts as the integration point between:

- React + Monaco Developer Portal
- Compilation Engine
- WASM Runtime
- Plugin Management
- Execution and monitoring components

The API contracts define the expected request and response
structures without implementing the internal compiler, runtime,
security, or frontend logic.

---

## 2. Base URL

During local development:

`http://127.0.0.1:8000`

---

## 3. API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | API service information |
| GET | `/health` | Health check |
| POST | `/api/compile/` | Submit Python code for compilation |
| POST | `/api/execute/` | Execute a compiled WASM module |
| GET | `/api/plugins/` | Retrieve available plugins |

---

# 4. Health Check API

## Endpoint

GET `/health`

## Purpose

Used by the frontend, deployment environment, or monitoring
system to verify that the WasmBox backend is running.

## Response

```json
{
  "status": "ok",
  "service": "WasmBox"
}