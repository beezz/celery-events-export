import time
import uuid
import logging
from datetime import datetime, timedelta
import elasticsearch
from elasticsearch import helpers as es_helpers


class Exporter:

    def __init__(self, conf):
        self.conf = conf
        self.name = self.conf.get('name', str(uuid.uuid4()))
        self._bulk_size = self.conf.get('bulk_size', 1)
        self._apply_utcoffset = self.conf.get('apply_utcoffset', True)
        self._add_timestamp = self.conf.get('add_timestamp', 'ts')
        self.log = logging.getLogger('celery_events_export.exporter.%s' % self.name)

    def apply_utcoffset(self, event):
        """Applies ``utcoffset``to event's timestamp."""
        event['ts'] += timedelta(hours=event['utcoffset'])

    def add_event_timestamp(self, event):
        """Adds event timestamp as a python's datetime object.

        Field name is set by ``add_timestamp`` option. If set to empty string,
        False or None, no additional timestamp field to the existing one in a
        form of unix timestamp will be added.

        In addition, if setting ``apply_utcoffset`` is set to True,
        ``event['utcoffset']`` will be applied.
        """
        event['ts'] = datetime.fromtimestamp(event['timestamp'])
        if self._apply_utcoffset:
            self.apply_utcoffset(event)

    def export_event(self, event, state):
        event = event.copy()
        if self._add_timestamp:
            self.add_event_timestamp(event)
        self._export_event(event, state)


class Elasticsearch(Exporter):

    def __init__(self, conf):
        super().__init__(conf)
        self._es = None
        self._buffer = []
        self._index_pattern = not (
            self.conf['index'] == datetime.now().strftime(self.conf['index']))

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
            conargs, conkwargs = self.conf['connection']
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
            events = [self.bulk_action_from_(event)]
        if events:
            es_helpers.bulk(self.es, events, chunk_size=self._bulk_size)


def from_type(type):
    return {'elasticsearch': Elasticsearch}[type]
