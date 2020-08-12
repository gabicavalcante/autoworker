from uuid import uuid4

from rq.contrib.legacy import cleanup_ghosts
from rq.utils import import_attribute
from redis import Redis
from rq.worker import Worker, WorkerStatus


def auto_worker(queue_name, redis_url, skip_failed, default_result_ttl):
    """
    Internal target to use in multiprocessing
    """
    connection = Redis.from_url(redis_url)

    cleanup_ghosts(connection)
    worker_class = import_attribute("rq.Worker")

    queue_class = import_attribute("rq.Queue")
    queue = queue_class(queue_name, connection=connection)

    if skip_failed:
        exception_handlers = []
    else:
        exception_handlers = None

    name = "{}-auto".format(uuid4().hex)
    worker = worker_class(
        queue,
        name=name,
        connection=connection,
        exception_handlers=exception_handlers,
        default_result_ttl=default_result_ttl,
    )
    worker.work(burst=True)
