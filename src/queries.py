from SPARQLWrapper import SPARQLWrapper, JSON
import requests
from rdflib import Graph, Namespace

ELSST_VOCAB_QUERY = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT ?iri ?lbl
 WHERE {
  GRAPH <https://thesauri.cessda.eu/elsst/>
  {?iri skos:prefLabel ?lbl .
    FILTER langMatches( lang(?lbl), "NL" )
  }
}
"""

CBS_VOCAB_QUERY = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX skos:<http://www.w3.org/2004/02/skos/core#>
SELECT ?iri ?lbl ?prefLbl
WHERE {
  GRAPH <http://cbs.nl/variables/>
  {?iri <http://www.w3.org/2004/02/skos/core#altLabel> ?lbl .
   ?iri skos:prefLabel ?prefLbl .

    FILTER langMatches( lang(?lbl), "NL" ) 

  }
}
"""


def create_table_terms(sparql_endpoint, query):
    """ Creates a dict from a vocab with 'label: uri' as the key/value pair.

    TODO: Think about possibility of multiple uri's being returned.
    :param sparql_endpoint: The endpoint that can be queries with sparql.
    :param query: The query to fetch the data with.
    :return: table containing the uri's of the labels in the vocabulary.
    """
    # Set up the SPARQL query
    sparql = SPARQLWrapper(sparql_endpoint)
    sparql.setReturnFormat(JSON)
    sparql.setQuery(query)
    table = {}
    try:
        results = sparql.query().convert()
        for result in results["results"]["bindings"]:
            table[result["lbl"]["value"]] = result["iri"]["value"]
        return table
    except KeyError:
        print('Received object does not contain correct keys.')


def create_table_concepts_skosmos(skosmos_endpoint, vocabulary):
    concepts_table = {}

    api_endpoint = f"{skosmos_endpoint}/rest/v1/{vocabulary}/data?lang=nl"

    # Make the API request to get the RDF data in Turtle format
    response = requests.get(api_endpoint, params={'format': 'text/turtle'})

    if response.status_code == 200:
        rdf_data = response.text

        # Parse RDF data using rdflib
        graph = Graph()
        graph.parse(data=rdf_data, format='turtle')

        skos = Namespace("http://www.w3.org/2004/02/skos/core#")

        # Extract concepts and populate the dictionary
        for concept_uri, label in graph.subject_objects(skos.prefLabel):
            concepts_table[str(label).upper()] = str(concept_uri)

    elif response.status_code == 404:
        print(f"No vocabulary found with the requested id/uri: {vocabulary}")
    else:
        print(f"Error: {response.status_code} - {response.reason}")

    return concepts_table
