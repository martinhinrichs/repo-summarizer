from typing import Optional
from pydantic import BaseModel

class File(BaseModel):
    path: str
    summary: Optional[str] = None
    hash: str

    class Config:
        schema_extra = {
            "example": {
                "path": "src/example.py",
                "summary": "This is an example Python file.",
                "hash": "a3f6b90dd3c9ab3e8d3f10c0303e433c"
            }
        }

