import enum
import logging
from collections import namedtuple
from functools import partial

from barbequeue.common.utils import import_stringified_func, stringify_func

logger = logging.getLogger(__name__)


class Job(object):
    """
    Job represents a function whose execution has been deferred through the Client's schedule function.

    Jobs are stored on the storage backend for persistence through restarts, and are scheduled for running
    to the workers.
    """
    class State(enum.Enum):
        """
        the Job.State object enumerates a Job's possible valid states.

        SCHEDULED means the Job has been accepted by the client, but has not been
        sent to the workers for running.

        QUEUED means the Job has been sent to the workers for running, but has not
        been run yet (to our knowledge).

        RUNNING means that one of the workers has started running the job, but is not
        complete yet. If the job has been set to track progress, then the job's progress
        and total_progress fields should be continuously updated.

        FAILED means that the job's function has raised an exception during runtime.
        The job's exception and traceback fields should be set.

        CANCELED means that the job has been canceled from running.

        COMPLETED means that the function has run to completion. The job's result field
        should be set with the function's return value.
        """

        SCHEDULED = 0
        QUEUED = 1
        RUNNING = 2
        FAILED = 3
        CANCELED = 4
        COMPLETED = 5

    def __init__(self, func, *args, **kwargs):
        """
        Create a new Job that will run func given the arguments passed to Job(). If the track_progress keyword parameter
        is given, the worker will pass an update_progress function to update interested parties about the function's
        progress. See Client.__doc__ for update_progress's function parameters.

        :param func: func can be a callable object, in which case it is turned into an importable string,
        or it can be an importable string already.
        """
        self.job_id = kwargs.pop('job_id', None)
        self.state = kwargs.pop('state', self.State.SCHEDULED)
        self.traceback = ""
        self.exception = None
        self.track_progress = kwargs.pop('track_progress', False)
        self.progress = 0
        self.total_progress = 0
        self.args = args
        self.kwargs = kwargs

        if callable(func):
            funcstring = stringify_func(func)
        elif isinstance(func, str):
            funcstring = func
        else:
            raise Exception(
                "Error in creating job. We do not know how to "
                "handle a function of type {}".format(type(func)))

        self.func = funcstring

    def get_lambda_to_execute(self):
        """
        return a function that executes the function assigned to this job.
        
        If job.track_progress is None (the default), the returned function accepts no argument
        and simply needs to be called. If job.track_progress is True, an update_progress function
        is passed in that can be used by the function to provide feedback progress back to the
        job scheduling system.
        
        :return: a function that executes the original function assigned to this job.
        """
        func = import_stringified_func(self.func)

        if self.track_progress:
            y = lambda p: func(update_progress=partial(p, self.job_id), *self.args, **self.kwargs)
        else:
            y = lambda: func(*self.args, **self.kwargs)

        return y

    @property
    def percentage_progress(self):
        """
        Returns a float between 0 and 1, representing the current job's progress in its task.
        
        :return: float corresponding to the total percentage progress of the job.
        """
        return float(self.progress) / self.total_progress

    def __repr__(self):
        return "<Job id: {id} state: {state} progress: {p}/{total} func: {func}>".format(
            id=self.job_id,
            state=self.state.name,
            func=self.func,
            p=self.progress,
            total=self.total_progress
        )
