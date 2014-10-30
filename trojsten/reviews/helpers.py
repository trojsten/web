from trojsten.regal.tasks.models  import Submit
from trojsten.submit.helpers import save_file, get_path, write_file

import os
import zipfile
import io

def submit_review (filecontent, filename, task, user, points):
    from time import time
    submit_id = str(int(time()))
    
    sfiletarget = os.path.join(
        get_path(task, user),
        "%s-%s-%s" % (user.last_name, submit_id, filename),
    )

    if hasattr(filecontent, "chunks"): 
        save_file(filecontent, sfiletarget)
    else:
        write_file (filename, "", sfiletarget)

    sub = Submit(task=task,
                 user=user,
                 submit_type=Submit.DESCRIPTION,
                 points=points,
                 testing_status=Submit.STATUS_REVIEWED,
                 filepath=sfiletarget)
    sub.save()

def get_latest_submits_by_task (task):
    des_submits = task.submit_set.filter(submit_type=Submit.DESCRIPTION, time__lt=task.round.end_time, testing_status="in queue").select_related('user', 'user__username')
    rev_submits = task.submit_set.filter(submit_type=Submit.DESCRIPTION, testing_status=Submit.STATUS_REVIEWED).select_related('user', 'user__username')

    users = {}
    for submit in des_submits:
        if not submit.user in users:
            users[submit.user] = {'description': submit}
        
        elif users[submit.user]['description'].time < submit.time:
            users[submit.user]['description'] = submit

    for submit in rev_submits:
        if not submit.user in users:
            users[submit.user] = {'review': submit}
        
        elif not 'review' in users[submit.user]:
            users[submit.user]['review'] = submit

        elif users[submit.user]['review'].time < submit.time:
            users[submit.user]['review'] = submit

    return users


def submit_readable_name (submit):
    return '%s_%s_%s' % (submit.user.last_name, submit.pk, submit.filename.split('-', 2)[-1])
