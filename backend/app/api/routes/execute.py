from fastapi import APIRouter
from pydantic import BaseModel

from app.services.runtime_service import RuntimeService

router = APIRouter(
    prefix="/api/execute",
    tags=["Execution"]
)

runtime_service = RuntimeService()


class ExecuteRequest(BaseModel):
    module_id: str


@router.post("/")
def execute_plugin(request: ExecuteRequest):
    return runtime_service.execute(request.module_id)