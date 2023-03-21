from enhancers.MetadataEnhancer import MetadataEnhancer
from utils import _try_for_key


class VariableEnhancer(MetadataEnhancer):

    def __init__(self, metadata):
        super().__init__(metadata)

    def enhance_metadata(self):
        variables = self.get_value_from_metadata('variable',
                                                 'variableInformation')

        for variable in variables:
            print(f"variable: {variable}")
            term = _try_for_key(variable, ['variableName', 'value'], 'Ouch')

            terms_dict = self.query_matched_terms(
                term,
                'getCbsVarUri',
                'https://fuseki.odissei.nl/skosmos/sparql'
            )

            terms = _try_for_key(
                terms_dict,
                ['results', 'bindings'],
                'grlc endpoint returned badly formatted JSON.'
            )
            print('einde')
            self.add_terms_to_metadata(terms, variable)
            print('metadata toegevoegd')

    def add_terms_to_metadata(self, terms, variable):
        if not terms:
            return
        term = terms[0]
        uri = _try_for_key(term, ['iri', 'value'],
                           'No uri found for ELSST term')
        variable['variableURI'] = {
            "typeName": 'variableURI',
            "multiple": False,
            "typeClass": "primitive",
            "value": uri
        }
