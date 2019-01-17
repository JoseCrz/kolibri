from django.db import transaction
from le_utils.constants import content_kinds

from .models import HelpReason
from .models import LearnerProgressNotification
from .models import NotificationEventType
from .models import NotificationObjectType
from .utils import memoize
from kolibri.core.content.models import ContentNode
from kolibri.core.exams.models import ExamAssignment
from kolibri.core.lessons.models import Lesson
from kolibri.core.logger.models import AttemptLog
from kolibri.core.logger.models import ContentSummaryLog


def get_assignments(instance, summarylog, attempt=False):
    """
    Returns all Lessons assigned to the user having the content_id
    """
    memberships = instance.user.memberships.all()
    # If the user is not in any classroom nor group, nothing to notify
    if not memberships:
        return []

    content_id = summarylog.content_id
    channel_id = summarylog.channel_id
    learner_groups = [m.collection for m in memberships]

    # Return only active Lessons that are assigned to the requesting user's groups
    filtered_lessons = Lesson.objects.filter(
        lesson_assignments__collection__in=learner_groups,
        is_active=True,
        resources__regex=r"" + content_id + ""
    ).distinct()
    # get the contentnode_id for each lesson:
    lesson_contentnode = {
        lesson.id: r['contentnode_id']
        for lesson in filtered_lessons
        for r in lesson.resources
        if (r['content_id'] == content_id and r['channel_id'] == channel_id)
    }
    if attempt:
        # This part is for the NeedsHelp event. These Events can only be triggered on Exercises:
        to_delete = []
        for lesson_id, contentnode_id in lesson_contentnode.items():
            content_node = ContentNode.objects.get(pk=contentnode_id)
            if content_node.kind != content_kinds.EXERCISE:
                to_delete.append(lesson_id)
        for lesson_id in to_delete:
            del lesson_contentnode[lesson_id]
    # Returns all the affected lessons with the touched contentnode_id, Resource must be inside a lesson
    lesson_resources = [(lesson, lesson_contentnode[lesson.id]) for lesson in filtered_lessons if lesson.id in lesson_contentnode]
    return lesson_resources


def get_exam_group(memberships, exam_id):
    """
    Returns all classrooms or learner groups having this exam
    """
    learner_groups = [m.collection for m in memberships]
    filtered_exam_assignments = ExamAssignment.objects.filter(
        exam_id=exam_id,
        collection__in=learner_groups
    ).distinct()
    touched_groups = [assignment.collection_id for assignment in filtered_exam_assignments]
    return touched_groups


def save_notifications(notifications):
    with transaction.atomic():
        for notification in notifications:
            notification.save()


def create_notification(notification_object, notification_event, user_id, group_id, lesson_id=None,
                        contentnode_id=None,
                        quiz_id=None, reason=None):
    notification = LearnerProgressNotification()
    notification.user_id = user_id
    notification.classroom_id = group_id
    notification.notification_object = notification_object
    notification.notification_event = notification_event
    if contentnode_id:
        notification.contentnode_id = contentnode_id
    if lesson_id:
        notification.lesson_id = lesson_id
    if quiz_id:
        notification.quiz_id = quiz_id
    if reason:
        notification.reason = reason
    return notification


def parse_summary_log(summarylog):
    if summarylog.progress < 1.0:
        return
    lessons = get_assignments(summarylog, summarylog)
    notifications = []
    for lesson, contentnode_id in lessons:
        # Check if the notification has been previously saved:
        if LearnerProgressNotification.objects.filter(user_id=summarylog.user_id,
                                                      notification_object=NotificationObjectType.Resource,
                                                      notification_event=NotificationEventType.Completed,
                                                      lesson_id=lesson.id,
                                                      contentnode_id=contentnode_id).exists():
            continue
        # Let's create an ResourceIndividualCompletion
        notification = create_notification(NotificationObjectType.Resource,
                                           NotificationEventType.Completed,
                                           summarylog.user_id,
                                           lesson.collection_id,
                                           lesson_id=lesson.id,
                                           contentnode_id=contentnode_id)
        notifications.append(notification)
        lesson_content_ids = [resource['content_id'] for resource in lesson.resources]

        # Let's check if an LessonResourceIndividualCompletion needs to be created
        user_completed = ContentSummaryLog.objects.filter(user_id=summarylog.user_id,
                                                          content_id__in=lesson_content_ids,
                                                          progress=1.0).count()
        if user_completed == len(lesson_content_ids):
            if not LearnerProgressNotification.objects.filter(user_id=summarylog.user_id,
                                                              notification_object=NotificationObjectType.Lesson,
                                                              notification_event=NotificationEventType.Completed,
                                                              lesson_id=lesson.id,
                                                              classroom_id=lesson.collection_id).exists():
                lesson_notification = create_notification(NotificationObjectType.Lesson, NotificationEventType.Completed,
                                                          summarylog.user_id,
                                                          lesson.collection_id, lesson_id=lesson.id)
                notifications.append(lesson_notification)

    save_notifications(notifications)


@memoize
def exist_exam_notification(user_id, exam_id):
    return LearnerProgressNotification.objects.filter(user_id=user_id,
                                                      quizz_id=exam_id,
                                                      event_type=NotificationEventType.Started).exists()


def parse_exam_log(examlog):
    if not examlog.closed:
        # Checks to add an 'Started' event
        if exist_exam_notification(examlog.user_id, examlog.exam_id):
            return  # the event has already been triggered
        elif examlog.exam.progress.answer_count == 0:
            return  # the exam has not started yet
        event_type = NotificationEventType.Started
        exist_exam_notification.cache_clear()
    else:
        event_type = NotificationEventType.Completed

    user_classrooms = examlog.user.memberships.all()

    touched_groups = get_exam_group(user_classrooms, examlog.exam_id)
    notifications = []
    for group in touched_groups:
        notification = create_notification(NotificationObjectType.Quiz, event_type,
                                           examlog.user_id, group, quiz_id=examlog.exam_id)
        notifications.append(notification)

    save_notifications(notifications)


def parse_attempts_log(attemptlog):
    # This Event should not be triggered when a Learner is interacting with an Exercise outside of a Lesson:
    lessons = get_assignments(attemptlog, attemptlog.masterylog.summarylog, attempt=True)
    if not lessons:
        return
    # get all the atempts log on this exercise:
    failed_interactions = []
    attempts = AttemptLog.objects.filter(masterylog_id=attemptlog.masterylog_id)
    failed_interactions = [failed for attempt in attempts for failed in attempt.interaction_history if failed['correct'] == 0]
    # More than 3 errors in this mastery log:
    needs_help = len(failed_interactions) > 3

    if needs_help:
        notifications = []
        for lesson, contentnode_id in lessons:
            # This Event should be triggered only once
            # TODO: Decide if add a day interval filter, to trigger the event in different days
            if LearnerProgressNotification.objects.filter(user_id=attemptlog.user_id,
                                                          notification_object=NotificationObjectType.Resource,
                                                          notification_event=NotificationEventType.Help,
                                                          lesson_id=lesson.id,
                                                          classroom_id=lesson.collection_id,
                                                          contentnode_id=contentnode_id).exists():
                continue
            notification = create_notification(NotificationObjectType.Resource, NotificationEventType.Help,
                                               attemptlog.user_id, lesson.collection_id,
                                               lesson_id=lesson.id,
                                               contentnode_id=contentnode_id,
                                               reason=HelpReason.Multiple)
            notifications.append(notification)
        save_notifications(notifications)