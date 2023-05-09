import json
from unittest.mock import patch, AsyncMock

import pytest
from cachetools import TTLCache
from fastapi import HTTPException
from ..enhancers import ELSSTEnhancer, VariableEnhancer

cache = TTLCache(maxsize=1024, ttl=12000)


def open_json_file(json_path):
    with open(json_path) as f:
        return json.load(f)


@pytest.fixture()
def cbs_metadata():
    return open_json_file("test-data/input-data/cbs-metadata-input.json")


@pytest.fixture()
def cbs_keyword_output():
    return open_json_file("test-data/output-data/cbs-keyword-output.json")


@pytest.fixture()
def cbs_variable_output():
    return open_json_file("test-data/output-data/cbs-variable-output.json")


@pytest.fixture()
def ELSST_enhancer(cbs_metadata):
    return ELSSTEnhancer(
        cbs_metadata,
        'https://grlc.odissei.nl/api-git/odissei-data/grlc/'
        'matchElsstTermForKeyword',
        'https://fuseki.odissei.nl/skosmos/sparql'
    )


@pytest.fixture()
def variable_enhancer(cbs_metadata):
    return VariableEnhancer(
        cbs_metadata,
        'https://grlc.odissei.nl/api-git/odissei-data/grlc/getCbsVarUri',
        'https://fuseki.odissei.nl/skosmos/sparql',
        cache
    )


def test_e2e_ELSST_enhancer(keyword_enhancer, cbs_keyword_output):
    # Application test of the keyword enhancer
    ELSST_enhancer.enhance_metadata()
    assert ELSST_enhancer.metadata == cbs_keyword_output


@pytest.mark.asyncio
async def test_e2e_variable_enhancer(variable_enhancer, cbs_metadata,
                                     cbs_variable_output):
    # Application test of the variable enhancer

    await variable_enhancer.enhance_metadata()
    assert variable_enhancer.metadata == cbs_variable_output

    # Test enhancing with cache
    http_client_mock = AsyncMock()
    variable_enhancer_cached = VariableEnhancer(
        cbs_metadata,
        'https://grlc.odissei.nl/api-git/odissei-data/grlc/getCbsVarUri',
        'https://fuseki.odissei.nl/skosmos/sparql',
        cache
    )

    with patch('httpx.AsyncClient', return_value=http_client_mock):
        await variable_enhancer_cached.enhance_metadata()

    assert variable_enhancer_cached.metadata == cbs_variable_output
    http_client_mock.get.assert_not_called()


def test_get_value_cbs_from_metadata(variable_enhancer, cbs_metadata):
    # Test getting the value of the 'variableInformation' block from metadata
    value = variable_enhancer.get_value_from_metadata('variable',
                                                      'variableInformation')
    assert isinstance(value, list)
    assert len(value) == 3

    # Test getting the value of a non-existing metadata field
    with pytest.raises(HTTPException):
        variable_enhancer.get_value_from_metadata('nonexistent_field',
                                                  'variableInformation')


def test_query_enhancements(variable_enhancer):
    # Test querying for a term that exists in the SPARQL endpoint
    enhancements_dict = variable_enhancer.query_enhancements('RINPERSOON')
    assert isinstance(enhancements_dict, dict)
    assert 'results' in enhancements_dict
    assert 'bindings' in enhancements_dict['results']
    assert len(enhancements_dict['results']['bindings']) > 0

    # Test querying for a term that does not exist in the SPARQL endpoint
    enhancements_dict = variable_enhancer.query_enhancements(
        'nonexistent_enhancement')
    assert isinstance(enhancements_dict, dict)
    assert 'results' in enhancements_dict
    assert 'bindings' in enhancements_dict['results']
    assert len(enhancements_dict['results']['bindings']) == 0

# def test_add_terms_to_metadata(variable_enhancer):
#     # Test adding terms to a variable metadata field
#     terms = [
#         {
#             "label": {"type": "literal", "value": "GDP"},
#             "iri": {"type": "uri",
#                     "value": "http://www.europeandataportal.eu/skos/eurovoc/concept_scheme/100196"},
#         },
#         {
#             "label": {"type": "literal", "value": "Gross Domestic Product"},
#             "iri": {"type": "uri",
#                     "value": "http://www.europeandataportal.eu/skos/eurovoc/concept_scheme/100196"},
#         }
#     ]
