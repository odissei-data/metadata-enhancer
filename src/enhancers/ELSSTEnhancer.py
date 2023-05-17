from .utils import _try_for_key
from .MetadataEnhancer import MetadataEnhancer

MAX_ENHANCEMENTS = 3


class ELSSTEnhancer(MetadataEnhancer):
    """ This class can be used to enhance terms with ELSST in DV metadata. """

    def __init__(self, metadata: dict, endpoint: str, sparql_endpoint: str):
        """
        The ELSST Topics metadata block is created to add the enhancements to.
        """
        super().__init__(metadata, endpoint, sparql_endpoint)
        self.enrichment_block = self.create_enrichment_block()

    def enhance_metadata(self):
        """ enhance_metadata implementation for the term enhancements. """

        self.ELSST_enhance_metadata('citation', 'keyword', 'keywordValue')
        self.ELSST_enhance_metadata('citation', 'topicClassification',
                                    'topicClassValue')

    def ELSST_enhance_metadata(self, metadata_block, compound_field, field):
        """ Handles the metadata enhancement of terms using ELSST matches.

        First a list of terms in the give compound in the given metadata block
        is retrieved. Then for all terms we match a term using the grlc API.
        Finally, the terms are added to the ELSST Topic metadata block.

        :param metadata_block: Contains compound field with matchable terms.
        :param compound_field: Contains the field that holds matchable terms.
        :param field: The field containing the matchable terms.
        """
        matchable_terms = self.get_value_from_metadata(compound_field,
                                                       metadata_block)
        print(matchable_terms)
        for term_dict in matchable_terms:
            term = _try_for_key(term_dict, f'{field}.value')

            enhancements_dict = self.query_enhancements(term)

            enhancements = _try_for_key(enhancements_dict, 'results.bindings')
            elsst_term = self.create_elsst_term(term)
            if enhancements:
                self.add_enhancements_to_metadata(enhancements, elsst_term)
                self.add_matched_term(elsst_term)

    def add_enhancements_to_metadata(self, enhancements: list, topic: dict):
        """ Goes through retrieved enhancements and adds them to the metadata.

        For every enhancement we add a URI and a label to the matched term
        in the ELSST Topics block.

        There is a limit of 3 enhancements added for a single term.
        The metadata block contains fields for elsstVarUri1, elsstVarUri2,
        and elsstVarUri3. The same goes for the labels.

        :param enhancements: The enhancements for a specific term.
        :param topic: The topic field that term is in.
        """

        max_enhancements = min(len(enhancements), MAX_ENHANCEMENTS)
        for i in range(max_enhancements):
            counter = i + 1
            self.add_enhancement_uri(enhancements[i], counter, topic)
            self.add_enhancement_label(enhancements[i], counter, topic)

    def add_enhancement_uri(self, enhancement: dict, counter: int,
                            term: dict):
        uri = _try_for_key(enhancement, 'iri.value')
        uri_type_name = f'elsstVarUri{counter}'
        self.add_enhancement_to_metadata_field(term, uri_type_name, uri)

    def add_enhancement_label(self, enhancement: dict, counter: int,
                              term: dict):
        label = _try_for_key(enhancement, 'lbl.value')
        label_type_name = f'elsstVarLabel{counter}'
        self.add_enhancement_to_metadata_field(term, label_type_name, label)

    def create_enrichment_block(self) -> list:
        """ Creates the enrichment custom metadata block """
        self.metadata_blocks["enrichments"] = {
            "displayName": "Enriched Metadata",
            "name": "enrichments",
            "fields": [
            ]
        }
        return self.metadata_blocks["enrichments"]["fields"]

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
        """

        :param elsst_term:
        :return:
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
