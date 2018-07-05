# -*- coding: utf-8 -*-
from time import time

import os
import random
from django.conf import settings
from django.utils.encoding import smart_bytes
from os import path
from unidecode import unidecode

from . import constants

judge_client = settings.JUDGE_CLIENT


def write_chunks_to_file(filepath, chunks):
    try:
        os.makedirs(os.path.dirname(filepath))
    except:  # noqa: E722 @FIXME
        pass
    with open(filepath, 'wb+') as destination:
        for chunk in chunks:
            destination.write(smart_bytes(chunk))


def get_lang_from_filename(filename):
    ext = os.path.splitext(filename)[1].lower()
    extmapping = {
        ".cpp": ".cc",
        ".cc": ".cc",
        ".pp": ".pas",
        ".pas": ".pas",
        ".dpr": ".pas",
        ".c": ".c",
        ".py": ".py",
        ".py3": ".py",
        ".hs": ".hs",
        ".cs": ".cs",
        ".java": ".java",
        ".zip": ".zip"}

    if ext not in extmapping:
        return False
    return extmapping[ext]


def get_path(task, user):
    """Returns path of the submission directory.

    Path is in form of: $SUBMIT_PATH/submits/user-id/task_id/
    """
    return os.path.join(settings.SUBMIT_PATH,
                        'submits',
                        "%s-%d" % (task.round.semester.competition.name, user.id),
                        "%s-%d" % (task.round.semester.competition.name, task.id))


def get_description_file_path(file, user, task):
    """Returns path for given description file.

    The path is of the form: $SUBMIT_PATH/submits/KSP/task_id/user_id/surname-id-originalfilename.
    Description submit id's are currently timestamps.
    """
    submit_id = str(int(time()))
    orig_filename, extension = os.path.splitext(path.basename(file.name))
    target_filename = ('%s-%s-%s' %
                       (user.last_name, submit_id, orig_filename)
                       )[:(255 - len(extension))] + extension
    return unidecode(os.path.join(
        get_path(task, user),
        target_filename,
    ))


def _generate_submit_id():
    """Generates a submit id in form of <timestamp>-##### where ##### are 5 random digits."""
    timestamp = int(time())
    return '%d-%05d' % (timestamp, random.randint(0, 99999))


def process_submit(f, task, language, user):
    """Calls judge_client.submit() with correct parameters."""
    contest_id = task.round.semester.competition.name

    # Determine language from filename if language not entered
    if language == '.':
        language = get_lang_from_filename(f.name)
        if not language:
            return False

    language = language.strip('.')
    data = smart_bytes(f.read())
    user_id = "%s-%d" % (contest_id, user.id)
    task_id = "%s-%d" % (contest_id, task.id)

    submit_id = _generate_submit_id()
    judge_client.submit(submit_id, user_id, task_id, data, language)

    return submit_id


def parse_result_and_points_from_protocol(submit):
    """
    Z XML protokolu získa výsledok testovania a počet bodov,
    ktoré sa neskôr môžu uložiť do databázy.

    Ak protokol ešte neexistuje, vráti None, None.
    """
    protocol_path = submit.protocol_path
    if not os.path.exists(protocol_path):
        return None, None

    with open(protocol_path) as protocol:
        return judge_client.parse_protocol(protocol, max_point=submit.task.source_points)


def update_submit(submit):
    """Zistí, či už je dotestované, ak hej, tak updatne databázu.

    Ak je dotestované, tak do zložky so submitmi testovač nahral súbor
    s rovnakým názvom ako má submit len s príponou .protokol
    (nastaviteľné v settings/common.py)

    Tento súbor obsahuje výstup testovača (v XML) a treba ho parse-núť
    """
    result, points = parse_result_and_points_from_protocol(submit)
    if result is not None:
        submit.tester_response = result
        submit.points = points
        submit.testing_status = constants.SUBMIT_STATUS_FINISHED
        submit.save()
