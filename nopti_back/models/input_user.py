from pydantic import BaseModel
from typing import Optional

class InputUser(BaseModel):
    input: str
    content_id: Optional[int] = None