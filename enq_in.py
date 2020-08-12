from spec.test import print_foo

from redis import Redis
from autoworker import AutoWorkerQueue
from datetime import timedelta

import os
os.environ['AUTO_WORKER_REDIS_URL'] = 'redis://localhost:6379/0'

job_queue = AutoWorkerQueue(name="queue_test", connection=Redis())


for x in range(10):
    job = job_queue.enqueue_in(
        timedelta(seconds=5),
        print_foo
    )
