import requests
from rdflib import Graph, Namespace


def create_table_concepts_skosmos(skosmos_endpoint, vocabulary, language):
    concepts_table = {}

    api_endpoint = f"{skosmos_endpoint}/rest/v1/{vocabulary}" \
                   f"/data?lang={language}"

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
