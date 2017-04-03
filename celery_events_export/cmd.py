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
        for exporter in self._exporters:
            exporter.export_event(event, self._state)

    def run(self, *args, **kwargs):
        self._conf = self.app.conf.events_export
        self._state = self.app.events.State()
        self._exporters = [
            exporters.from_type(conf['type'])(conf)
            for conf in self._conf.get('exporters', [])
        ]
        logger.info(
                'Configured %d exporter(s). Types: %s',
            len(self._exporters),
            [_.conf['type'] for _ in self._exporters])
        if not self._exporters:
            sys.exit('Please configure at least one exporter.')
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
