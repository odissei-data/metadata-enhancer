import jmespath

from utils import _try_for_key
from .MetadataEnhancer import MetadataEnhancer


class VocabularyEnhancer(MetadataEnhancer):
    """ Used to enrich terms with Vocabulary concepts in DV metadata. """
    MATCHED_TERM_TYPE_NAME = 'matchedTerm'
    VOCABULARY_TYPE_NAME = 'vocabulary'
    URI_TYPE_NAME = "vocabVarUri1"
    LABEL_TYPE_NAME = "vocabVarLabel1"

    def __init__(self, metadata: dict, enrichment_table: dict,
                 terms_list: list, vocab_name: str):
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
        self.create_compound_field("term")

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
            if not term or term in self.added_terms_set:
                break
            label = term.upper()
            uri = self.query_enrichment_table(label)
            if uri:
                # add
                self.add_enhancements_to_metadata(term, uri, label)

    def add_enhancements_to_metadata(self, term: str, uri: str, label: str):
        term_field = {}
        self.add_enhancement_to_compound_metadata_field(
            term_field,
            self.MATCHED_TERM_TYPE_NAME,
            term)
        self.add_enhancement_to_compound_metadata_field(
            term_field,
            self.VOCABULARY_TYPE_NAME,
            self.vocab_name
        )
        self.add_enhancement_to_compound_metadata_field(
            term_field,
            self.URI_TYPE_NAME,
            uri)
        self.add_enhancement_to_compound_metadata_field(
            term_field,
            self.LABEL_TYPE_NAME,
            label)
        self.add_to_compound_field("term", term_field)
        self.added_terms_set.add(term)

    def add_to_compound_field(self, type_name, term_field):
        """ Adds a term to a given compound field.

        The compound field is retrieved using jmespath and the type name.
        Object that will contain all the term fields is added to the compound.

        :param type_name: The type name of the compound field.
        :param term_field: The object that will contain the term fields.
        """
        compound_field = jmespath.search(f"[?typeName=='{type_name}']",
                                         self.enrichment_block)
        compound_field[0]["value"].append(term_field)

    def create_compound_field(self, type_name):
        """ Creates the compound that will contain all info on an added term.

        :param type_name: the type_name of the compound field.
        """
        compound_field = {
            "typeName": type_name,
            "multiple": True,
            "typeClass": "compound",
            "value": []
        }

        self.enrichment_block.append(compound_field)
