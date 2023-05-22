import os

from cachetools import TTLCache
from fastapi import FastAPI

from enhancers.ELSSTEnhancer import ELSSTEnhancer
from enhancers.VariableEnhancer import VariableEnhancer
from schema.input import EnhancerInput
from version import get_version

app = FastAPI()

ROOT_API_URL = os.environ['ROOT_API_URL']
ELSST_ENDPOINT = os.environ['ELSST_ENDPOINT']
VARIABLE_ENDPOINT = os.environ['VARIABLE_ENDPOINT']
ELSST_VOCABULARY_URL = os.environ['ELSST_VOCABULARY_URL']
VARIABLE_VOCABULARY_URL = os.environ['VARIABLE_VOCABULARY_URL']

MAX_SIZE = 1024
TTL = 12000

# Create a global cache object
cache = TTLCache(maxsize=MAX_SIZE, ttl=TTL)


@app.get("/version", tags=["Version"])
async def info():
    result = get_version()
    return {"version": result}


@app.post('/dataverse-ELSST-enhancer', tags=['Dataverse ELSST enhancer'])
async def dataverse_ELSST_enhancer(
        enhancer_input: EnhancerInput) -> dict:
    ELSST_enhancer = ELSSTEnhancer(
        enhancer_input.metadata,
        ROOT_API_URL + ELSST_ENDPOINT,
        ELSST_VOCABULARY_URL
    )
    ELSST_enhancer.enhance_metadata()
    return ELSST_enhancer.metadata


@app.post('/dataverse-variable-enhancer', tags=['Dataverse metadata enhancer'])
async def dataverse_metadata_enhancer(enhancer_input: EnhancerInput) -> dict:
    variable_enhancer = VariableEnhancer(
        enhancer_input.metadata,
        ROOT_API_URL + VARIABLE_ENDPOINT,
        VARIABLE_VOCABULARY_URL,
        cache
    )
    await variable_enhancer.enhance_metadata()
    return variable_enhancer.metadata
