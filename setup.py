from setuptools import setup

install_requires = [
    'celery',
    'elasticsearch',
]

setup(
    name='celery-events-export',
    install_requires=install_requires,
    entry_points={
        'celery.commands': [
            'events_export = celery_events_export.cmd:ExportCommand',
        ]
    }
)
