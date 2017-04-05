import time
from datetime import datetime

import pytest

from celery_events_export import exporters


class Obj:
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)


class TestExporter:

    def test_finalize_options_called(self, mocker):
        mocker.patch.object(exporters.Exporter, 'finalize_options')
        exporters.Exporter({}, {})
        exporters.Exporter.finalize_options.assert_called_once_with()

    def test_apply_utcoffset(self):
        ex = exporters.Exporter({'add_timestamp': 'ceets'}, {})

        with pytest.raises(KeyError):
            ex.apply_utcoffset({})

        event = {'utcoffset': -2, 'timestamp': time.time()}
        ex.add_event_timestamp(event)
        assert ex._add_timestamp in event
        assert isinstance(event[ex._add_timestamp], datetime)

    def test_add_task_name(self):
        ex = exporters.Exporter({}, {})
        state = Obj()
        uuid = 'random-task-uuid'
        state.tasks = {uuid: Obj(name='task_name')}
        event = {'uuid': uuid}
        ex.add_task_name(event, state)
        assert event['task_name'] == 'task_name'
