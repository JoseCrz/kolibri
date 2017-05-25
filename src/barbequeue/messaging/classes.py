import enum
import json
from collections import namedtuple


class UnknownMessageError(Exception):
    pass


class MessageType(enum.Enum):
    # Job status messages
    JOB_FAILED = 0  # 0, so it can be falsey
    JOB_STARTED = 1
    JOB_UPDATED = 2
    JOB_COMPLETED = 3

    # Job command messages
    START_JOB = 101
    CANCEL_JOB = 102


class Message(namedtuple("_Message", ["type", "message"])):
    def serialize(self):
        # check that message type is in one of the message types we define
        assert self.type in (
            t.value for t in list(MessageType)
        ), "Message type not found in predetermined message type list!"

        return json.dumps({"type": self.type, "messsage": self.message})


class SuccessMessage(Message):
    def __new__(cls, job_id, result):
        msg = {'job_id': job_id, 'result': result}
        self = super(SuccessMessage, cls).__new__(cls, type=MessageType.JOB_COMPLETED, message=msg)
        return self


class ProgressMessage(Message):
    def __new__(cls, job_id, progress, total_progress, stage=""):
        """
        Creates a Message that updates the progress for the job given by job_id.
       
        :param job_id: The job_id of the job to update.
        :param progress: the current progress achieved by the running function so far. It should be less than or equal to the value of total_progress.
        :param total_progress: the total amount of progress achievable by the function. This can correspond directly to a concrete action done by the function (such as total number of videos to download, the number of items to process etc.)
        :param stage: an optional argument giving a short name for the current stage the job is on, e.g. 'downloading videos', 'loading subtitles', etc.
        :return: None
        
        :type job_id: str
        :type progress: float
        :type total_progress: float
        :type stage: str
        """
        msg = {'job_id': job_id, 'progress': progress, 'total_progress': total_progress, 'stage': stage}
        self = super(ProgressMessage, cls).__new__(cls, type=MessageType.JOB_UPDATED, message=msg)
        return self
