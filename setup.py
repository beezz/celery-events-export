from setuptools import setup

install_requires = [
    'celery',
    'elasticsearch',
]


def get_version():
    with open('VERSION') as vf:
        return vf.read().strip()


setup(
    name='celery-events-export',
    version=get_version(),
    install_requires=install_requires,
    packages=['celery_events_export'],
    entry_points={
        'celery.commands': [
            'events_export = celery_events_export.cmd:ExportCommand',
        ]
    },
    author='Michal Kuffa',
    author_email='michal.kuffa@gmail.com',
)
