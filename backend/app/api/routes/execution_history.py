from fastapi import APIRouter

from backend.app.services.execution_history_service import (
    execution_history_service,
)


router = APIRouter(
    prefix="/api",
    tags=["Execution History"],
)


@router.get("/history")
def get_history():
    return execution_history_service.get_history()


@router.get("/metrics")
def get_metrics():
    return execution_history_service.get_metrics()
