import httpx
from threading import Lock
from fastapi import HTTPException
from cachetools import TTLCache
from httpx import AsyncClient

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
        retrieved. Then for all variables we find enhancements using an API.
        We add all the retrieved enhancements to the cache with the var as key.
        Finally, we add the enhancements to the metadata.
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
                    enhancements = cached_result
                    self.add_enhancements_to_metadata(enhancements,
                                                      variable_dict)
                else:
                    tasks.append(
                        self.query_enhancements_async(client, variable_dict,
                                                      variable))

            results = await gather_with_concurrency(CONCURRENCY_LIMIT, *tasks)
            for enhancements, variable, variable_dict in results:
                with self.lock:
                    self.cache[variable] = enhancements
                self.add_enhancements_to_metadata(enhancements, variable_dict)

    async def query_enhancements_async(self, client: AsyncClient,
                                       variable_dict: dict, variable: str):
        """ async query implementation for the variable matching API call

        :param client: httpx client.
        :param variable_dict: Dictionary of the variable field in the metadata.
        :param variable: Variable to query the enhancements with.
        :return: the fetched enhancements, the variable and the variable dict.
        """

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
                detail=f"Failed to query enhancement for variable: {variable}"
            )

        enhancements = _try_for_key(response.json(), 'results.bindings')
        return enhancements, variable, variable_dict

    def add_enhancements_to_metadata(self, enhancements: list,
                                     variable_dict: dict):
        """ Adds the variable enhancements to the metadata.

        If there are no enhancements, this method returns.
        Else it adds the first matched URI to the variable that was used to
        find the match.

        :param enhancements: Enhancements to add to the metadata.
        :param variable_dict: The variable field to add the enhancements to.
        """
        if not enhancements:
            return
        enhancement = enhancements[0]
        uri = _try_for_key(enhancement, 'iri.value')
        variable_type_name = 'variableVocabularyURI'
        self.add_enhancement_to_metadata_field(variable_dict,
                                               variable_type_name, uri)
