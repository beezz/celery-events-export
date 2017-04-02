import logging
from celery.bin.base import Command
from celery_events_export import exporters


class ExportCommand(Command):
    """
    Export celery worker events
    """

    def export_event(self, event):
        self._state.event(event)
        for exporter in self._exporters:
            exporter.export_event(event, self._state)

    def run(self, *args, **kwargs):
        logging.basicConfig(level=logging.INFO)
        self._state = self.app.events.State()
        self._exporters = [
            exporters.from_type(conf['type'])(conf)
            for conf in self.app.conf.events_export
        ]
        with self.app.connection() as connection:
            recv = self.app.events.Receiver(connection, handlers={
                '*': self.export_event
            })
            recv.capture(limit=None, timeout=None, wakeup=True)
