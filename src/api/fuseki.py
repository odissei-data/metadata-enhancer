from SPARQLWrapper import SPARQLWrapper, JSON


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
            table[result["lbl"]["value"].upper()] = result["iri"]["value"]
        return table
    except KeyError:
        print('Received object does not contain correct keys.')
