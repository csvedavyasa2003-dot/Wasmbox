from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from compiler import run_python_plugin

app = FastAPI()

# Allow the React frontend (running on a different port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to Ankita's actual dev URL later, e.g. http://localhost:5173
    allow_methods=["*"],
    allow_headers=["*"],
)

class CompileRequest(BaseModel):
    code: str

@app.post("/api/compile")
def compile_plugin(request: CompileRequest):
    result = run_python_plugin(request.code)
    return result