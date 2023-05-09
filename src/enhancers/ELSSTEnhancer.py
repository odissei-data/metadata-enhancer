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
        self.elsst_topics = self.create_elsst_topics()

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
        for term_dict in matchable_terms:
            term = _try_for_key(term_dict, f'{field}.value')

            enhancements_dict = self.query_matched_terms(term)

            enhancements = _try_for_key(enhancements_dict, 'results.bindings')
            topic = self.create_elsst_topic(term)
            self.add_terms_to_metadata(enhancements, topic)

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
                            topic: dict):
        uri = _try_for_key(enhancement, 'iri.value')
        uri_type_name = f'elsstVarUri{counter}'
        self.add_enhancement_to_metadata_field(topic, uri_type_name, uri)

    def add_enhancement_label(self, enhancement: dict, counter: int,
                              topic: dict):
        label = _try_for_key(enhancement, 'lbl.value')
        label_type_name = f'elsstVarLabel{counter}'
        self.add_enhancement_to_metadata_field(topic, label_type_name, label)

    def create_elsst_topics(self) -> list:
        """ Creates the ELSST Topics custom metadata block """
        self.metadata_blocks["elsstTopic"] = {
            "displayName": "ELSST Topics",
            "name": "elsstTopics",
            "fields": [
            ]
        }
        return self.metadata_blocks["elsstTopic"]["fields"]

    def create_elsst_topic(self, term: str) -> dict:
        """ Creates a topic field dict for a given term.

        :param term: The term to add to the field.
        """
        topic = {
            "matchedTerm": {
                "typeName": 'matchedTerm',
                "multiple": False,
                "typeClass": "primitive",
                "value": term
            }
        }

        self.elsst_topics.append(
            {
                "typeName": "topic",
                "multiple": True,
                "typeClass": "compound",
                "value": [
                    topic
                ]
            }
        )

        return topic
