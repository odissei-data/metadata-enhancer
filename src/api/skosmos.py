import requests
from rdflib import Graph, URIRef
from rdflib.namespace import DCTERMS, RDF, SKOS

from elsst import versionless_elsst_uri


def create_table_concepts_skosmos(skosmos_endpoint, vocabulary, language,
                                  *, versionless=False) -> dict:
    """Load preferred labels, optionally resolving dct:isVersionOf URIs."""
    language = getattr(language, 'value', language).lower()
    api_endpoint = f"{skosmos_endpoint.rstrip('/')}/rest/v1/{vocabulary}/data"
    params = {'format': 'text/turtle'}
    if language != 'all':
        params['lang'] = language
    response = requests.get(api_endpoint,
                            params=params,
                            timeout=60)
    response.raise_for_status()
    graph = Graph().parse(data=response.text, format='turtle')
    return create_table_from_graph(graph, language, versionless=versionless)


def create_table_from_graph(graph, language, *, versionless=False) -> dict:
    """Build one language's lookup table from RDF, including full exports."""
    language = getattr(language, 'value', language).lower()
    if not versionless:
        # Preserve the generic loader's handling of untyped and untagged RDF.
        # For this path, language selection remains the endpoint's job.
        return {str(label).upper(): str(concept)
                for concept, label in graph.subject_objects(SKOS.prefLabel)}
    table = {}
    for concept in sorted(set(graph.subjects(RDF.type, SKOS.Concept))):
        labels = [label for label in graph.objects(concept, SKOS.prefLabel)
                  if getattr(label, 'language', None)
                  and (language == 'all' or label.language.lower() == language)]
        if not labels:
            continue
        targets = list(graph.objects(concept, DCTERMS.isVersionOf))
        if len(targets) == 1 and isinstance(targets[0], URIRef):
            uri = targets[0]
        elif not targets and versionless_elsst_uri(str(concept)) != str(concept):
            # ELSST 6 includes 35 new concepts without dct:isVersionOf.
            # Their published identifiers still follow /id/<release>/<UUID>.
            uri = versionless_elsst_uri(str(concept))
        else:
            raise ValueError(f"Expected one dct:isVersionOf URI for {concept}")
        for label in labels:
            key = str(label).upper()
            if language == 'all' and key in table and table[key] != str(uri):
                # Do not guess when translations refer to different concepts.
                table[key] = None
            else:
                table[key] = str(uri)
    if language == 'all':
        table = {label: uri for label, uri in table.items() if uri is not None}
    if versionless and not table:
        raise ValueError(f"No concepts found for language {language}")
    return table
