from enhancers.MetadataEnhancer import MetadataEnhancer


class FrequencyEnhancer(MetadataEnhancer):
    def __init__(self, metadata: dict, enrichment_table: dict):
        super().__init__(metadata, enrichment_table)
        self.enrichment_block = self.create_metadata_block(
            "enrichments",
            "Enriched Metadata"
        )

    def enhance_metadata(self):
        alternative_title = self.get_value_from_metadata(
            metadata_field_name='alternativeTitle',
            metadata_block='citation'
        )
        frequency_of_use = self.query_enrichment_table(alternative_title)
        if frequency_of_use:
            self.add_enhancement_to_primitive_metadata_field('frequencyOfUse',
                                                             frequency_of_use)
