from utils import _try_for_key
from .MetadataEnhancer import MetadataEnhancer


class VocabularyEnhancer(MetadataEnhancer):
    """ Used to enrich terms with Vocabulary concepts in DV metadata. """

    def __init__(self, metadata: dict, enrichment_table: dict,
                 terms_list: list, type_dict: dict):
        """
        The enrichments metadata block is created to add the enhancements to.
        """
        super().__init__(metadata, enrichment_table)
        self.enrichment_block = self.create_metadata_block(
            "enrichments",
            "Enriched Metadata"
        )
        self.added_terms_set = set()
        self.terms_list = terms_list
        self.type_dict = type_dict

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
        # extract
        matchable_terms = self.get_value_from_metadata(compound_field,
                                                       metadata_block)
        # match
        for term_dict in matchable_terms:
            term = _try_for_key(term_dict, f'{field}.value')
            if term in self.added_terms_set:
                break

            # add
            term_field = {}
            matched_term_type_name = self.type_dict['matched_type']
            self.add_enhancement_to_compound_metadata_field(
                term_field,
                matched_term_type_name,
                term)
            label = term.upper()
            uri = self.query_enrichment_table(label)
            if uri:
                uri_type_name = f"{self.type_dict['uri_type']}1"
                label_type_name = f"{self.type_dict['label_type']}1"
                self.add_enhancement_to_compound_metadata_field(
                    term_field,
                    uri_type_name,
                    uri)
                self.add_enhancement_to_compound_metadata_field(
                    term_field,
                    label_type_name,
                    label)
                self.add_to_compound_field(self.type_dict['compound_type'],
                                           term_field)
                self.added_terms_set.add(term)
