import os
from time import time

from unidecode import unidecode

from trojsten.regal.tasks.models import Submit
from trojsten.submit.helpers import get_path, write_chunks_to_file
from trojsten.submit.constants import SUBMIT_STATUS_REVIEWED


def submit_review(filecontent, filename, task, user, points, comment=''):
    submit_id = str(int(time()))

    sfiletarget = os.path.join(
        get_path(task, user),
        '%s-%s-%s' % (user.last_name, submit_id, filename),
    )

    sfiletarget = unidecode(sfiletarget)

    if hasattr(filecontent, 'chunks'):
        write_chunks_to_file(sfiletarget, filecontent.chunks())
    else:
        write_chunks_to_file(sfiletarget, [filecontent])

    sub = Submit(task=task, user=user, points=points, submit_type=Submit.DESCRIPTION,
                 testing_status=SUBMIT_STATUS_REVIEWED, filepath=sfiletarget, reviewer_comment=comment)
    sub.save()


def get_latest_submits_for_task(task):
    description_submits = task.submit_set.filter(
        submit_type=Submit.DESCRIPTION, time__lt=task.round.end_time
    ).exclude(testing_status=SUBMIT_STATUS_REVIEWED).select_related('user')

    source_submits = task.submit_set.filter(
        submit_type=Submit.SOURCE, time__lt=task.round.end_time
    ).exclude(testing_status=SUBMIT_STATUS_REVIEWED).select_related('user')

    review_submits = task.submit_set.filter(
        submit_type=Submit.DESCRIPTION, testing_status=SUBMIT_STATUS_REVIEWED
    ).select_related('user')

    submits_by_user = {}
    for submit in description_submits:
        if submit.user not in submits_by_user:
            submits_by_user[submit.user] = {'description': submit}
        elif submits_by_user[submit.user]['description'].time < submit.time:
            submits_by_user[submit.user]['description'] = submit

    for submit in source_submits:
        if submit.user in submits_by_user:
            if 'sources' not in submits_by_user[submit.user]:
                submits_by_user[submit.user]['sources'] = [submit]
            else:
                submits_by_user[submit.user]['sources'].append(submit)

    for submit in review_submits:
        if submit.user not in submits_by_user:
            submits_by_user[submit.user] = {'review': submit}
        elif 'review' not in submits_by_user[submit.user]:
            submits_by_user[submit.user]['review'] = submit
        elif submits_by_user[submit.user]['review'].time < submit.time:
            submits_by_user[submit.user]['review'] = submit

    return submits_by_user


def get_user_as_choices(task):
    return [
        (user.pk, user.get_full_name())
        for user in get_latest_submits_for_task(task)
    ]


def submit_directory(submit):
    return '%s_%s/' % (submit.user.last_name, submit.pk)

def submit_download_filename(submit):
    return '%s_%s/%s' % (submit.user.last_name, submit.pk, submit.filename.split('-', 2)[-1])

def submit_source_download_filename(submit, description_submit_id):
    return '%s_%s/source/%s' % (submit.user.last_name, description_submit_id, submit.filename)

def submit_protocol_download_filename(submit, description_submit_id):
    return '%s_%s/source/%s' % (submit.user.last_name, description_submit_id, os.path.basename(submit.protocol_path))
