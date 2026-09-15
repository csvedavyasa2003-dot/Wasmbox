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
)

app = FastAPI(
    title="WasmBox API",
    description="Secure multi-tenant WebAssembly plugin sandbox",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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
