from utils import _try_for_key
from .MetadataEnhancer import MetadataEnhancer


class ELSSTEnhancer(MetadataEnhancer):
    """ This class can be used to enrich terms with ELSST in DV metadata. """

    def __init__(self, metadata: dict, enrichment_table: dict):
        """
        The enrichments metadata block is created to add the enhancements to.
        """
        super().__init__(metadata, enrichment_table)
        self.enrichment_block = self.create_metadata_block(
            "enrichments",
            "Enriched Metadata"
        )
        self.added_terms_set = set()

    def enhance_metadata(self):
        """ enhance_metadata implementation for the term enhancements. """

        self.ELSST_enhance_metadata('citation', 'keyword', 'keywordValue')
        self.ELSST_enhance_metadata('citation', 'topicClassification',
                                    'topicClassValue')

    def ELSST_enhance_metadata(self, metadata_block, compound_field, field):
        """ Handles the metadata enhancement of terms using ELSST matches.

        First a list of terms in the give compound in the given metadata block
        is retrieved. Then for all terms we match a term using the enrichment
        table. Finally, the terms are added to the enrichments metadata block.

        :param metadata_block: Contains compound field with matchable terms.
        :param compound_field: Contains the field that holds matchable terms.
        :param field: The field containing the matchable terms.
        """
        matchable_terms = self.get_value_from_metadata(compound_field,
                                                       metadata_block)
        for term_dict in matchable_terms:
            term = _try_for_key(term_dict, f'{field}.value')
            if term in self.added_terms_set:
                break

            elsst_term = self.create_elsst_term(term)
            label = term.upper()
            uri = self.query_enrichment_table(label)
            if uri:
                self.add_enhancement_uri(uri, 1, elsst_term)
                self.add_enhancement_label(label, 1, elsst_term)
                self.add_matched_term(elsst_term)
                self.added_terms_set.add(term)

    def add_enhancement_uri(self, uri: str, counter: int,
                            term_field: dict):
        uri_type_name = f'elsstVarUri{counter}'
        self.add_enhancement_to_compound_metadata_field(term_field,
                                                        uri_type_name, uri)

    def add_enhancement_label(self, label: str, counter: int,
                              term_field: dict):
        label_type_name = f'elsstVarLabel{counter}'
        self.add_enhancement_to_compound_metadata_field(term_field,
                                                        label_type_name,
                                                        label)

    def create_elsst_term(self, term: str) -> dict:
        """ Creates an elsst term field dict for a given term.

        :param term: The term to add to the field.
        """
        elsst_term = {
            "matchedTerm": {
                "typeName": 'matchedTerm',
                "multiple": False,
                "typeClass": "primitive",
                "value": term
            }
        }

        return elsst_term

    def add_matched_term(self, elsst_term):
        """ Adds a matched elsst term to the elsstTerm compound.

        :param elsst_term: The matched elsst term field dict.
        """
        self.enrichment_block.append(
            {
                "typeName": "elsstTerm",
                "multiple": True,
                "typeClass": "compound",
                "value": [
                    elsst_term
                ]
            }
        )
