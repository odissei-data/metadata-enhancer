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
