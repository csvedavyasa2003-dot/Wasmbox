from pydantic import BaseModel, Field

class RunRequest(BaseModel):
    module_id: str = Field(..., min_length=1)
    a: int
    b: int