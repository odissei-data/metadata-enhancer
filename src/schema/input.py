from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EnhancerInput(BaseModel):
    metadata: Any = Field(..., description="Metadata as a list or dict")


class VocabInput(BaseModel):
    metadata: Any = Field(..., description="Metadata as a list or dict")
    endpoint: str = Field(..., description="The endpoint URL of the vocabulary service")
    vocabulary: str = Field(..., description="The vocabulary identifier")
    vocabulary_name: str = Field(..., description="The human-readable name of the vocabulary")
    language: str = Field(..., description="The language code (e.g., 'nl' for Dutch)")
    terms: list[str] = Field(..., description="A list of terms to look up in the vocabulary")


class Lang(str, Enum):
    en = "en"
    nl = "nl"


class LangInput(BaseModel):
    language: Lang
