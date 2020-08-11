from test import print_foo

from redis import Redis
from rq import Queue
from autoworker import AutoWorkerQueue

q = AutoWorkerQueue(name="queue_test", connection=Redis())

for x in range(10):
    q.enqueue(print_foo)
