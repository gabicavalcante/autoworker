from test import print_foo

from redis import Redis
from autoworker import AutoWorkerQueue

q = AutoWorkerQueue(name="queue_test", connection=Redis())
q2 = AutoWorkerQueue(name="queue2_test", connection=Redis())


for x in range(10):
    q.enqueue(print_foo)
    q2.enqueue(print_foo)
