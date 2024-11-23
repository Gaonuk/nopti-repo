from pydantic import BaseModel
from typing import List, Literal

class ContentEntity(BaseModel):
    id: int
    title: str
    summary: str
    link: str
    date: str
    type: Literal["youtube", "article", "podcast"]
    passed: bool
    shown: bool