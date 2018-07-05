# coding=utf-8
import socket
from decimal import Decimal
from django.utils.encoding import smart_bytes
from xlrd.xlsx import ET

from trojsten.submit import constants


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

    def submit(self, submit_id, user_id, task_id, submission_content, language):
        """Submits a file to the judge system.

        :param submit_id: unique id of the submit.
        :param user_id: user id for the judge system in form of contestid-userid.
        :param task_id: task id for the judge system in form of contestid-taskid.
        :param submission_content: submission file content uploaded by user.
        :param language: programming language for the submission_file.
        :returns: submit_id
        """

        header = self._create_header(submit_id, user_id, task_id, language)
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
            tree = ET.parse(protocol_content)
        except SyntaxError:
            raise ProtocolCorruptedError('Error while parsing protocol.\n%s' % protocol_content)

        compile_log = tree.find("compileLog")
        if compile_log is not None:
            return constants.SUBMIT_RESPONSE_ERROR, 0  # Returns zero points if there was error.

        run_log = tree.find("runLog")
        result = constants.SUBMIT_RESPONSE_OK
        for test in run_log:
            if test.tag != 'test':
                continue
            test_result = test[2].text
            if test_result != constants.SUBMIT_RESPONSE_OK:
                result = test_result
                break
        try:
            score = Decimal(tree.find("runLog/score").text)
        except (ValueError, TypeError):
            raise ProtocolFormatError("Invalid score.\n%s" % protocol_content)
        points = (max_points * score) / Decimal(100)

        return result, points

    def _create_header(self, submit_id, user_id, task_id, language):
        """Creates a raw header from submit parameters"""
        return smart_bytes('submit1.3\n%s\n%s\n%s\n%s\n%s\n%s\nmagic_footer\n' % (
            self.tester_id,
            submit_id,
            user_id,
            task_id,
            language,
            0,  # priority
        ))

    def _send_data_to_server(self, header, submission_file_content):
        """Sends submission to the judge system."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((self.tester_url, self.tester_port))
            sock.sendall(header)
            sock.sendall(submission_file_content)
        except JudgeConnectionError:
            raise JudgeConnectionError('Failed to connect to judge system (%s:%s)' % (self.tester_url, self.tester_port))
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
    pass


class ProtocolError(ValueError):
    pass


class ProtocolCorruptedError(ProtocolError):
    pass


class ProtocolFormatError(ProtocolError):
    pass