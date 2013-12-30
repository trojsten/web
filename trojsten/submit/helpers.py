from django.conf import settings
from time import time
import os
import random
import socket
import xml.etree.ElementTree as ET


def write_file(what, where):
    try:
        os.makedirs(where.rsplit('/', 1)[0])
    except:
        pass
    with open(where, 'w+') as destination:
        destination.write(what)


def save_file(what, where):
    try:
        os.makedirs(where.rsplit('/', 1)[0])
    except:
        pass
    with open(where, 'wb+') as destination:
        for chunk in what.chunks():
            destination.write(chunk)


def get_lang_from_filename(filename):
    ext = os.path.splitext(filename)[1].lower()
    extmapping = {
        ".cpp": ".cc",
        ".cc":  ".cc",
        ".pp":  ".pas",
        ".pas": ".pas",
        ".dpr": ".pas",
        ".c":   ".c",
        ".py":  ".py",
        ".py3": ".py3",
        ".hs":  ".hs",
        ".cs":  ".cs",
        ".java": ".java"}

    if not ext in extmapping:
        return False
    return extmapping[ext]


def get_path_raw(contest_id, task_id, user_id):
    return "%s/submits/%s/%s/%s" % (
        settings.SUBMIT_PATH,
        str(contest_id),
        str(task_id),
        str(user_id))


def get_path(task, user):
    return get_path_raw(task.round.series.competition.name, task.id, user.id)


def build_raw(contest_id, submit_id, user_id, correct_filename, timestamp, original_name, data):
    return "%s\n%s\n%s\n%s\n%s\n%s\n%s" % (
        contest_id,
        submit_id,
        user_id,
        correct_filename,
        timestamp,
        original_name,
        data)


def post_submit(raw):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((settings.TESTER_URL, settings.TESTER_PORT))
    sock.send(raw)
    sock.close()


def send_submit(f, contest_id, task_id, language, user_id):
    # Determine language from filename if language not entered
    if language == '.':
        lang = get_lang_from_filename(f.name)
        if not lang:
            return False
        language = lang

    # Generate submit ID
    timestamp = int(time())
    submit_id = str(timestamp) + '-'
    for i in range(0, 5):
        submit_id += str(random.randint(0, 9))

    # Prepare local directories
    path = get_path_raw(contest_id, task_id, user_id)

    # Prepare variables
    user_id = contest_id + '-' + str(user_id)
    task_id = contest_id + '-' + str(task_id)
    original_name = f.name
    correct_filename = task_id + language
    data = f.read()

    # Prepare RAW
    raw = "%s\n%s\n%s\n%s\n%s\n%s\n%s" % (
        contest_id,
        submit_id,
        user_id,
        correct_filename,
        timestamp,
        original_name,
        data)

    # Write RAW to local file
    write_file(raw, path + '/' + submit_id + '.raw')

    # Send RAW for testing
    # post_submit(raw)

    # Return submit "timestamp" ID
    return submit_id


def process_submit(f, task, language, user):
    contest_id = task.round.series.competition.name
    return send_submit(f, contest_id, task.id, language, user.id)

def update_submit(submit):
    protocol_path = submit.filepath.rsplit('.',1)[0] + '.protokol'
    if os.path.exists(protocol_path):
        tree = ET.parse(protocol_path)
        clog = tree.find("compileLog")
        if clog is not None:
            result = 'CERR'
            clog = clog.text
            score = 0
            points = 0
        else:
            runlog = tree.find("runLog")
            result = 'OK'
            for test in runlog:
                if test.tag != 'test':
                    continue
                test_result = test[2].text
                if test_result != 'OK':
                    result = test_result
                    break
            score = int(float(tree.find("runLog/score").text))
            points = (submit.task.source_points * score) // 100
        submit.points = points
        submit.tester_response = result
        submit.testing_status = 'finished'
