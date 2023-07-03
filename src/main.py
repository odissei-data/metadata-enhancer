import os

from fastapi import FastAPI

from enhancers.ELSSTEnhancer import ELSSTEnhancer
from enhancers.VariableEnhancer import VariableEnhancer
from queries import create_table_terms, CBS_VOCAB_QUERY, \
    ELSST_VOCAB_QUERY
from schema.input import EnhancerInput
from version import get_version

app = FastAPI()

ELSST_VOCABULARY_URL = os.environ['ELSST_VOCABULARY_URL']
VARIABLE_VOCABULARY_URL = os.environ['VARIABLE_VOCABULARY_URL']

CBS_table = create_table_terms(VARIABLE_VOCABULARY_URL, CBS_VOCAB_QUERY)
ELSST_table = create_table_terms(ELSST_VOCABULARY_URL, ELSST_VOCAB_QUERY)


@app.get("/version", tags=["Version"])
async def info():
    result = get_version()
    return {"version": result}


@app.post('/dataverse-ELSST-enhancer', tags=['Dataverse ELSST enhancer'])
async def dataverse_ELSST_enhancer(
        enhancer_input: EnhancerInput) -> dict:
    ELSST_enhancer = ELSSTEnhancer(
        enhancer_input.metadata,
        ELSST_table
    )
    ELSST_enhancer.enhance_metadata()
    return ELSST_enhancer.metadata


@app.post('/dataverse-variable-enhancer', tags=['Dataverse metadata enhancer'])
async def dataverse_metadata_enhancer(enhancer_input: EnhancerInput) -> dict:
    variable_enhancer = VariableEnhancer(
        enhancer_input.metadata,
        CBS_table
    )
    variable_enhancer.enhance_metadata()
    return variable_enhancer.metadata
