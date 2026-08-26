from pydantic import BaseModel


class RunRequest(BaseModel):
    module_id: str
    a: int
    b: int