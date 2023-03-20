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

    elsst_topics = create_elsst_topics(metadata_blocks)
    keywords = retrieve_keywords(metadata_blocks)

    for keyword in keywords:
        term = _try_for_key(keyword, ['keywordValue', 'value'],
                            'keywordValue field value not found in'
                            ' keyword metadata block')

        headers = {
            'accept': 'application/json',
            'Content-type': 'application/json',
        }
        print(headers)
        params = {
            'label': term,
            'endpoint': 'https://fuseki.odissei.nl/skosmos/sparql',
        }

        url = 'https://grlc.odissei.nl/api-git/odissei-data/grlc/' \
              'matchElsstTermForKeyword'

        response = requests.get(
            url,
            params=params,
            headers=headers,
        )
        print(response.status_code)
        if not response.ok:
            raise HTTPException(status_code=response.status_code,
                                detail=response.text)
        print(response.text)
        terms_dict = response.json()

        terms = _try_for_key(terms_dict, ['results', 'bindings'],
                             'grlc endpoint returned badly formatted JSON.')

        topic = create_elsst_topic_keyword(elsst_topics, term)
        print(f'dict: {topic}')
        counter = 0
        for term in terms:
            counter += 1
            add_keyword_elsst_label(topic, term, counter)
            add_keyword_elsst_uri(topic, term, counter)

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


def create_elsst_topics(metadata_blocks: dict):
    metadata_blocks["elsstTopic"] = {
        "displayName": "ELSST Topics",
        "name": "elsstTopics",
        "fields": [
        ]
    }

    return metadata_blocks["elsstTopic"]["fields"]


def create_elsst_topic_keyword(elsst_topics: list, term: str):
    print(f'elsst topic: {elsst_topics}')

    topic = {
        "keyword": {
            "typeName": 'keyword',
            "multiple": False,
            "typeClass": "primitive",
            "value": term
        }
    }

    elsst_topics.append(
        {
            "typeName": "topic",
            "multiple": True,
            "typeClass": "compound",
            "value": [
                topic
            ]
        }
    )

    return topic


def add_keyword_elsst_uri(topic: dict, term: dict, counter: int):
    uri = _try_for_key(term, ['iri', 'value'], 'No uri found for ELSST term')
    varUri = 'elsstVarUri' + str(counter)

    topic[varUri] = {
        "typeName": varUri,
        "multiple": False,
        "typeClass": "primitive",
        "value": uri
    }
    print(f'keyword uri added: {topic}')


def add_keyword_elsst_label(elsst_topic_dict: dict, term: dict, counter: int):
    label = _try_for_key(term, ['lbl', 'value'],
                         'No label found for ELSST term')

    varLabel = 'elsstVarLabel' + str(counter)

    elsst_topic_dict[varLabel] = {
        "typeName": varLabel,
        "multiple": False,
        "typeClass": "primitive",
        "value": label
    }

    print(f'keyword label added: {elsst_topic_dict}')
