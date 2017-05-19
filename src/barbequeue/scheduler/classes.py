from queue import Full, Empty
from threading import Event

from barbequeue.common.classes import BaseCloseableThread
from barbequeue.messaging.classes import MessageType


class Scheduler(object):
    INCOMING_MESSAGES_MAILBOX = "scheduler-incoming"

    def __init__(self, storage_backend, messaging_backend, worker_backend, incoming_mailbox, worker_mailbox):
        # TODO: Extend the scheduler module to use the messaging backend,
        # not talk to the worker backend directly
        self.incoming_mailbox = incoming_mailbox
        self.worker_mailbox = worker_mailbox
        self.worker_backend = worker_backend

        # HACK, don't talk to the worker queue directly. Won't work if we're using process-based workers.
        self.worker_queue = worker_backend.jobqueue

        self.storage_backend = storage_backend
        self.scheduler_shutdown_event = Event()

        self.messaging_backend = messaging_backend

        self.start_scheduler_thread()

    def start_scheduler_thread(self):
        self.scheduler_thread = SchedulerThread(worker_queue=self.worker_queue,
                                                messaging_backend=self.messaging_backend,
                                                storage_backend=self.storage_backend,
                                                incoming_message_mailbox=self.INCOMING_MESSAGES_MAILBOX,
                                                shutdown_event=self.scheduler_shutdown_event, thread_name="SCHEDULER")
        self.scheduler_thread.setDaemon(True)
        self.scheduler_thread.start()

    def shutdown(self):
        self.scheduler_shutdown_event.set()


class SchedulerThread(BaseCloseableThread):
    def __init__(self, storage_backend, messaging_backend, incoming_message_mailbox, worker_queue, *args, **kwargs):
        self.worker_queue = worker_queue
        self.storage_backend = storage_backend
        self.messaging_backend = messaging_backend
        self.incoming_message_mailbox = incoming_message_mailbox
        super(SchedulerThread, self).__init__(*args, **kwargs)

    def main_loop(self, timeout):
        self.schedule_next_job(timeout)
        self.handle_worker_messages(timeout)

    def handle_worker_messages(self, timeout):
        try:
            msg = self.messaging_backend.pop(self.incoming_message_mailbox, timeout=timeout)
        except Empty:
            self.logger.debug("No new messages from workers.")
            return

        if msg.type == MessageType.JOB_UPDATED:
            pass
        elif msg.type == MessageType.JOB_COMPLETED:
            pass
        elif msg.type == MessageType.JOB_FAILED:
            pass
        else:
            self.logger.error("Unknown message type: {}".format(msg.type))

    def schedule_next_job(self, timeout):
        next_job = self.storage_backend.get_next_scheduled_job()

        if not next_job:
            self.logger.debug("No job to schedule right now.")
            return

        try:
            self.worker_queue.put(next_job, timeout=timeout)
        except Full:
            self.logger.debug("Worker queue full; skipping scheduling of job {} for now.".format(next_job.job_id))
            return
