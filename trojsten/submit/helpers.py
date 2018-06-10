# -*- coding: utf-8 -*-
import os
import random
import socket
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError
from xml.parsers.expat import ExpatError
from decimal import Decimal
from time import time

from django.conf import settings
from django.utils.encoding import smart_bytes
from os import path
from unidecode import unidecode

from . import constants


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


def get_path_raw(contest_id, task_id, user_id):
    """Vypočíta cestu, kam uložiť súbory submitu bez dotknutia databázy.

    Cesta má tvar: $SUBMIT_PATH/submits/KSP/task_id/user_id
    """

    return os.path.join(settings.SUBMIT_PATH, 'submits',
                        str(user_id), str(task_id))


def get_path(task, user):
    """Vypočíta cestu, kam uložiť súbory submitu.

    Cesta má tvar: $SUBMIT_PATH/submits/KSP/task_id/user_id
    """
    return get_path_raw(
        task.round.semester.competition.name, "%s-%d" % (
            task.round.semester.competition.name, task.id
        ),
        "%s-%d" % (task.round.semester.competition.name, user.id)
    )


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


def post_submit(raw, data):
    """Pošle RAW na otestovanie"""
    if settings.SUBMIT_DEBUG:
        print("Submit RAW: ")
        print(raw)
        print(data)
    else:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((settings.TESTER_URL, settings.TESTER_PORT))
        sock.sendall(smart_bytes(raw))
        sock.sendall(smart_bytes(data))
        sock.close()


def process_submit_raw(f, contest_id, task_id, language, user_id):
    """Spracuje submit bez dotknutia databázy"""
    # Determine language from filename if language not entered
    if language == '.':
        language = get_lang_from_filename(f.name)
        if not language:
            return False

    language = language.strip('.')

    # Generate submit ID
    # Submit ID is <timestamp>-##### where ##### are 5 random digits
    timestamp = int(time())
    submit_id = "%d-%05d" % (timestamp, random.randint(0, 99999))

    # Prepare submit parameters (not entirely sure about this yet).
    user_id = "%s-%d" % (contest_id, user_id)
    task_id = "%s-%d" % (contest_id, task_id)
    data = f.read()

    # Determine local directory to store RAW file into
    path = get_path_raw(contest_id, task_id, user_id)

    priority = 0

    # Prepare RAW header from submit parameters
    raw = "submit1.3\n%s\n%s\n%s\n%s\n%s\n%s\nmagic_footer\n" % (
        settings.TESTER_WEB_IDENTIFIER,
        submit_id,
        user_id,
        task_id,
        language,
        priority,
    )

    # Write RAW to local file
    write_chunks_to_file(os.path.join(path, submit_id + constants.SUBMIT_RAW_FILE_EXTENSION), [raw, data])

    # Send RAW for testing (uncomment when deploying)
    post_submit(raw, data)

    # Return submit ID
    return submit_id


def process_submit(f, task, language, user):
    """Načíta všetko potrebné z databázy a spracuje submit"""
    contest_id = task.round.semester.competition.name
    return process_submit_raw(f, contest_id, task.id, language, user.id)


def parse_result_and_points_from_protocol(submit):
    """
    Z XML protokolu získa výsledok testovania a počet bodov,
    ktoré sa neskôr môžu uložiť do databázy.

    Ak protokol ešte neexistuje, vráti None, None.
    """
    protocol_path = submit.protocol_path
    if not os.path.exists(protocol_path):
        return None, None

    try:
        tree = ET.parse(protocol_path)
    except (ParseError, ExpatError):
        return constants.SUBMIT_RESPONSE_PROTOCOL_CORRUPTED, 0

    # Ak kompilátor vyhlási chyby, testovač ich vráti v tagu <compileLog>
    # Ak takýto tag existuje, výsledok je chyba pri testovaní a 0 bodov.
    clog = tree.find("compileLog")
    if clog is not None:
        return constants.SUBMIT_RESPONSE_ERROR, 0

    # Pre každý vstup kompilátor vyprodukuje tag <test>, všetky <test>-y
    # sú v tag-u <runLog>. Výsledok je buď OK, alebo prvý nájdený druh
    # chyby.
    runlog = tree.find("runLog")
    result = constants.SUBMIT_RESPONSE_OK
    for test in runlog:
        if test.tag != 'test':
            continue
        test_result = test[2].text
        if test_result != constants.SUBMIT_RESPONSE_OK:
            result = test_result
            break
    # Na konci testovača je v tagu <score> uložené percento získaných
    # bodov.
    try:
        score = Decimal(tree.find("runLog/score").text)
    except:  # noqa: E722 @FIXME
        score = 0
    points = (submit.task.source_points * score) / Decimal(100)

    return result, points


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
