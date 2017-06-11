import os
import multiprocessing as mp

from redis import StrictRedis
from rq.contrib.legacy import cleanup_ghosts
from rq.queue import Queue
from osconf import config_from_environment


MAX_PROCS = mp.cpu_count() + 1
"""Number of maximum procs we can run
"""

class AutoWorkerQueue(Queue):

    def __init__(self, name='default', default_timeout=None, connection=None,
                 async=True, job_class=None, max_workers=None):
        super(AutoWorkerQueue, self).__init__(
            name=name, default_timeout=default_timeout, connection=connection,
            async=async, job_class=job_class
        )
        self.max_workers = max_workers
        self.workers = []

    def enqueue(self, f, *args, **kwargs):
        res = super(AutoWorkerQueue, self).enqueue(f, *args, **kwargs)
        self.clean_workers()
        if len(self.workers) <= self.max_workers:
            aw = AutoWorker(self.name, 1)
            self.workers.append(aw)
            aw.work()
        return res

    def clean_workers(self):
        for idx, aw in enumerate(self.workers[:]):
            if aw.worker.death_date:
                self.workers.pop(idx)

    def run_job(self, job):
        return super(AutoWorkerQueue, self).run_job(job)




class AutoWorker(object):
    """AutoWorker allows to spawn multiple RQ Workers using multiprocessing.
    :param queue: Queue to listen
    :param max_procs: Number of max_procs to spawn
    """
    def __init__(self, queue=None, max_procs=None):
        if queue is None:
            self.queue = 'default'
        else:
            self.queue = queue
        if max_procs is None:
            self.max_procs = MAX_PROCS
        elif 1 <= max_procs < MAX_PROCS + 1:
            self.max_procs = max_procs
        else:
            raise ValueError('Max procs {} not supported'.format(max_procs))
        self.processes = []
        self.config = config_from_environment(
            'AUTOWORKER',
            ['redis_url'],
            queue_class='rq.Queue',
            worker_class='rq.Worker',
            job_class='rq.Job',
        )

    def worker(self):
        """Internal target to use in multiprocessing
        """
        from rq.utils import import_attribute
        conn = StrictRedis.from_url(self.config['redis_url'])
        cleanup_ghosts(conn)
        worker_class = import_attribute(self.config['worker_class'])
        queue_class = import_attribute(self.config['queue_class'])
        q = [queue_class(self.queue, connection=conn)]
        worker = worker_class(q, connection=conn)
        worker._name = '{}-auto'.format(worker.name)
        worker.work(burst=True)

    def _create_worker(self):
        child_pid = os.fork()
        if child_pid == 0:
            self.worker()

    def work(self):
        """Spawn the multiple workers using multiprocessing and `self.worker`_
        targget
        """
        self.processes = [
            mp.Process(target=self._create_worker) for _ in range(0, self.max_procs)
        ]
        for proc in self.processes:
            proc.daemon = True
            proc.start()
