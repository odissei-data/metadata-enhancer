import os

from fastapi import FastAPI

from enhancers.KeywordEnhancer import KeywordEnhancer
from enhancers.VariableEnhancer import VariableEnhancer
from schema.input import EnhancerInput
from version import get_version

app = FastAPI()

KEYWORD_ENDPOINT = os.environ['KEYWORD_ENDPOINT']
VARIABLE_ENDPOINT = os.environ['VARIABLE_ENDPOINT']
KEYWORD_VOCABULARY_URL = os.environ['KEYWORD_VOCABULARY_URL']
VARIABLE_VOCABULARY_URL = os.environ['VARIABLE_VOCABULARY_URL']


@app.get("/version", tags=["Version"])
async def info():
    result = get_version()
    return {"version": result}


@app.post('/dataverse-keyword-enhancer', tags=['Dataverse keyword enhancer'])
async def dataverse_keyword_enhancer(
        enhancer_input: EnhancerInput) -> dict:
    keyword_enhancer = KeywordEnhancer(
        enhancer_input.metadata,
        KEYWORD_ENDPOINT,
        KEYWORD_VOCABULARY_URL
    )
    keyword_enhancer.enhance_metadata()
    return keyword_enhancer.metadata


@app.post('/dataverse-variable-enhancer', tags=['Dataverse metadata enhancer'])
async def dataverse_metadata_enhancer(enhancer_input: EnhancerInput) -> dict:
    variable_enhancer = VariableEnhancer(
        enhancer_input.metadata,
        VARIABLE_ENDPOINT,
        VARIABLE_VOCABULARY_URL
    )
    variable_enhancer.enhance_metadata()
    return variable_enhancer.metadata
