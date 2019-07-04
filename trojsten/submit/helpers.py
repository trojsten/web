# -*- coding: utf-8 -*-
import os
import random
from os import path
from time import time

from django.conf import settings
from django.utils.encoding import smart_bytes
from judge_client import constants as judge_constants
from judge_client.client import ProtocolCorruptedError
from unidecode import unidecode

from . import constants

judge_client = settings.JUDGE_CLIENT


def write_chunks_to_file(target_path, chunks):
    try:
        os.makedirs(os.path.dirname(target_path))
    except OSError:
        # Directory exists.
        pass
    with open(target_path, 'wb+') as destination:
        for chunk in chunks:
            destination.write(smart_bytes(chunk))


def _get_lang_from_filename(filename):
    ext = os.path.splitext(filename)[1].lower()
    return constants.EXT_MAPPING.get(ext, None)


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
        language = _get_lang_from_filename(f.name)
        if not language:
            return False

    # TODO: Strip '.' before
    language = language.strip('.')

    submit_id = _generate_submit_id()
    user_id = "%s-%d" % (contest_id, user.id)
    task_id = "%s-%d" % (contest_id, task.id)
    data = f.read()

    judge_client.submit(submit_id, user_id, task_id, data, language)

    return submit_id


def parse_result_and_points_from_protocol(submit):
    """Parses result and points from XML protocol.

    :param submit: submit model instance.
    :return: subimt_result, points or None, None if protocol does not exist.
    """
    if submit.protocol is None:
        return None, None
    try:
        # TODO: limit protocol size so we don't go OOM in case of malicious protocol.
        protocol = judge_client.parse_protocol(
            submit.protocol, max_points=submit.task.source_points)
        return protocol.result, protocol.points
    except ProtocolCorruptedError:
        return judge_constants.SUBMIT_RESPONSE_PROTOCOL_CORRUPTED, 0
