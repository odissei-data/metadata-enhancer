"""Canonical ELSST identifiers for enrichment."""

import re


_VERSIONED_URI = re.compile(
    r'^https://elsst\.cessda\.eu/id/[0-9]+/'
    r'([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-'
    r'[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$'
)


def versionless_elsst_uri(uri):
    """Remove only a numbered ELSST release segment; preserve other URIs."""
    match = _VERSIONED_URI.fullmatch(uri)
    return f'https://elsst.cessda.eu/id/{match[1]}' if match else uri


def normalize_existing_uris(metadata):
    """Normalize only ELSST enrichment values, leaving source metadata intact."""
    fields = metadata['datasetVersion']['metadataBlocks'].get('enrichments', {}).get('fields', [])
    for field in fields:
        if field.get('typeName') == 'enrichedElsstClassification':
            field['value'] = list(dict.fromkeys(versionless_elsst_uri(uri) for uri in field['value']))
