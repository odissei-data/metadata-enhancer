from enhancers.MetadataEnhancer import MetadataEnhancer
from utils import _try_for_key


class KeywordEnhancer(MetadataEnhancer):

    def __init__(self, metadata):
        super().__init__(metadata)

    def enhance_metadata(self):
        keywords = self.get_value_from_metadata('keyword', 'citation')
        elsst_topics = self.create_elsst_topics(self.metadata_blocks)

        for keyword in keywords:
            term = _try_for_key(keyword, ['keywordValue', 'value'],
                                'keywordValue field value not found in'
                                ' keyword metadata block')

            terms_dict = self.query_matched_terms(
                term,
                'matchElsstTermForKeyword',
                'https://fuseki.odissei.nl/skosmos/sparql'
            )

            terms = _try_for_key(
                terms_dict,
                ['results', 'bindings'],
                'grlc endpoint returned badly formatted JSON.'
            )
            topic = self.create_elsst_topic_keyword(elsst_topics, term)
            self.add_terms_to_metadata(terms, topic)


    def add_terms_to_metadata(self, terms, topic):
        counter = 0
        for term in terms:
            counter += 1
            self.add_keyword_elsst_label(topic, term, counter)
            self.add_keyword_elsst_uri(topic, term, counter)

    def add_keyword_elsst_uri(self, topic: dict, term: dict, counter: int):
        uri = _try_for_key(term, ['iri', 'value'],
                           'No uri found for ELSST term')
        varUri = 'elsstVarUri' + str(counter)

        topic[varUri] = {
            "typeName": varUri,
            "multiple": False,
            "typeClass": "primitive",
            "value": uri
        }
        print(f'keyword uri added: {topic}')

    def add_keyword_elsst_label(self, elsst_topic_dict: dict, term: dict,
                                counter: int):
        label = _try_for_key(term, ['lbl', 'value'],
                             'No label found for ELSST term')

        varLabel = 'elsstVarLabel' + str(counter)

        elsst_topic_dict[varLabel] = {
            "typeName": varLabel,
            "multiple": False,
            "typeClass": "primitive",
            "value": label
        }

        print(f'keyword label added: {elsst_topic_dict}')

    def create_elsst_topics(self, metadata_blocks: dict):
        metadata_blocks["elsstTopic"] = {
            "displayName": "ELSST Topics",
            "name": "elsstTopics",
            "fields": [
            ]
        }

        return metadata_blocks["elsstTopic"]["fields"]

    def create_elsst_topic_keyword(self, elsst_topics: list, term: str):

        topic = {
            "keyword": {
                "typeName": 'keyword',
                "multiple": False,
                "typeClass": "primitive",
                "value": term
            }
        }

        elsst_topics.append(
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
