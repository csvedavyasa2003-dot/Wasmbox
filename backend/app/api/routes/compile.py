from fastapi import APIRouter
from pydantic import BaseModel

from app.services.compiler_service import CompilerService

router = APIRouter(
    prefix="/api/compile",
    tags=["Compilation"]
)

compiler_service = CompilerService()


class CompileRequest(BaseModel):
    code: str


@router.post("/")
def compile_plugin(request: CompileRequest):
    return compiler_service.compile(request.code)