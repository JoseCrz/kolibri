from concurrent.futures import ThreadPoolExecutor
from functools import partial

from barbequeue.worker.backends.base import BaseBackend


class Backend(BaseBackend):
    def __init__(self, *args, **kwargs):
        # Internally, we use conncurrent.future.Future to run and track
        # job executions. We need to keep track of which future maps to which
        # job they were made from, and we use the job_future_mapping dict to do
        # so.
        self.job_future_mapping = {}
        super(Backend, self).__init__(*args, **kwargs)

    def schedule_job(self, job):
        """
        schedule a job to the type of workers spawned by self.start_workers.
        
        
        :param job: the job to schedule for running.
        :return: 
        """
        l = job.get_lambda_to_execute()

        if job.track_progress:
            future = self.workers.submit(l, self.update_progress)
        else:
            future = self.workers.submit(l)

        # assign the futures to a dict, mapping them to a job
        self.job_future_mapping[future] = job
        # callback for when the future is now!
        future.add_done_callback(self.handle_finished_future)

        return future

    def shutdown(self, wait=True):
        self.workers.shutdown(wait=wait)

    def start_workers(self, num_workers):
        return ThreadPoolExecutor(max_workers=num_workers)

    def handle_finished_future(self, future):
        # get back the job assigned to the future
        job = self.job_future_mapping[future]

        try:
            result = future.result()
        except Exception as e:
            # TODO: concurrent.futures doesn't provide the stacktrace.
            # find a way to catch the stacktrace.
            self.report_error(job, e, "")
            return

        self.report_success(job, result)


class Reporter(object):
    def __init__(self, reportqueue):
        pass
