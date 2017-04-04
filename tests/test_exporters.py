import pytest
import time
from datetime import datetime
from celery_events_export import exporters


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
