from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(
    prefix="/api/compile",
    tags=["Compilation"]
)


class CompileRequest(BaseModel):
    code: str


@router.post("/")
def compile_plugin(request: CompileRequest):
    return {
        "success": True,
        "message": "Compilation endpoint ready",
        "status": "pending",
        "code_length": len(request.code)
    }