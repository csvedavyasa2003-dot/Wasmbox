from fastapi import APIRouter
from pydantic import BaseModel

from backend.app.services.compiler_service import CompilerService


router = APIRouter(
    prefix="/api",
    tags=["Python Execution"],
)

compiler_service = CompilerService()


class RunPythonRequest(BaseModel):
    code: str


@router.post("/run-python")
def run_python(request: RunPythonRequest):
    return compiler_service.compile(request.code)