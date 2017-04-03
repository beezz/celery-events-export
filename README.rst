
====================
Celery events export
====================

Monitor and export `Celery <http://www.celeryproject.org/>` worker events.


Installation
============


Usage
=====


.. code-block:: bash

   $ celery -A app events_export --type elasticsearch --es-url http://elastic:changeme@localhost:9200
