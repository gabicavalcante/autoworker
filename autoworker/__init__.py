# coding: utf-8
from __future__ import unicode_literals
import os
import multiprocessing as mp
from uuid import uuid4

from redis import Redis
from redis import connection
from rq.defaults import DEFAULT_RESULT_TTL

from rq.queue import Queue
from rq.worker import Worker, WorkerStatus
from rq.utils import import_attribute
from osconf import config_from_environment
from autoworker.work import worker, num_connected_workers

# Number of maximum procs we can run
MAX_PROCS = mp.cpu_count() + 1


class AutoWorkerQueue(Queue):
    def __init__(
        self,
        name="default",
        default_timeout=None,
        connection=None,
        is_async=True,
        job_class=None,
        max_workers=None,
    ):
        super(AutoWorkerQueue, self).__init__(
            name=name,
            default_timeout=default_timeout,
            connection=connection,
            is_async=is_async,
            job_class=job_class,
        )
        if max_workers is None:
            max_workers = MAX_PROCS
        self.max_workers = max_workers

    def enqueue(self, f, *args, **kwargs):
        res = super(AutoWorkerQueue, self).enqueue(f, *args, **kwargs)
        self.run_autowker()
        return res

    def enqueue_job(self, job, pipeline=None, at_front=False):
        res = super(AutoWorkerQueue, self).enqueue_job(job, pipeline, at_front)
        self.run_autowker()
        return res

    def run_autowker(self):
        if Worker.count(queue=self) <= self.max_workers: 
            aw = AutoWorker(self.name, max_procs=1)
            aw.work()

    def run_job(self, job):
        return super(AutoWorkerQueue, self).run_job(job)


class AutoWorker(object):
    """
    AutoWorker allows to spawn multiple RQ Workers using multiprocessing.
    :param queue: Queue to listen
    :param max_procs: Number of max_procs to spawn
    """

    def __init__(
        self,
        queue=None,
        max_procs=None,
        skip_failed=True,
        default_result_ttl=DEFAULT_RESULT_TTL
    ):
        self.queue = "default"
        if queue is not None:
            self.queue = queue

        if max_procs is None:
            self.max_procs = MAX_PROCS
        elif 1 <= max_procs < MAX_PROCS + 1:
            self.max_procs = max_procs
        else:
            raise ValueError("Max procs {} not supported".format(max_procs))

        self.processes = []
        self.config = config_from_environment(
            "AUTO_WORKER",
            ["redis_url"],
            queue_class="rq.Queue",
            worker_class="rq.Worker",
            job_class="rq.Job",
        )
        self.skip_failed = skip_failed
        self.default_result_ttl = default_result_ttl

    def work(self):
        """
        Spawn the multiple workers using multiprocessing and `self.worker`_
        targget
        """
        max_procs = 1 # self.max_procs - num_connected_workers()
        self.processes = [
            mp.Process(target=worker, args=(self.queue, self.config["redis_url"], self.skip_failed, self.default_result_ttl)).start() for _ in range(0, max_procs)
        ] 
