from SPARQLWrapper import SPARQLWrapper, JSON


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


# Define your SPARQL query
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

endpoint = "https://fuseki.odissei.nl/skosmos/sparql"


def create_table_terms(sparql_endpoint, query):
    """
    TODO: Think about possibility of multiple uri's being returned.
    :param sparql_endpoint:
    :param query:
    :return:
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
    except:
        print('Query failed.')

results = create_table_terms(endpoint, ELSST_VOCAB_QUERY)
print(results)
