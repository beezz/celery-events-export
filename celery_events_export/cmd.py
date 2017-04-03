import sys
import logging
from celery.bin.base import Command
from celery_events_export import exporters


logger = logging.getLogger('celery_events_export.cmd')


class ExportCommand(Command):
    """
    Export celery worker events
    """

    def export_event(self, event):
        self._state.event(event)
        self._exporter.export_event(event, self._state)

    def run(self, *args, **kwargs):
        self._conf = self.app.conf.events_export
        self._state = self.app.events.State()
        try:
            exporter_conf = self._conf['exporter']
        except KeyError:
            system.exit('Missing exporter configuration.')
        try:
            exporter_type = exporter_conf['type']
        except KeyError:
            system.exit('Missing exporter\'s type configuration option.')
        self._exporter = exporters.from_type(exporter_type)(exporter_conf)
        logger.info(
            'Exporter `%s` of type `%s` created.',
            self._exporter.name,
            exporter_type)
        with self.app.connection() as connection:
            recv = self.app.events.Receiver(
                connection,
                handlers={self._conf.get('event_type', '*'): self.export_event},
            )
            recv.capture(
                limit=self._conf.get('limit', None),
                timeout=self._conf.get('timeout', None),
                wakeup=self._conf.get('wakeup', True),
            )
