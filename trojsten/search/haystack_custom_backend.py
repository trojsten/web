from django.conf import settings
from haystack.backends import elasticsearch_backend as es_backend


class AsciifoldingElasticBackend(es_backend.ElasticsearchSearchBackend):
    def __init__(self, *args, **kwargs):
        super(AsciifoldingElasticBackend, self).__init__(*args, **kwargs)
        # analyzer = ELASTICSEARCH_DEFAULT_ANALYZER
        self.DEFAULT_SETTINGS['settings']['analysis']['analyzer'] =\
            settings.ELASTICSEARCH_ANALYZER

    def build_schema(self, fields):
        content_field_name, mapping = super(AsciifoldingElasticBackend,
                                            self).build_schema(fields)

        for field_name, field_class in fields.items():
            field_mapping = mapping[field_class.index_fieldname]

            if field_mapping['type'] == 'string' and field_class.indexed:
                if not hasattr(field_class, 'facet_for') and \
                        field_class.field_type not in ('ngram', 'edge_ngram'):
                    field_mapping['analyzer'] = "ascii_analyser"

            mapping.update({field_class.index_fieldname: field_mapping})
        return (content_field_name, mapping)


class AsciifoldingElasticSearchEngine(es_backend.ElasticsearchSearchEngine):
    backend = AsciifoldingElasticBackend
