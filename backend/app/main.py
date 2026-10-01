import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.routes import (
    compile,
    compile_component,
    execute,
    execution_history,
    plugins,
    run,
    run_component,
    run_python,
)

app = FastAPI(
    title="WasmBox API",
    description="Secure multi-tenant WebAssembly plugin sandbox",
    version="0.1.0",
)

allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:5174"
).split(",")

print("CORS ALLOWED ORIGINS:", allowed_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "WasmBox API is running",
        "status": "ok",
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "WasmBox",
    }


app.include_router(compile.router)
app.include_router(execute.router)
app.include_router(plugins.router)
app.include_router(run.router)
app.include_router(run_component.router)
app.include_router(compile_component.router)
app.include_router(execution_history.router)
app.include_router(run_python.router)