import os
import zipfile
from time import time

from unidecode import unidecode

from trojsten.regal.tasks.models  import Submit
from trojsten.submit.helpers import save_file, get_path, write_file
from trojsten.submit.constants import SUBMIT_STATUS_REVIEWED


def submit_review(filecontent, filename, task, user, points):    
    submit_id = str(int(time()))
    
    sfiletarget = os.path.join(
        get_path(task, user),
        "%s-%s-%s" % (user.last_name, submit_id, filename),
    )

    sfiletarget = unidecode(sfiletarget)

    if hasattr(filecontent, "chunks"):
        save_file(filecontent, sfiletarget)
    else:
        write_file(filecontent, "", sfiletarget)

    sub = Submit(task=task, user=user, points=points, submit_type=Submit.DESCRIPTION,
                 testing_status=SUBMIT_STATUS_REVIEWED, filepath=sfiletarget)
    sub.save()

def get_latest_submits_by_task(task):
    description_submits = task.submit_set.filter(
            submit_type=Submit.DESCRIPTION, time__lt=task.round.end_time
        ).exclude(testing_status=SUBMIT_STATUS_REVIEWED).select_related("user", "user__username")
    
    review_submits = task.submit_set.filter(
        submit_type=Submit.DESCRIPTION, testing_status=SUBMIT_STATUS_REVIEWED
        ).select_related("user", "user__username")

    users = {}
    for submit in description_submits:
        if not submit.user in users:
            users[submit.user] = {"description": submit}
        elif users[submit.user]["description"].time < submit.time:
            users[submit.user]["description"] = submit

    for submit in review_submits:
        if not submit.user in users:
            users[submit.user] = {"review": submit}
        elif not "review" in users[submit.user]:
            users[submit.user]["review"] = submit
        elif users[submit.user]["review"].time < submit.time:
            users[submit.user]["review"] = submit

    return users

def get_user_as_choices (task):
    return [(user.pk, "%s %s" % (user.first_name, user.last_name)) for user in get_latest_submits_by_task(task)]

def submit_download_filename(submit):
    return "%s_%s_%s" % (submit.user.last_name, submit.pk, submit.filename.split("-", 2)[-1])
