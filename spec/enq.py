from autoworker.test import print_foo

from redis import Redis
from rq import Queue

q = Queue(connection=Redis())

for x in range(10000):
    q.enqueue(print_foo)
