from django.conf import settings
from django.core import mail
from django.test import RequestFactory, TestCase

from .forms import ContactForm


class ContactFormTests(TestCase):
    valid_data = {'name': 'Test',
                  'email': 'test@example.com',
                  'subject': 'test subject',
                  'body': 'Test message'}

    def request(self):
        return RequestFactory().request()

    def test_valid_data_required(self):
        """
        Can't try to build the message dict unless data is valid.

        """
        data = {'name': 'Test',
                'body': 'Test message',
                'email': 'test@example.com'}
        form = ContactForm(request=self.request(), data=data)
        self.assertRaises(ValueError, form.get_message_dict)
        self.assertRaises(ValueError, form.get_context)

    def test_send(self):
        """
        Valid form can and does in fact send email.

        """
        form = ContactForm(request=self.request(),
                           data=self.valid_data)
        self.assertTrue(form.is_valid())

        form.save()
        self.assertEqual(1, len(mail.outbox))

        message = mail.outbox[0]
        self.assertTrue(self.valid_data['body'] in message.body)
        self.assertEqual(settings.DEFAULT_FROM_EMAIL,
                         message.from_email)
        self.assertEqual(form.recipient_list,
                         message.recipients())
        self.assertListEqual([self.valid_data['email']], message.reply_to)
