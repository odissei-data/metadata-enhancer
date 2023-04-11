from .utils import _try_for_key
from .MetadataEnhancer import MetadataEnhancer

MAX_ENHANCEMENTS = 3


class KeywordEnhancer(MetadataEnhancer):
    """ This class can be used to enhance the keywords in DV metadata. """

    def __init__(self, metadata: dict, endpoint: str, sparql_endpoint: str):
        """
        The ELSST Topics metadata block is created to add the enhancements to.
        """
        super().__init__(metadata, endpoint, sparql_endpoint)
        self.elsst_topics = self.create_elsst_topics()

    def enhance_metadata(self):
        """ enhance_metadata implementation for the keyword enhancements.

        First the keywords in the citation metadata block are retrieved.
        Then for all keywords fetch enhancements using the grlc API.
        Finally, the enhancements are added to the ELSST Topic metadata block.
        """
        keywords = self.get_value_from_metadata('keyword', 'citation')

        for keyword_dict in keywords:
            keyword = _try_for_key(keyword_dict, 'keywordValue.value')

            enhancements_dict = self.query_enhancements(
                keyword,
            )

            enhancements = _try_for_key(enhancements_dict, 'results.bindings')
            topic = self.create_elsst_topic_keyword(keyword)
            self.add_enhancements_to_metadata(enhancements, topic)

    def add_enhancements_to_metadata(self, enhancements: list, topic: dict):
        """ Goes through retrieved enhancements and adds them to the metadata.

        For every enhancement we add a URI and a label to the matched keyword
        in the ELSST Topics block.

        There is a limit of 3 enhancements added for a single keyword.
        The metadata block contains fields for elsstVarUri1, elsstVarUri2,
        and elsstVarUri3. The same goes for the labels.

        :param enhancements: The enhancements for a specific keyword.
        :param topic: The topic field that keyword is in.
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

    def create_elsst_topic_keyword(self, keyword: str) -> dict:
        """ Creates a topic field dict for a given keyword.

        :param keyword: The keyword to add to the field.
        """
        topic = {
            "matchedKeyword": {
                "typeName": 'matchedKeyword',
                "multiple": False,
                "typeClass": "primitive",
                "value": keyword
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
