from .MetadataEnhancer import MetadataEnhancer
from .utils import _try_for_key


class VariableEnhancer(MetadataEnhancer):

    def __init__(self, metadata: dict, enrichment_table: dict):
        super().__init__(metadata, enrichment_table)

    def enhance_metadata(self):
        """ enhance_metadata implementation for the variable enhancements.

        First the variables in the variableInformation metadata block are
        retrieved. Then for all variables we find enhancements using an API.
        We add all the retrieved enhancements to the cache with the var as key.
        Finally, we add the enhancements to the metadata.
        """
        variables = self.get_value_from_metadata('variable',
                                                 'variableInformation')
        for variable_dict in variables:
            variable = _try_for_key(variable_dict,
                                    'variableName.value')
            variable_uri = self.query_enrichment_table(variable)
            if variable_uri:
                self.add_enhancements_to_metadata(variable_uri, variable_dict)

    def add_enhancements_to_metadata(self, variable_uri: str,
                                     variable_dict: dict):
        """ Adds the variable enhancements to the metadata.

        If there are no enhancements, this method returns.
        Else it adds the first matched URI to the variable that was used to
        find the match.

        :param variable_uri: Enhancements to add to the metadata.
        :param variable_dict: The variable field to add the enhancements to.
        """
        variable_type_name = 'variableVocabularyURI'
        self.add_enhancement_to_metadata_field(variable_dict,
                                               variable_type_name,
                                               variable_uri)
