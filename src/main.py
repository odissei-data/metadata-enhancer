import os

from fastapi import FastAPI

import terms
import utils
from enhancers.FrequencyEnhancer import FrequencyEnhancer
from enhancers.VocabularyEnhancer import VocabularyEnhancer
from enhancers.VariableEnhancer import VariableEnhancer
from queries import create_table_terms, CBS_VOCAB_QUERY, \
    ELSST_VOCAB_QUERY, create_table_concepts_skosmos
from schema.input import EnhancerInput
from version import get_version

app = FastAPI()

GITHUB_RAW_URL = os.environ['GITHUB_RAW_URL']
ELSST_VOCABULARY_URL = os.environ['ELSST_VOCABULARY_URL']
VARIABLE_VOCABULARY_URL = os.environ['VARIABLE_VOCABULARY_URL']

CBS_table = create_table_terms(VARIABLE_VOCABULARY_URL, CBS_VOCAB_QUERY)
ELSST_table = create_table_terms(ELSST_VOCABULARY_URL, ELSST_VOCAB_QUERY)
frequency_table = utils.load_tsv_from_github_raw(GITHUB_RAW_URL)
CBS_taxonomy_table = create_table_concepts_skosmos("https://vocabs.cbs.nl",
                                                   "taxonomie")
CBS_vocab_table = create_table_concepts_skosmos("https://vocabs.cbs.nl",
                                                "begrippen")


@app.get("/version", tags=["Version"])
async def info():
    result = get_version()
    return {"version": result}


@app.post('/dataverse-ELSST-enhancer', tags=['Dataverse ELSST enhancer'])
async def dataverse_ELSST_enhancer(
        enhancer_input: EnhancerInput) -> dict:
    ELSST_enhancer = VocabularyEnhancer(
        enhancer_input.metadata,
        ELSST_table,
        terms.ELSST_terms,
        terms.ELSST_type_dict
    )
    ELSST_enhancer.enhance_metadata()
    return ELSST_enhancer.metadata


@app.post('/dataverse-variable-enhancer', tags=['Dataverse variable enhancer'])
async def dataverse_metadata_enhancer(enhancer_input: EnhancerInput) -> dict:
    variable_enhancer = VariableEnhancer(
        enhancer_input.metadata,
        CBS_table
    )
    variable_enhancer.enhance_metadata()
    return variable_enhancer.metadata


@app.post('/dataverse-frequency-enhancer',
          tags=['Dataverse frequency enhancer'])
async def dataverse_frequency_enhancer(enhancer_input: EnhancerInput) -> dict:
    frequency_enhancer = FrequencyEnhancer(
        enhancer_input.metadata,
        frequency_table
    )
    frequency_enhancer.enhance_metadata()
    return frequency_enhancer.metadata


@app.post('/dataverse-cbs-taxonomy-enhancer',
          tags=['Dataverse CBS taxonomy enhancer'])
async def dataverse_cbs_taxonomy_enhancer(
        enhancer_input: EnhancerInput) -> dict:
    taxonomy_enhancer = VocabularyEnhancer(
        enhancer_input.metadata,
        CBS_taxonomy_table,
        terms.CBS_taxonomy_terms,
        terms.cbs_taxonomy_type_dict
    )
    taxonomy_enhancer.enhance_metadata()
    return taxonomy_enhancer.metadata


@app.post('/dataverse-cbs-vocab-enhancer', tags=['CBS vocab enhancer'])
async def dataverse_cbs_vocab_enhancer(enhancer_input: EnhancerInput) -> dict:
    vocab_enhancer = VocabularyEnhancer(
        enhancer_input.metadata,
        CBS_taxonomy_table,
        terms.CBS_vocab_terms,
        terms.cbs_vocab_type_dict
    )
    vocab_enhancer.enhance_metadata()
    return vocab_enhancer.metadata
