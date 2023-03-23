from enhancers.MetadataEnhancer import MetadataEnhancer
from utils import _try_for_key


class VariableEnhancer(MetadataEnhancer):

    def __init__(self, metadata: dict, endpoint: str, sparql_endpoint: str):
        super().__init__(metadata, endpoint, sparql_endpoint)

    def enhance_metadata(self):
        """ enhance_metadata implementation for the variable enhancements.

        First the variables in the variableInformation metadata block are
        retrieved. Then for all variables we match a term using the grlc API.
        Finally, we add the terms to the metadata inside the variable field.
        """
        variables = self.get_value_from_metadata('variable',
                                                 'variableInformation')

        for variable_dict in variables:
            variable = _try_for_key(variable_dict, ['variableName', 'value'],
                                    'variableName field value not found')

            terms_dict = self.query_matched_terms(
                variable
            )

            terms = _try_for_key(
                terms_dict,
                ['results', 'bindings'],
                'grlc endpoint returned badly formatted JSON.'
            )
            self.add_terms_to_metadata(terms, variable_dict)

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
        uri = _try_for_key(term, ['iri', 'value'],
                           'No uri found for ELSST term')
        variable_type_name = 'variableVocabularyURI'
        self.add_term_to_metadata_field(variable_dict, variable_type_name, uri)
