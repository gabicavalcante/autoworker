AutoWorker
==========

[![Build Status](https://travis-ci.org/gabicavalcante/autoworker.svg?branch=master)](https://travis-ci.org/gabicavalcante/autoworker)

Spawn RQ Workers automatically. This project work based on the original autoworker. 

```python
from redis import Redis
from rq import Queue
from autoworker import AutoWorkerQueue

q = AutoWorkerQueue(name="queue_test", connection=Redis())

for x in range(10):
    q.enqueue(print_foo)
```

**Note**: From **v0.4.0** failed jobs doesn't go to the failed queue. If you want to enqueue to failed queue you should call `AutoWorker` as following

.. code-block:: python

    aw = AutoWorker(queue='high', max_procs=6, skip_failed=False)
