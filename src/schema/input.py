from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EnhancerInput(BaseModel):
    metadata: list | dict | Any


class VocabInput(BaseModel):
    metadata: list | dict | Any
    endpoint: str = Field(example="https://vocabs.cbs.nl")
    vocabulary: str = Field(example="begrippen")
    vocabulary_name: str = Field(example="CBS concepts")
    language: str = Field(example="nl")
    terms: list = Field(example="keyword")


class Lang(str, Enum):
    en = "en"
    nl = "nl"


class LangInput(BaseModel):
    language: Lang
