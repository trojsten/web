# coding=utf-8
import socket
from collections import namedtuple
from decimal import Decimal
from xml.etree import ElementTree

from django.utils.encoding import smart_bytes

from trojsten.submit import constants

Protocol = namedtuple('Protocol', ['result', 'points', 'compile_log', 'tests'])
ProtocolTest = namedtuple('ProtocolTest', ['name', 'result', 'time', 'details'])


class JudgeClient(object):

    def __init__(self, tester_id, tester_url, tester_port):
        """Initializes JudgeClient instance.

        :param tester_id:
        :param tester_url:
        :param tester_port:
        :param storage:
        """
        self.tester_id = tester_id
        self.tester_url = tester_url
        self.tester_port = tester_port

    def submit(self, submit_id, user_id, task_id, submission_content, language, priority=0):
        """Submits a file to the judge system.

        :param submit_id: unique id of the submit.
        :param user_id: user id for the judge system in form of contestid-userid.
        :param task_id: task id for the judge system in form of contestid-taskid.
        :param submission_content: submission file content uploaded by user.
        :param language: programming language for the submission_file.
        :returns: submit_id
        """

        header = self._create_header(submit_id, user_id, task_id, language, priority)
        self._send_data_to_server(header, submission_content)

    @staticmethod
    def parse_protocol(protocol_content, max_points):
        """Parses protocol returned by judge system.

        If protocol contains <compileLog> it means there was a testing error.
        If any of <test> tag in <runLog> contains non OK result, the overall result is the first non OK result.
        The points are computed from percentage of maximum points stored in <score> tag.

        :param protocol_content: content of the protocol.
        :param max_points: maximum possible points for the task.
        :return: testing_result, number_of_points
        """
        try:
            tree = ElementTree.fromstring(protocol_content)
        except SyntaxError:
            raise ProtocolCorruptedError(
                'Error while parsing protocol.', protocol_content)

        compile_log = tree.find("compileLog")
        if compile_log is not None:
            return Protocol(
                points=0,  # Returns zero points if there was error.
                result=constants.SUBMIT_RESPONSE_ERROR,
                compile_log=compile_log.text,
                tests=tuple())

        result = constants.SUBMIT_RESPONSE_OK
        tests = []
        run_log = tree.find("runLog")
        for test in run_log:
            if test.tag != 'test':
                continue
            test_result = test[2].text
            details = test[4].text if len(test) > 4 else None
            tests.append(ProtocolTest(name=test[0].text,
                                      result=test_result,
                                      time=test[3].text,
                                      details=details))
            if test_result != constants.SUBMIT_RESPONSE_OK:
                result = test_result
                break
        try:
            score = Decimal(tree.find("runLog/score").text)
        except (ValueError, TypeError):
            raise ProtocolFormatError("Invalid score.", protocol_content)
        points = (max_points * score) / Decimal(100)
        return Protocol(result=result, points=points, compile_log=None, tests=tests)

    def _create_header(self, submit_id, user_id, task_id, language, priority):
        """Creates a raw header from submit parameters"""
        return 'submit1.3\n%s\n%s\n%s\n%s\n%s\n%s\nmagic_footer\n' % (
            self.tester_id,
            submit_id,
            user_id,
            task_id,
            language,
            priority,
        )

    def _send_data_to_server(self, header, submission_file_content):
        """Sends submission to the judge system."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((self.tester_url, self.tester_port))
            sock.sendall(smart_bytes(header))
            sock.sendall(smart_bytes(submission_file_content))
        except JudgeConnectionError:
            raise JudgeConnectionError(
                'Failed to connect to judge system (%s:%s)' % (self.tester_url, self.tester_port))
        finally:
            sock.close()


class DebugJudgeClient(JudgeClient):
    def __init__(self):
        super(DebugJudgeClient, self).__init__('TEST_ID', 'TEST_URL', 47)

    def _send_data_to_server(self, header, submission_file_content):
        print('Submit RAW:')
        print(header)
        print(submission_file_content)


class JudgeConnectionError(IOError):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return '%s: %s' % (self.__class__.__name__, repr(self.message))


class ProtocolError(ValueError):
    def __init__(self, message, protocol):
        self.message = message
        self.protocol = protocol

    def __str__(self):
        return '%s: %s\n%s\n' % (self.__class__.__name__, repr(self.message), self.protocol)


class ProtocolCorruptedError(ProtocolError):
    pass


class ProtocolFormatError(ProtocolError):
    pass
