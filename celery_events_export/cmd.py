import logging
import sys

from celery.bin.base import Command
from celery_events_export import exporters

logger = logging.getLogger('celery_events_export.cmd')


class ExportCommand(Command):
    """
    Export celery worker events
    """

    def add_arguments(self, parser):
        # Monitor connection group
        group = parser.add_argument_group('Event monitor connection options')
        group.add_argument(
            '--event-type',
            help='Event type. Defaults to \'*\'',
            default='*',
        )
        group.add_argument(
            '--limit',
            help='Limit',
            default=None,
        )
        group.add_argument(
            '--timeout',
            help='Timeout',
            default=None,
        )
        group.add_argument(
            '--wakeup',
            help=(
                'Sends a signal to all workers'
                ' to force them to send a heartbeat'),
            default=True,
        )
        #

        parser.add_argument(
            '--type',
            help='Exporter type.',
            default=None,
        )
        for ExporterClass in exporters.ALL_EXPORTERS.values():
            ExporterClass.add_arguments(parser)

    def export_event(self, event):
        self._state.event(event)
        self._exporter.export_event(event, self._state)

    def run(self, **cli_options):
        self._cli_options = cli_options
        try:
            self._conf = self.app.conf.events_export
        except AttributeError:
            self._conf = {}
        self._state = self.app.events.State()
        exporter_conf = self._conf.get('exporter', {})
        try:
            exporter_type = self._cli_options['type'] or exporter_conf['type']
        except KeyError:
            sys.exit('Missing exporter\'s type configuration option.')
        self._exporter = exporters.from_type(exporter_type)(exporter_conf, cli_options)
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
