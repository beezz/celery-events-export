"""
celery_events_export.exporters
==============================
"""
import logging
import uuid
from datetime import datetime, timedelta


class Exporter(object):
    """Base class for different types of exporters.

    :class:`Exporter` subclass must implement ``_export_event(event, state)``
    method which do the actual exporting work.
    """

    def __init__(self, conf, cli_options):
        self.conf = conf
        self.cli_options = cli_options
        self.name = self.conf.get('name', str(uuid.uuid4()))
        self._bulk_size = self.conf.get('bulk_size', 1)
        self._apply_utcoffset = self.conf.get('apply_utcoffset', True)
        self._add_timestamp = self.conf.get('add_timestamp', 'ts')
        self.log = logging.getLogger(
            'celery_events_export.exporter.%s' % self.name)
        self.finalize_options()

    @classmethod
    def add_arguments(cls, parser):
        """Adds custom command line argument options."""

    def finalize_options(self):
        """Merges configuration with command line options."""

    def apply_utcoffset(self, event):
        """Applies ``utcoffset``to event's timestamp."""
        event[self._add_timestamp] += timedelta(hours=event['utcoffset'])

    def add_event_timestamp(self, event):
        """Adds event timestamp as a python's datetime object.

        Field name is set by ``add_timestamp`` option. If set to empty string,
        False or None, no additional timestamp field to the existing one in a
        form of unix timestamp will be added.

        In addition, if setting ``apply_utcoffset`` is set to True,
        ``event['utcoffset']`` will be applied.
        """
        event[self._add_timestamp] = datetime.fromtimestamp(event['timestamp'])
        if self._apply_utcoffset:
            self.apply_utcoffset(event)

    def add_task_name(self, event, state):
        """Adds task name to event data.

        As Celery documentation note, task name is sent only with -received
        event and state keeps track of this.
        """
        if event['uuid'] in state.tasks:
            event['task_name'] = state.tasks[event['uuid']].name

    def _export_event(self, event, state):
        raise NotImplementedError(
            'Exporter subclass must implement _export_event method')

    def export_event(self, event, state):
        event = event.copy()
        if 'uuid' in event:
            self.add_task_name(event, state)
        if self._add_timestamp:
            self.add_event_timestamp(event)
        self._export_event(event, state)


from celery_events_export.exporters.es import Elasticsearch  # noqa
from celery_events_export.exporters.prometheus import Prometheus  # noqa


# TODO: Use extensions and pkg_resources to make this dynamic
ALL_EXPORTERS = {
    'elasticsearch': Elasticsearch,
    'prometheus': Prometheus,
}


def from_type(type):
    return ALL_EXPORTERS[type]
