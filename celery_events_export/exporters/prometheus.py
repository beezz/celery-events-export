from celery_events_export.exporters import Exporter
from prometheus_client import start_http_server


class Prometheus(Exporter):
    def __init__(self, conf, cli_options):
        super(Prometheus, self).__init__(conf, cli_options)
        # with Prometheus irrelevant
        self._add_timestamp = None

        self.metrics = {
            # 'worker_alive': Gauge(
            #     'worker_alive',
            #     'Worker connection state',
            #     ['hostname'],
            # ),
            # 'worker_active': Gauge(
            #     'worker_active',
            #     'Worker processing state',
            #     ['hostname'],
            # ),
        }
        start_http_server(9190)

    def _export_event(self, event, state):
        # mx = self.metrics
        # for worker in state.alive_workers():
        #     pass
        #     # print(worker.loadavg)
        #     # (mx['worker_alive']
        #           .labels(worker.hostname)
        #           .set(1 if worker.alive else 0)
        pass
