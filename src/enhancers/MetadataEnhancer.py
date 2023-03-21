import requests
from fastapi import HTTPException

from utils import _try_for_key


class MetadataEnhancer:
    """

    """

    def __init__(self, metadata):
        self._metadata = metadata
        self.metadata_blocks = _try_for_key(
            metadata,
            ['datasetVersion', 'metadataBlocks'],
            'Metadata does not contain datasetVersion or metadataBlocks key'
        )

    @property
    def metadata(self):
        return self._metadata

    def enhance_metadata(self):
        pass

    def get_value_from_metadata(self, metadata_field_name, metadata_block):
        fields = _try_for_key(
            self.metadata_blocks,
            [metadata_block, 'fields'],
            'variableInformation metadata block not found. '
            'JSON might be formatted incorrectly.'
        )

        metadata_field = next((field for field in fields if
                               field.get('typeName') == metadata_field_name),
                              None)

        return metadata_field['value']

    @staticmethod
    def query_matched_terms(value_to_match, endpoint, sparql_endpoint):
        headers = {
            'accept': 'application/json',
            'Content-type': 'application/json',
        }

        params = {
            'label': value_to_match,
            'endpoint': sparql_endpoint,
        }

        url = 'https://grlc.odissei.nl/api-git/odissei-data/grlc/' + endpoint
        print(url)
        response = requests.get(
            url,
            params=params,
            headers=headers,
        )
        print(response.text)
        if not response.ok:
            raise HTTPException(status_code=response.status_code,
                                detail=response.text)
        return response.json()

    def add_terms_to_metadata(self, **kwargs):
        pass
