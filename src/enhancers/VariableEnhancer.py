from .MetadataEnhancer import MetadataEnhancer
from utils import _try_for_key


class VariableEnhancer(MetadataEnhancer):

    def __init__(self, metadata: dict, enrichment_table: dict):
        super().__init__(metadata, enrichment_table)

    def enhance_metadata(self):
        """ enhance_metadata implementation for the variable enhancements.

        First the variables in the variableInformation metadata block are
        retrieved. Then for all variables we find enhancements using a table..
        Finally, we add the enhancements to the metadata.
        """
        variables = self.get_value_from_metadata('odisseiVariable',
                                                 'variableInformation')
        for variable_dict in variables:
            variable = _try_for_key(variable_dict,
                                    'odisseiVariableName.value')
            variable_uri = self.query_enrichment_table(variable)
            if variable_uri:
                self.add_enhancement_to_compound_metadata_field(
                    variable_dict,
                    'odisseiVariableVocabularyURI',
                    variable_uri)
