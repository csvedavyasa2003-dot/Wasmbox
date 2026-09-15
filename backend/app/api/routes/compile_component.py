from fastapi import APIRouter
from pydantic import BaseModel

from backend.app.services.component_compiler_service import (
    ComponentCompilerService,
)
from backend.app.services.source_validation_service import (
    source_validation_service,
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
    is_valid, validation_error = source_validation_service.validate(
        request.code
    )

    if not is_valid:
        return {
            "success": False,
            "output": "",
            "error": validation_error,
        }

    return compiler_service.compile(
        request.code,
        request.module_id,
    )
