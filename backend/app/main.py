from fastapi import FastAPI

from app.api.routes import compile, execute, plugins


app = FastAPI(
    title="WasmBox API",
    description="Secure multi-tenant WebAssembly plugin sandbox",
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "message": "WasmBox API is running",
        "status": "ok"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "WasmBox"
    }


app.include_router(compile.router)
app.include_router(execute.router)
app.include_router(plugins.router)