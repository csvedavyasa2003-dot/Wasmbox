from fastapi import APIRouter
from pydantic import BaseModel

from backend.app.services.component_compiler_service import (
    ComponentCompilerService,
)


router = APIRouter(
    prefix="/api",
    tags=["Component Compilation"],
)

compiler_service = ComponentCompilerService()


class ComponentCompileRequest(BaseModel):
    code: str
    module_id: str


@router.post("/compile-component")
def compile_component(request: ComponentCompileRequest):
    return compiler_service.compile(
        request.code,
        request.module_id,
    )