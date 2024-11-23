from pydantic import BaseModel,Field, model_validator
from typing import Literal

from typing import List



class SimilarIDS(BaseModel):
    list_similar_elements_id: List[int] = Field(
        description="List of ids having similarity with the Key element provided"
    )