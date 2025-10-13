import os
import terms
import utils
from starlette import status
from fastapi import FastAPI, HTTPException, Path
from enhancers.FrequencyEnhancer import FrequencyEnhancer
from enhancers.VocabularyEnhancer import VocabularyEnhancer
from enhancers.VariableEnhancer import VariableEnhancer
from api.queries import CBS_BEGRIPPEN_QUERY, CBS_TAXONOMIE_QUERY, CBS_VOCAB_QUERY
from api.skosmos import create_table_concepts_skosmos
from api.fuseki import create_table_terms
from schema.input import EnhancerInput, VocabInput, Lang
from version import get_version

app = FastAPI()
GITHUB_RAW_URL = os.environ['GITHUB_RAW_URL']
ELSST_FUSEKI_URL = os.environ['ELSST_FUSEKI_URL']
VARIABLE_FUSEKI_URL = os.environ['VARIABLE_FUSEKI_URL']
CBS_VOCAB_URL = os.environ['CBS_VOCAB_URL']
ELSST_VOCAB_URL = os.environ['ELSST_VOCAB_URL']

frequency_table = utils.load_tsv_from_github_raw(GITHUB_RAW_URL)
if frequency_table is None:
    raise RuntimeError("Failed to load frequency table.")

CBS_table = create_table_terms(VARIABLE_FUSEKI_URL, CBS_VOCAB_QUERY)
if CBS_table is None:
    raise RuntimeError("Failed to load CBS table.")

CBS_taxonomy_table = create_table_terms(CBS_VOCAB_URL, CBS_TAXONOMIE_QUERY)
if CBS_taxonomy_table is None:
    raise RuntimeError("Failed to load CBS taxonomy table.")

CBS_vocab_table = create_table_terms(CBS_VOCAB_URL, CBS_BEGRIPPEN_QUERY)
if CBS_vocab_table is None:
    raise RuntimeError("Failed to load CBS vocab table.")
ELSST_table = create_table_concepts_skosmos(ELSST_VOCAB_URL, "elsst-5",
                                                    Lang.nl)
if ELSST_table is None:
    raise RuntimeError("Failed to load ELSST table.")

ELSST_english_table = create_table_concepts_skosmos(ELSST_VOCAB_URL, "elsst-5",
                                                    Lang.en)
if ELSST_english_table is None:
    raise RuntimeError("Failed to load ELSST English table.")

@app.get("/version", tags=["Version"])
async def info():
    result = get_version()
    return {"version": result}


@app.post('/enrich/elsst/{language}', tags=['Vocabulary enrichment'])
async def enrich_with_ELSST(
        enhancer_input: EnhancerInput,
        language: Lang = Path(
            ..., title="Language",
            description="Choose the language for ELSST enrichment")) -> dict:

    if language == 'en':
        elsst_table = ELSST_english_table
    elif language == 'nl':
        elsst_table = ELSST_table
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid language specified, choose between 'en' and 'nl'.",
        )

    ELSST_enhancer = VocabularyEnhancer(
        enhancer_input.metadata,
        elsst_table,
        terms.ELSST_terms,
        "ELSST",
        "enrichedElsstClassification"
    )

    ELSST_enhancer.enhance_metadata()
    return ELSST_enhancer.metadata


@app.post('/enrich/variable', tags=['Variable enrichment'])
async def enrich_with_variable(enhancer_input: EnhancerInput) -> dict:
    variable_enhancer = VariableEnhancer(
        enhancer_input.metadata,
        CBS_table
    )
    variable_enhancer.enhance_metadata()
    return variable_enhancer.metadata


@app.post('/enrich/frequency',
          tags=['Frequency enrichment'])
async def enrich_with_frequency(enhancer_input: EnhancerInput) -> dict:
    frequency_enhancer = FrequencyEnhancer(
        enhancer_input.metadata,
        frequency_table
    )
    frequency_enhancer.enhance_metadata()
    return frequency_enhancer.metadata


@app.post('/enrich/cbs-taxonomy',
          tags=['Vocabulary enrichment'])
async def enrich_with_cbs_taxonomy(enhancer_input: EnhancerInput) -> dict:
    taxonomy_enhancer = VocabularyEnhancer(
        enhancer_input.metadata,
        CBS_taxonomy_table,
        terms.CBS_taxonomy_terms,
        "CBS taxonomy",
        "enrichedCbsTaxonomyTerm"
    )
    taxonomy_enhancer.enhance_metadata()
    return taxonomy_enhancer.metadata


@app.post('/enrich/cbs-concepts', tags=['Vocabulary enrichment'])
async def enrich_with_cbs_concepts(enhancer_input: EnhancerInput) -> dict:
    vocab_enhancer = VocabularyEnhancer(
        enhancer_input.metadata,
        CBS_vocab_table,
        terms.CBS_vocab_terms,
        "CBS concepts",
        "enrichedCbsConcept"
    )
    vocab_enhancer.enhance_metadata()
    return vocab_enhancer.metadata


@app.post('/enrich/vocabulary', tags=['Vocabulary enrichment'])
async def enrich_with_vocabulary(vocab_input: VocabInput) -> dict:
    vocab_table = create_table_concepts_skosmos(
        vocab_input.endpoint,
        vocab_input.vocabulary,
        vocab_input.language
    )
    vocab_enhancer = VocabularyEnhancer(
        vocab_input.metadata,
        vocab_table,
        vocab_input.terms,
        vocab_input.vocabulary_name,
        vocab_input.type_name
    )
    vocab_enhancer.enhance_metadata()
    return vocab_enhancer.metadata
