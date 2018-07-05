from time import time

import random
import socket
from django.utils.encoding import smart_bytes


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

    def submit(self, user_id, task_id, submission_content, language):
        """Submits a file to the judge system.

        :param user_id: user id for the judge system in form of contestid-userid.
        :param task_id: task id for the judge system in form of contestid-taskid.
        :param submission_content: submission file content uploaded by user.
        :param language: programming language for the submission_file.
        :returns: submit_id
        """

        submit_id = JudgeClient._generate_submit_id()
        header = self._create_header(submit_id, user_id, task_id, language)
        self._send_data_to_server(header, submission_content)

        return submit_id

    @staticmethod
    def _generate_submit_id():
        """Generates a submit id in form of <timestamp>-##### where ##### are 5 random digits."""
        timestamp = int(time())
        return '%d-%05d' % (timestamp, random.randint(0, 99999))

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
        sock.connect((self.tester_url, self.tester_port))
        sock.sendall(header)
        sock.sendall(submission_file_content)
        sock.close()


class DebugJudgeClient(JudgeClient):
    def __init__(self):
        super(DebugJudgeClient, self).__init__('TEST_ID', 'TEST_URL', 47)

    def _send_data_to_server(self, header, submission_file_content):
        print('Submit RAW:')
        print(header)
        print(submission_file_content)

