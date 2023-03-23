from utils import _try_for_key
from .MetadataEnhancer import MetadataEnhancer


class KeywordEnhancer(MetadataEnhancer):
    """ This class can be used to enhance the keywords in DV metadata.

    """
    def __init__(self, metadata: dict, endpoint: str, sparql_endpoint: str):
        """
        The ELSST Topics metadata block is created to add the matched terms to.
        """
        super().__init__(metadata, endpoint, sparql_endpoint)
        self.elsst_topics = self.create_elsst_topics()

    def enhance_metadata(self):
        """ enhance_metadata implementation for the keyword enhancements.

        First the keywords in the citation metadata block are retrieved.
        Then for all keywords we match a term using the grlc API.
        Finally, the terms are added to the ELSST Topic metadata block.
        """
        keywords = self.get_value_from_metadata('keyword', 'citation')

        for keyword_dict in keywords:
            keyword = _try_for_key(keyword_dict, ['keywordValue', 'value'],
                                   'keywordValue field value not found in'
                                   ' keyword metadata block')

            terms_dict = self.query_matched_terms(
                keyword,
            )

            terms = _try_for_key(
                terms_dict,
                ['results', 'bindings'],
                'grlc endpoint returned badly formatted JSON.'
            )
            topic = self.create_elsst_topic_keyword(keyword)
            self.add_terms_to_metadata(terms, topic)

    def add_terms_to_metadata(self, terms: list, topic: dict):
        """ Goes through all the retrieved terms and adds them to the metadata.

            For every term we add a URI and a label to the matched keyword in
            the ELSST Topics block.

            There is a limit of 3 terms that can be added for a single keyword.
            The metadata block contains fields for elsstVarUri1, elsstVarUri2,
            and elsstVarUri3. The same goes for the labels.


        :param terms: The terms matched to a specific keyword.
        :param topic: The topic field that keyword is in.
        """

        max_terms = min(len(terms), 3)
        for i in range(max_terms):
            counter = i+1
            self.add_term_uri(terms[i], counter, topic)
            self.add_term_label(terms[i], counter, topic)

    def add_term_uri(self, term: dict, counter: int, topic: dict):
        uri = _try_for_key(term, ['iri', 'value'],
                           'No uri found for ELSST term')
        uri_type_name = f'elsstVarUri{counter}'
        self.add_term_to_metadata_field(topic, uri_type_name, uri)

    def add_term_label(self, term: dict, counter: int, topic: dict):
        label = _try_for_key(term, ['lbl', 'value'],
                             'No label found for ELSST term')
        label_type_name = f'elsstVarLabel{counter}'
        self.add_term_to_metadata_field(topic, label_type_name, label)

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
            "keyword": {
                "typeName": 'keyword',
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
