import os
from collections import OrderedDict
from time import time

import czech_sort
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from unidecode import unidecode

from trojsten.submit import constants as submit_constants
from trojsten.submit.helpers import get_path, write_chunks_to_file
from trojsten.submit.models import Submit


def submit_review(filecontent, filename, task, user, points, comment="", submit=None):
    if filecontent is None and submit is None:
        raise ValidationError(_("You should upload a file or specify parent submit."))

    if filecontent is not None:
        submit_id = str(int(time()))

        sfiletarget = os.path.join(
            get_path(task, user), "%s-%s-%s" % (user.last_name, submit_id, filename)
        )

        sfiletarget = unidecode(sfiletarget)

        if hasattr(filecontent, "chunks"):
            write_chunks_to_file(sfiletarget, filecontent.chunks())
        else:
            write_chunks_to_file(sfiletarget, [filecontent])
    else:
        sfiletarget = submit.filepath

    sub = Submit(
        task=task,
        user=user,
        points=points,
        submit_type=submit_constants.SUBMIT_TYPE_DESCRIPTION,
        testing_status=submit_constants.SUBMIT_STATUS_REVIEWED,
        filepath=sfiletarget,
        reviewer_comment=comment,
    )
    sub.save()


def edit_review(filecontent, filename, submit, user, points, comment=""):
    if filecontent is not None:
        submit_id = str(int(time()))

        sfiletarget = unidecode(
            os.path.join(
                get_path(submit.task, user), "%s-%s-%s" % (user.last_name, submit_id, filename)
            )
        )

        if hasattr(filecontent, "chunks"):
            write_chunks_to_file(sfiletarget, filecontent.chunks())
        else:
            write_chunks_to_file(sfiletarget, [filecontent])

        submit.filepath = sfiletarget

    submit.user = user
    submit.points = points
    submit.reviewer_comment = comment
    submit.save()


def get_latest_submits_for_task(task):
    description_submits = (
        task.submit_set.filter(
            submit_type=submit_constants.SUBMIT_TYPE_DESCRIPTION, time__lte=task.round.end_time
        )
        .exclude(testing_status=submit_constants.SUBMIT_STATUS_REVIEWED)
        .select_related("user")
    )

    source_submits = (
        task.submit_set.filter(
            submit_type=submit_constants.SUBMIT_TYPE_SOURCE, time__lte=task.round.end_time
        )
        .exclude(testing_status=submit_constants.SUBMIT_STATUS_REVIEWED)
        .select_related("user")
    )

    review_submits = task.submit_set.filter(
        submit_type=submit_constants.SUBMIT_TYPE_DESCRIPTION,
        testing_status=submit_constants.SUBMIT_STATUS_REVIEWED,
    ).select_related("user")

    submits_by_user = {}
    for submit in description_submits:
        if submit.user not in submits_by_user:
            submits_by_user[submit.user] = {"description": submit}
        elif submits_by_user[submit.user]["description"].time < submit.time:
            submits_by_user[submit.user]["description"] = submit

    for submit in source_submits:
        if submit.user in submits_by_user:
            if "sources" not in submits_by_user[submit.user]:
                submits_by_user[submit.user]["sources"] = [submit]
            else:
                submits_by_user[submit.user]["sources"].append(submit)

    for submit in review_submits:
        if submit.user not in submits_by_user:
            submits_by_user[submit.user] = {"review": submit}
        elif "review" not in submits_by_user[submit.user]:
            submits_by_user[submit.user]["review"] = submit
        elif submits_by_user[submit.user]["review"].time < submit.time:
            submits_by_user[submit.user]["review"] = submit

    return OrderedDict(
        sorted(
            submits_by_user.items(),
            key=lambda x: (czech_sort.key(x[0].last_name), czech_sort.key(x[0].first_name)),
        )
    )


def get_user_as_choices(task):
    return [(user.pk, user.get_full_name()) for user in get_latest_submits_for_task(task)]


def submit_directory(submit, order=0):
    return "%03d_%s_%s/" % (
        order,
        unidecode(submit.user.get_full_name().lower().replace(" ", "_")),
        submit.pk,
    )


def submit_download_filename(submit, order=0):
    _, extension = os.path.splitext(os.path.basename(submit.filepath))
    name = unidecode(submit.user.get_full_name().lower().replace(" ", "_"))
    return "%03d_%s_%s/%s%s" % (order, name, submit.pk, name, extension)


def submit_source_download_filename(submit, description_submit_id, order=0):
    return "%03d_%s_%s/source/%s" % (
        order,
        unidecode(submit.user.get_full_name().lower().replace(" ", "_")),
        description_submit_id,
        submit.filename,
    )


def submit_protocol_download_filename(submit, description_submit_id, order=0):
    name, _ = os.path.splitext(os.path.basename(submit.filepath))
    protocol_path = "%s.%s" % (name, settings.PROTOCOL_FILE_EXTENSION)

    return "%03d_%s_%s/source/%s" % (
        order,
        unidecode(submit.user.get_full_name().lower().replace(" ", "_")),
        description_submit_id,
        protocol_path,
    )
