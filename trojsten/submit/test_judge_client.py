import time

import socket
import threading
from unittest import TestCase

from trojsten.submit.judge_client import JudgeClient


class SubmitHelpersTests(TestCase):
    TESTER_URL = '127.0.0.1'
    TESTER_PORT = 7777
    TESTER_ID = 'TEST'

    def setUp(self):
        self.judge_client = JudgeClient(self.TESTER_ID, self.TESTER_URL, self.TESTER_PORT)

    def test_submit(self):
        def run_fake_server(test):
            server_sock = socket.socket()
            server_sock.bind((self.TESTER_URL, self.TESTER_PORT))
            server_sock.listen(0)
            conn, addr = server_sock.accept()
            raw = conn.recv(2048)
            data = conn.recv(2048)
            server_sock.close()
            test.received = raw + data

        server_thread = threading.Thread(target=run_fake_server, args=(self,))
        server_thread.start()
        time.sleep(50.0 / 1000.0)  # 50ms should be enough for the server to bind
        self.judge_client.submit('test_user', 'test_task', 'test_submission', 'py')
        server_thread.join()

        request_parts = self.received.split('\n')
        # Header
        self.assertEqual(request_parts[0], b'submit1.3')
        self.assertEqual(request_parts[1], b'TEST')
        self.assertEqual(len(request_parts[2]), 16)
        self.assertEqual(request_parts[3], b'test_user')
        self.assertEqual(request_parts[4], b'test_task')
        self.assertEqual(request_parts[5], b'py')
        self.assertEqual(request_parts[6], b'0')
        self.assertEqual(request_parts[7], b'magic_footer')
        # Submission
        self.assertEqual(request_parts[8], b'test_submission')

