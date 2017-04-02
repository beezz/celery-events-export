from setuptools import setup

setup(
    name='celery-events-export',
    entry_points={
        'celery.commands': [
            'events_export = celery_events_export.cmd:ExportCommand',
        ]
    }
)