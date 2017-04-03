# broker_url = 'amqp://guest:guest@localhost:5672//'

imports = (
    'event_generator.tasks'
)

# result_backend = 'rpc://'

# The prefix to use for event receiver queue names.
# event_queue_prefix =  'celeryev'

# Expiry time in seconds (int/float) for when after a monitor clients event
# queue will be deleted (x-expires).
# event_queue_expires = 60

# Message expiry time in seconds (int/float) for when messages sent to a
# monitor clients event queue is deleted (x-message-ttl)
# For example, if this value is set to 10 then a message delivered to this
# queue will be deleted after 10 seconds.
# event_queue_ttl =

# Message serialization format used when sending event messages.
# event_serializer = 'json'

events_export = {
    'event_type': '*',
    'limit': None,
    'timeout': None,
    'wakeup': True,
    'exporters': [
        {
            'name': 'elastic',
            'type': 'elasticsearch',
            'connection': (
                [['http://elastic:changeme@localhost:9200']],
                {},
            ),
            'index': 'celery-events-%Y-%m-%d',
            'add_timestamp': 'ts',
            'apply_utcoffset': True,
            'bulk_size': 10,
        },
    ]
}


import logging
logging.basicConfig(level=logging.INFO)
