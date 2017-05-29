import logging
import pytest

from barbequeue.common.classes import Job
from barbequeue.messaging.classes import Message, MessageType
from barbequeue.worker.backends import inmem


@pytest.fixture
def mailbox():
    return "pytest"


@pytest.fixture
def worker(mailbox):
    logging.info("test_inmem.worker() working")
    b = inmem.Backend(incoming_message_mailbox=mailbox, outgoing_message_mailbox=mailbox)
    yield b
    b.shutdown()


@pytest.fixture
def startmsg(job):
    msg = Message(type=MessageType.START_JOB, message={"job": job})
    return msg


@pytest.fixture
def simplejob():
    logging.info("simplejob spawning a Job")
    job = Job(id, 'test', job_id='simplejob')
    return job


ID_SET = None


def testfunc(val=None):
    global ID_SET
    ID_SET = val


@pytest.fixture
def job():
    global ID_SET
    test_func_name = "{module}.{func}".format(module=__name__, func="testfunc")
    yield Job(test_func_name, job_id="test", val="passme")
    ID_SET = None  # reset the value set by testfunc


class TestWorker:
    def test_successful_job_adds_to_report_queue(self, worker, simplejob, mocker):
        mocker.spy(worker.reportqueue, 'put')

        logging.info("TestWorker starting simplejob...")
        worker.start_job(simplejob)
        logging.info("TestWorker joining jobqueue...")
        worker.jobqueue.join()

        assert worker.reportqueue.put.call_count == 1
        assert simplejob == worker.reportqueue.put.call_args[0][0].message.get('job')


class TestMonitor:
    def test_handle_messages_start_message_starts_a_job(self, worker, startmsg, job, mocker):
        mocker.spy(worker.monitor_thread, 'start_job')
        worker.monitor_thread.handle_incoming_message(startmsg)

        start_job = worker.monitor_thread.start_job
        assert start_job.call_count == 1
        assert startmsg.message['job'] in start_job.call_args[0]
