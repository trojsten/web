from django.conf import settings
from django.contrib.sites.models import Site
from django.urls import reverse

from trojsten.diplomas.models import DiplomaTemplate
from trojsten.people.models import User

from django.contrib.auth.models import Group
from django.test import TransactionTestCase, override_settings

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

english = override_settings(
    LANGUAGE_CODE='en-US',
    LANGUAGES=(('en', 'English'),),
)


class CreateDiplomaTestCase(TransactionTestCase):
    fixtures = ['diploma_templates.json']

    def setUp(self):
        self.site = Site.objects.get(pk=settings.SITE_ID)

        self.template = DiplomaTemplate.objects.filter(pk=1).get()

        self.form_data = urlencode({'template': 1, 'participants_data': "fieldname\nfieldvalue\n", 'join_pdf': 'on'})

        self.user_standard = User.objects.create_user("standard_user", 'test@email.com', 'pass')

        self.user_super = User.objects.create_superuser('super_user', 'super@user.com', 'pass')

        self.test_group = Group.objects.create(name='test_group')

        self.url = reverse('view_diplomas')

    def test_create_diploma(self):
        self.client.force_login(self.user_super)

        r = self.client.post(self.url,
                             data=self.form_data,
                             content_type="application/x-www-form-urlencoded")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content-Type'], 'application/zip')

    @english
    def test_malformed_input(self):
        self.client.force_login(self.user_super)
        malformed = urlencode({'template': 1, 'participants_data': "[{'name': 'val]", 'join_pdf': 'on'})
        r = self.client.post(self.url,
                             data=malformed,
                             content_type="application/x-www-form-urlencoded")
        messages = list(r.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Participants data: Failed to parse the input data')

    def test_standard_user_permissions(self):
        self.template.authorized_groups.add(self.test_group)

        self.client.force_login(self.user_standard)

        # Test that user who isnt superuser cant access template with group permissions if he's not in one
        r = self.client.post(self.url,
                             data=self.form_data,
                             content_type="application/x-www-form-urlencoded")
        self.assertEqual(r.status_code, 403)

        # Test that same user can't even preview template or get sources of template
        r = self.client.get(reverse('diploma_preview', kwargs={'diploma_id': 1}))
        self.assertEqual(r.status_code, 403)

        r = self.client.get(reverse('diploma_sources', kwargs={'diploma_id': 1}))
        self.assertEqual(r.status_code, 403)

        # Test that adding the user to group grants these permissions
        self.user_standard.groups.add(self.test_group)
        self.client.force_login(self.user_standard)

        r = self.client.post(self.url,
                             data=self.form_data,
                             content_type="application/x-www-form-urlencoded")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content-Type'], 'application/zip')

        r = self.client.get(reverse('diploma_preview', kwargs={'diploma_id': 1}))
        self.assertEqual(r.status_code, 200)

        r = self.client.get(reverse('diploma_sources', kwargs={'diploma_id': 1}))
        self.assertEqual(r.status_code, 200)

    def test_superuser_permissions(self):
        self.template.authorized_groups.add(self.test_group)

        self.client.force_login(self.user_super)

        r = self.client.post(self.url,
                             data=self.form_data,
                             content_type="application/x-www-form-urlencoded")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content-Type'], 'application/zip')

        r = self.client.get(reverse('diploma_preview', kwargs={'diploma_id': 1}))
        self.assertEqual(r.status_code, 200)

        r = self.client.get(reverse('diploma_sources', kwargs={'diploma_id': 1}))
        self.assertEqual(r.status_code, 200)
