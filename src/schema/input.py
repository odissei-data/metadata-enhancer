from typing import Any

from pydantic import BaseModel


class EnhancerInput(BaseModel):
    metadata: list | dict | Any
