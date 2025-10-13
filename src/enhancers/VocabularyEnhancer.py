import jmespath

from utils import _try_for_key
from .MetadataEnhancer import MetadataEnhancer


class VocabularyEnhancer(MetadataEnhancer):
    """ Used to enrich terms with Vocabulary concepts in DV metadata. """

    def __init__(self, metadata: dict, enrichment_table: dict,
                 terms_list: list, vocab_name: str, type_name: str):
        """
        The enrichments metadata block is created to add the enhancements to.
        A terms set is created to avoid duplicate matched terms.
        The terms list tracks what terms from the original metadata should be
        used for matching.
        """
        super().__init__(metadata, enrichment_table)
        self.enrichment_block = self.create_metadata_block(
            "enrichments",
            "Enriched Metadata"
        )
        self.added_terms_set = set()
        self.terms_list = terms_list
        self.vocab_name = vocab_name
        self.type_name = type_name

    def enhance_metadata(self):
        """ enhance_metadata implementation for the term enhancements. """

        if 'keyword' in self.terms_list:
            self.vocab_enhance_metadata('citation', 'keyword', 'keywordValue')

        if 'topicClassification' in self.terms_list:
            self.vocab_enhance_metadata('citation', 'topicClassification',
                                        'topicClassValue')

    def vocab_enhance_metadata(self, metadata_block, compound_field, field):
        """ Handles the metadata enhancement of terms using concept matches.

        First a list of terms in the give compound in the given metadata block
        is retrieved. Then for all terms we match a term using the enrichment
        table. Finally, the terms are added to the enrichments metadata block.

        :param metadata_block: Contains compound field with matchable terms.
        :param compound_field: Contains the field that holds matchable terms.
        :param field: The field containing the matchable terms.
        """

        terms = []

        # extract
        matchable_terms = self.get_value_from_metadata(compound_field,
                                                       metadata_block)
        # match
        for term_dict in matchable_terms:
            term = _try_for_key(term_dict, f'{field}.value')
            if not term or term in self.added_terms_set:
                break
            label = term.upper()
            uri = self.query_enrichment_table(label)
            if uri:
                terms.append(uri)
        # add
        self.add_enhancements_to_metadata(terms)

    def add_enhancements_to_metadata(self, terms: list):
        """ Creates a single primitive multiple field with a list of terms """
        if not terms:
            return

        primitive_field = {
            "typeName": self.type_name,
            "multiple": True,
            "typeClass": "primitive",
            "value": terms
        }

        self.enrichment_block.append(primitive_field)
