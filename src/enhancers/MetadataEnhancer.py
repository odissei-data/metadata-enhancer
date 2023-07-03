from fastapi import HTTPException

from .utils import _try_for_key


class MetadataEnhancer:
    """ A super class used for enhancing Dataverse metadata.

    The MetadataEnhancer's is a class that describes the steps for enhancement.
    A class that implements MetadataEnhancer will need to mainly implement the
    enhance_metadata method. This method often consists out of four steps:
    1. Get the value to retrieve enhancements with from the metadata.
    2. Query an enrichment table to retrieve the matched enhancements.
    3. Add the matched enhancements to a specific location in the metadata.

    Step 1 and 2 are the same for all enhancers, that's why they are
    implemented in this super class.

    """

    def __init__(self, metadata: dict, enrichment_table: dict):
        self._metadata = metadata
        self.enrichment_table = enrichment_table
        self.metadata_blocks = _try_for_key(
            metadata,
            'datasetVersion.metadataBlocks',
        )

    @property
    def metadata(self):
        return self._metadata

    def enhance_metadata(self):
        pass

    def get_value_from_metadata(self, metadata_field_name: str,
                                metadata_block: str):
        """  Retrieves a field from a specific metadata block.

        :param metadata_field_name: The field to retrieve from the block.
        :param metadata_block: Specific metadata block inside the DV metadata.
        """
        fields = _try_for_key(
            self.metadata_blocks,
            f'{metadata_block}.fields'
        )

        metadata_field = next((field for field in fields if
                               field.get('typeName') == metadata_field_name),
                              None)

        if not metadata_field:
            raise HTTPException(
                status_code=400,
                detail=f'metadata does not contain {metadata_field_name}'
            )

        return metadata_field['value']

    def query_enrichment_table(self, value_to_match: str):
        """ Queries an enrichment table, uses the value to find the enrichment.

        :param value_to_match: The value to use for finding matches.
        """
        if value_to_match in self.enrichment_table.keys():
            return self.enrichment_table[value_to_match]
        else:
            return None

    def add_enhancements_to_metadata(self, enhancements: list,
                                     field_dict: dict):
        pass

    def add_enhancement_to_metadata_field(self, metadata_field: dict,
                                          type_name: str, value: str):
        """ Adds a matched enhancement to a specific metadata field.

        :param metadata_field: The metadata field to add the enhancement to.
        :param type_name: The type name of the enhancement added to the field.
        :param value: The value of the enhancement added to the field.
        """
        metadata_field[type_name] = {
            "typeName": type_name,
            "multiple": False,
            "typeClass": "primitive",
            "value": value
        }
