
from celery.bin.base import Command


class ExportCommand(Command):
    """
    Export celery worker events
    """

    def run(self, **kwargs):
        print('Export command is running ...')
        print(kwargs)
