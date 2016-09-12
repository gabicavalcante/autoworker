from autoworker import AutoWorker

from expects import *


with description('The autoworker class'):
    with context('if not max_procs is defined'):
        with it('must be the same as number of cpus + 1'):
            import multiprocessing as mp

            a = AutoWorker()
            expect(a.max_procs).to(equal(mp.cpu_count() + 1))

    with context('if max_procs is passed to __init__'):
        with it('must be the the same value'):
            a = AutoWorker(max_procs=3)
            expect(a.max_procs).to(equal(3))

        with it('must raise an error if is 0 < max_procs < number of cpus + 1'):
            def callback():
                a = AutoWorker(max_procs=10)

            expect(callback).to(raise_error(ValueError))

    with context('if no queue is defient'):
        with it('must be "default" queue'):
            a = AutoWorker()
            expect(a.queue).to(equal('default'))
    with context('if a queue is defined'):
        with it('have to be the same value'):
            a = AutoWorker('low')
            expect(a.queue).to(equal('low'))


with description('An instance of a AutoWorker'):
    with before.each:
        self.aw = AutoWorker()

    with it('must have a "work" method to spawn max_procs workers'):
        self.aw.work()
