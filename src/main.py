from fastapi import FastAPI

from enhancers.KeywordEnhancer import KeywordEnhancer
from enhancers.VariableEnhancer import VariableEnhancer
from schema.input import EnhancerInput
from version import get_version

app = FastAPI()


@app.get("/version", tags=["Version"])
async def info():
    result = get_version()
    return {"version": result}


@app.post('/dataverse-keyword-enhancer', tags=['Dataverse keyword enhancer'])
async def dataverse_keyword_enhancer(
        enhancer_input: EnhancerInput) -> dict:
    keyword_enhancer = KeywordEnhancer(
        enhancer_input.metadata,
        'matchElsstTermForKeyword',
        'https://fuseki.odissei.nl/skosmos/sparql'
    )
    keyword_enhancer.enhance_metadata()
    return keyword_enhancer.metadata


@app.post('/dataverse-variable-enhancer', tags=['Dataverse metadata enhancer'])
async def dataverse_metadata_enhancer(enhancer_input: EnhancerInput) -> dict:
    variable_enhancer = VariableEnhancer(
        enhancer_input.metadata,
        'getCbsVarUri',
        'https://fuseki.odissei.nl/skosmos/sparql'
    )
    variable_enhancer.enhance_metadata()
    return variable_enhancer.metadata
