from pydantic import BaseModel


class AddRequest(BaseModel):
    a: int
    b: int


class WasmRunRequest(BaseModel):
    filename: str
    a: int
    b: int