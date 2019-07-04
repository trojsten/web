from django.conf import settings
from django.core import mail
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from trojsten.people.models import User
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
        form = ContactForm(request=self.request(), captcha=False, data=data)
        self.assertRaises(ValueError, form.get_message_dict)
        self.assertRaises(ValueError, form.get_context)

    @override_settings(CONTACT_FORM_RECIPIENTS=('roots@example.com', ))
    def test_send(self):
        """
        Valid form can and does in fact send email.

        """
        form = ContactForm(request=self.request(),
                           captcha=False,
                           data=self.valid_data)
        self.assertTrue(form.is_valid())

        form.save()
        self.assertEqual(1, len(mail.outbox))

        message = mail.outbox[0]
        self.assertTrue(self.valid_data['body'] in message.body)
        self.assertEqual(settings.DEFAULT_FROM_EMAIL,
                         message.from_email)
        self.assertEqual(settings.CONTACT_FORM_RECIPIENTS,
                         tuple(message.recipients()))
        self.assertListEqual([
            '{}<{}>'.format(self.valid_data['name'], self.valid_data['email'])
        ], message.reply_to)

    def test_captcha_field_present(self):
        form = ContactForm(request=self.request(), captcha=True)
        self.assertTrue('captcha' in form.fields)

    def test_view_with_anonymous(self):
        response = self.client.get(reverse('contact_form'))
        self.assertContains(response, _('Name'))
        self.assertContains(response, _('Email'))
        self.assertContains(response, _('Message'))
        self.assertContains(response, 'Captcha')

    def test_view_with_logged_in(self):
        user = User.objects.create()
        self.client.force_login(user)
        response = self.client.get(reverse('contact_form'))
        self.assertContains(response, _('Name'))
        self.assertContains(response, _('Email'))
        self.assertContains(response, _('Message'))
        self.assertNotContains(response, 'Captcha')
