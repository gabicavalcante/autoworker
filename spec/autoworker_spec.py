import os
from autoworker import AutoWorker, AutoWorkerQueue
from rq.queue import Queue

from expects import *
from mamba import *

# Setup environment variable
os.environ['AUTO_WORKER_REDIS_URL'] = 'redis://localhost:6379/0'


with description('The autoworker class'):
    with context('if not max_procs is defined'):
        with it('must be the same as number of cpus + 1'):
            import multiprocessing as mp

            aw = AutoWorker()
            expect(aw.max_procs).to(equal(mp.cpu_count() + 1))

    with context('if max_procs is passed to __init__'):
        with it('must be the the same value'):
            aw = AutoWorker(max_procs=3)
            expect(aw.max_procs).to(equal(3))

        with it('must raise an error if is 0 < max_procs < number of cpus + 1'):
            def callback():
                import multiprocessing as mp
                aw = AutoWorker(max_procs=mp.cpu_count() + 2)

            expect(callback).to(raise_error(ValueError))

    with context('if no queue is defined'):
        with it('must be "default" queue'):
            aw = AutoWorker()
            q = Queue('default', connection=aw.connection)
            expect(aw.queue).to(equal(q))
    with context('if a queue is defined'):
        with it('have to be the same value'):
            aw = AutoWorker('low')
            q = Queue('low', connection=aw.connection)
            expect(aw.queue).to(equal(q))


with description('An instance of a AutoWorker'):
    with before.each:
        self.aw = AutoWorker()

    with it('must have a "work" method to spawn max_procs workers'):
        self.aw.work()
