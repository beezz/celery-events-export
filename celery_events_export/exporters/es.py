from datetime import datetime
from celery_events_export.exporters import Exporter
import elasticsearch
from elasticsearch import helpers as es_helpers


class Elasticsearch(Exporter):

    def __init__(self, conf, cli_options):
        super(Elasticsearch, self).__init__(conf, cli_options)
        self._es = None
        self._buffer = []
        self._index_pattern = not (
            self.conf['index'] == datetime.now().strftime(self.conf['index']))

    @classmethod
    def add_arguments(cls, parser):
        group = parser.add_argument_group('Elasticsearch options')
        group.add_argument(
            '--es-url',
            help='Elasticsearch connection url')
        group.add_argument(
            '--es-index',
            help='Index pattern. (celery-event-%%Y-%%m-%%d)')

    def finalize_options(self):
        clio, conf = self.cli_options, self.conf
        self.conf['index'] = (
            clio['es_index'] or conf.get('index', 'celery-events-%Y-%m-%d'))

    def get_event_index(self, event):
        """Uses ``event``'s timestamp to format time-based index pattern.
        """
        if self._index_pattern:
            if self._add_timestamp:
                ts = event[self._add_timestamp]
            else:
                ts = datetime.fromtimestamp(event['timestamp'])
            return ts.strftime(self.conf['index'])
        else:
            return self.conf['index']

    def bulk_action_from_event(self, event):
        """Transforms an event into elasticsearch's bulk action.
        """
        return {
            '_index': self.get_event_index(event),
            '_type': event['type'],
            '_source': event,
        }

    @property
    def es(self):
        """Elasticsearch client."""
        if self._es is None:
            if self.cli_options.get('es_url'):
                conargs, conkwargs = [self.cli_options.get('es_url')], {}
            else:
                conargs, conkwargs = self.conf.get(
                    'connection', [['http://localhost:9200'], {}])
            self.log.info('Creating Elasticsearch client')
            self._es = elasticsearch.Elasticsearch(*conargs, **conkwargs)
        return self._es

    def _export_event(self, event, state):
        if self._bulk_size:
            self._buffer.append(self.bulk_action_from_event(event))
            if len(self._buffer) >= self._bulk_size:
                events = self._buffer[:]
                self._buffer = []
            else:
                events = None
        else:
            events = [self.bulk_action_from_event(event)]
        if events:
            es_helpers.bulk(self.es, events, chunk_size=self._bulk_size)
