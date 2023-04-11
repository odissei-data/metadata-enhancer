import copy

import httpx
from threading import Lock
from fastapi import HTTPException
from cachetools import TTLCache

from .MetadataEnhancer import MetadataEnhancer
from .utils import _try_for_key, gather_with_concurrency

CONCURRENCY_LIMIT = 25


class VariableEnhancer(MetadataEnhancer):

    def __init__(self, metadata: dict, endpoint: str, sparql_endpoint: str,
                 cache: TTLCache):
        super().__init__(metadata, endpoint, sparql_endpoint)
        self.cache = cache
        self.lock = Lock()

    async def enhance_metadata(self):
        """ enhance_metadata implementation for the variable enhancements.

        First the variables in the variableInformation metadata block are
        retrieved. Then for all variables we match a term using the grlc API.
        Finally, we add the terms to the metadata inside the variable field.
        """
        variables = self.get_value_from_metadata('variable',
                                                 'variableInformation')
        async with httpx.AsyncClient() as client:
            tasks = []
            for variable_dict in variables:
                variable = _try_for_key(variable_dict,
                                        'variableName.value')
                cached_result = self.cache.get(variable)
                if cached_result is not None:
                    terms = cached_result
                    self.add_terms_to_metadata(terms, variable_dict)
                else:
                    tasks.append(
                        self.query_matched_terms_async(client, variable_dict,
                                                       variable))

            results = await gather_with_concurrency(CONCURRENCY_LIMIT, *tasks)
            for terms, variable, variable_dict in results:
                with self.lock:
                    self.cache[variable] = terms
                self.add_terms_to_metadata(terms, variable_dict)

    async def query_matched_terms_async(self, client, variable_dict, variable):
        # Build request URL with the variable to match
        headers = {
            'accept': 'application/json',
            'Content-type': 'application/json',
        }

        params = {
            'label': variable,
            'endpoint': self.sparql_endpoint,
        }

        response = await client.get(url=self.endpoint, params=params,
                                    headers=headers)
        if response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to query matched term for variable: {variable}"
            )

        terms = _try_for_key(response.json(), 'results.bindings')
        return terms, variable, variable_dict

    def add_terms_to_metadata(self, terms: list, variable_dict: dict):
        """ Adds the terms matched on variables to the metadata

        If there are no matched terms, this method returns.
        Else it adds the first matched URI to the variable that was used to
        find the match.

        :param terms:
        :param variable_dict:
        :return:
        """
        if not terms:
            return
        term = terms[0]
        uri = _try_for_key(term, 'iri.value')
        variable_type_name = 'variableVocabularyURI'
        self.add_term_to_metadata_field(variable_dict, variable_type_name, uri)
