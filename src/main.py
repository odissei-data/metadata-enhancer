import requests
from fastapi import FastAPI, HTTPException

from schema.input import EnhancerInput
from version import get_version

app = FastAPI()


@app.get("/version", tags=["Version"])
async def info():
    result = get_version()
    return {"version": result}


@app.post('/dataverse-variable-enhancer', tags=['Dataverse metadata enhancer'])
async def dataverse_metadata_enhancer(enhancer_input: EnhancerInput) -> dict:
    dataverse_metadata = enhancer_input.metadata

    metadata_blocks = _try_for_key(
        dataverse_metadata,
        ['datasetVersion', 'metadataBlocks'],
        'Metadata does not contain datasetVersion or metadataBlocks key')

    elsst_topics = retrieve_elsst_topics(metadata_blocks)
    keywords = retrieve_keywords(metadata_blocks)

    for keyword in keywords:
        term = _try_for_key(keyword, ['keywordValue', 'value'],
                            'keywordValue field value not found in'
                            ' keyword metadata block')

        headers = {
            'accept': 'application/json',
        }

        params = {
            'label': term,
            'endpoint': 'https://fuseki.dev.odissei.nl/skosmos/sparql',
        }

        url = 'https://grlc.odissei.nl/api-git/odissei-data/grlc/' \
              'matchElsstTermForKeyword'

        response = requests.get(
            url,
            params=params,
            headers=headers,
        )
        if not response.ok:
            raise HTTPException(status_code=response.status_code,
                                detail=response.text)

        terms_dict = response.json()

        terms = _try_for_key(terms_dict, ['results', 'bindings'],
                             'grlc endpoint return badly formatted JSON.')

        elsst_topic_dict = retrieve_elsst_topic_keyword(elsst_topics, keyword)
        print(f'dict: {elsst_topic_dict}')
        for term in terms:
            add_keyword_elsst_label(elsst_topic_dict, term)
            add_keyword_elsst_uri(elsst_topic_dict, term)

    return dataverse_metadata


def retrieve_variables(metadata_blocks: dict) -> list:
    keys = ['variableInformation', 'fields']
    fields = _try_for_key(metadata_blocks, keys,
                          'variableInformation metadata block not found.'
                          ' JSON might be formatted incorrectly.')

    variable_block = next((fields for field in fields if
                           field.get('typeName') == 'variable'), None)[0]
    return variable_block['value']


def _try_for_key(dictionary: dict, key_path: list, exception_detail: str):
    value = dictionary
    for key in key_path:
        try:
            value = value[key]
        except (KeyError, TypeError):
            raise HTTPException(status_code=400, detail=exception_detail)
    return value


def retrieve_keywords(metadata_blocks: dict) -> list:
    keys = ['citation', 'fields']
    fields = _try_for_key(
        metadata_blocks,
        keys,
        'citation metadata block not found. '
        'JSON might be formatted incorrectly.'
    )

    keyword_block = next((field for field in fields if
                          field.get('typeName') == 'keyword'), None)

    return keyword_block['value']


def retrieve_elsst_topics(metadata_blocks: dict):
    keys = ['elsstTopic', 'fields']
    fields = _try_for_key(
        metadata_blocks,
        keys,
        'elsstTopic metadata block not found. '
        'JSON might be formatted incorrectly.'
    )

    elsst_block = next((field for field in fields if
                        field.get('typeName') == 'elsstTopic'), None)

    return elsst_block['value']


def retrieve_elsst_topic_keyword(elsst_topics, keyword):
    keyword_value = _try_for_key(
        keyword,
        ['keywordValue', 'value'],
        'No keywordValue found in keyword block'
    )

    for topic in elsst_topics:
        topic_keyword = _try_for_key(
            topic,
            ['keyword', 'value'],
            'No keyword or value key in keywordValue dict'
        )

        if topic_keyword == keyword_value:
            return topic
    raise HTTPException(status_code=400,
                        detail='Could not find ')


def add_keyword_elsst_uri(elsst_topic_dict: dict, term: dict):
    try:
        uri = term['iri']['value']
    except KeyError:
        raise HTTPException(status_code=400,
                            detail='No uri found for ELSST term')
    varUri = 'elsstVarUri'

    elsst_topic_dict[varUri] = {
        "typeName": varUri,
        "multiple": False,
        "typeClass": "primitive",
        "value": uri
    }
    print(f'keyword uri added: {elsst_topic_dict}')


def add_keyword_elsst_label(elsst_topic_dict: dict, term: dict):
    print(term)
    print(term['lbl']['value'])
    try:
        label = term['lbl']['value']
    except KeyError:
        raise HTTPException(status_code=404,
                            detail='No label found for ELSST term')
    varLabel = 'elsstVarLabel'
    print('ik kom hier')

    elsst_topic_dict[varLabel] = {
        "typeName": varLabel,
        "multiple": False,
        "typeClass": "primitive",
        "value": label
    }

    print(f'keyword label added: {elsst_topic_dict}')

#
# def add_elsst_uri_to_metadata(variable: dict, term: dict):
#     try:
#         uri = term['iri']['value']
#     except KeyError:
#         raise HTTPException(status_code=404,
#                             detail='No uri found for ELSST term')
#
#     varLabel = 'elsstVarURI1'
#     variable[varLabel] = {
#         "typeName": varLabel,
#         "multiple": False,
#         "typeClass": "primitive",
#         "value": uri
#     }
#
#
# def add_elsst_label_to_metadata(variable: dict, term: dict):
#     varLabel = 'elsstVarLabel1'
#
#     try:
#         label = term['lbl']['value']
#     except KeyError:
#         raise HTTPException(status_code=404,
#                             detail='No label found for ELSST term')
#
#     variable[varLabel] = {
#         "typeName": varLabel,
#         "multiple": False,
#         "typeClass": "primitive",
#         "value": label
#     }
