import json
import pytest
from cachetools import TTLCache
from fastapi import HTTPException

from ..enhancers import ELSSTEnhancer, VariableEnhancer

cache = TTLCache(maxsize=1024, ttl=12000)


def open_json_file(json_path):
    with open(json_path) as f:
        return json.load(f)


@pytest.fixture()
def elsst_table():
    return open_json_file("test-data/table-data/elsst_table.json")


@pytest.fixture()
def cbs_table():
    return open_json_file("test-data/table-data/cbs_table.json")


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
def ELSST_enhancer(cbs_metadata, elsst_table):
    return ELSSTEnhancer(
        cbs_metadata,
        elsst_table
    )


@pytest.fixture()
def variable_enhancer(cbs_metadata, cbs_table):
    return VariableEnhancer(
        cbs_metadata,
        cbs_table
    )


def test_e2e_ELSST_enhancer(ELSST_enhancer, cbs_keyword_output):
    # Application test of the ELSST_enhancer
    ELSST_enhancer.enhance_metadata()
    assert ELSST_enhancer.metadata == cbs_keyword_output


def test_e2e_variable_enhancer(variable_enhancer, cbs_metadata,
                               cbs_variable_output):
    # Application test of the variable enhancer

    variable_enhancer.enhance_metadata()
    assert variable_enhancer.metadata == cbs_variable_output


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
    enrichment = variable_enhancer.query_enrichment_table('RINPERSOON')
    assert enrichment == "https://portal.odissei-data.nl/data/cbs/" \
                         "variableThesaurus/cf0133339b23e5a5f73799" \
                         "5ca64af06f98f14b8c5c827e8149f10b02934e07860"

    # Test querying for a term that does not exist in the SPARQL endpoint
    enrichment = variable_enhancer.query_enrichment_table(
        'nonexistent_enhancement')
    assert enrichment is None
