from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone

from trojsten.contests.models import Competition, Semester, Round, Task, Category
from trojsten.people.models import User, UserProperty, UserPropertyKey
from trojsten.rules.kms import KMS_ALFA, KMS_BETA, KMS_COEFFICIENT_PROP_NAME
from trojsten.submit.models import Submit


def get_row_for_user(tables, user, category):
    for table in tables:
        if table.tag.key == category:
            for row in table.rows:
                if row.user == user:
                    return row


class KMSRulesTest(TestCase):
    def setUp(self):
        competition = Competition.objects.create(name='TestCompetition', pk=7)
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        self.semester = Semester.objects.create(number=1, name='Test semester', competition=competition,
                                                year=1)
        self.start = timezone.now() + timezone.timedelta(-8)
        self.end = timezone.now() + timezone.timedelta(-2)
        round = Round.objects.create(number=1, semester=self.semester, visible=True,
                                     solutions_visible=False, start_time=self.start, end_time=self.end)

        category_alfa = Category.objects.create(name=KMS_ALFA, competition=competition)
        category_beta = Category.objects.create(name=KMS_BETA, competition=competition)

        self.tasks = []
        for i in range(1, 11):
            self.tasks.append(Task.objects.create(number=i, name='Test task {}'.format(i), round=round))
            cat = []
            if i <= 7:
                cat += [category_alfa]
            if i >= 4:
                cat += [category_beta]
            self.tasks[-1].categories = cat
            self.tasks[-1].save()

        year = timezone.now().year + 2
        self.user = User.objects.create(username="TestUser", password="password",
                                        first_name="Jozko", last_name="Mrkvicka", graduation=year)
        self.coeff_prop_key = UserPropertyKey.objects.create(key_name=KMS_COEFFICIENT_PROP_NAME)

        self.url = reverse('view_latest_results')

    def create_submits(self, user, points):
        for i in range(len(points)):
            if points[i] >= 0:
                submit = Submit.objects.create(task=self.tasks[i], user=user,
                                               submit_type=1, points=points[i], testing_status='reviewed')
                submit.time = self.start + timezone.timedelta(days=2)
                submit.save()

    def test_only_best_five(self):

        points = [9, 7, 0, 8, 4, 5, 4]
        active = [True] * 7
        active[2] = False
        self.create_submits(self.user, points)

        response = self.client.get("%s?single_round=True" % self.url)
        self.assertEqual(response.status_code, 200)
        row = get_row_for_user(response.context['tables'], self.user, KMS_ALFA)
        self.assertEqual(row.cells_by_key['sum'].points, '33')
        for i in range(1, 8):
            self.assertEqual(row.cells_by_key[i].points, str(points[i-1]))
            if i not in [5, 7]:
                self.assertEqual(row.cells_by_key[i].active, active[i-1])
        self.assertTrue(row.cells_by_key[5].active ^ row.cells_by_key[7].active)

    def test_tasks_coefficients_alfa(self):
        UserProperty.objects.create(user=self.user, key=self.coeff_prop_key, value=3)
        points = [1, 2, 3, 4, 5, 6, 7]
        self.create_submits(self.user, points)
        response = self.client.get("%s?single_round=True" % self.url)
        self.assertEqual(response.status_code, 200)
        row = get_row_for_user(response.context['tables'], self.user, KMS_ALFA)
        for i in range(1, 3):
            self.assertFalse(row.cells_by_key[i].active)
        for i in range(3, 8):
            self.assertTrue(row.cells_by_key[i].active)
        self.assertEqual(row.cells_by_key['sum'].points, '25')

    def test_tasks_coefficients_beta(self):
        UserProperty.objects.create(user=self.user, key=self.coeff_prop_key, value=7)
        points = [-1, -1, -1, 3, 4, 5, 6, 7, 8]
        self.create_submits(self.user, points)
        response = self.client.get("%s?single_round=True" % self.url)
        self.assertEqual(response.status_code, 200)
        row = get_row_for_user(response.context['tables'], self.user, KMS_BETA)
        self.assertFalse(row.cells_by_key[4].active)
        for i in range(5, 10):
            self.assertTrue(row.cells_by_key[i].active)
        self.assertEqual(row.cells_by_key['sum'].points, '30')

    def test_beta_only_user(self):
        UserProperty.objects.create(user=self.user, key=self.coeff_prop_key, value=7)
        points = [-1, -1, 2, 3, 4, 5, 6, 7, 8]
        self.create_submits(self.user, points)
        response = self.client.get("%s?single_round=True" % self.url)
        self.assertEqual(response.status_code, 200)
        row_beta = get_row_for_user(response.context['tables'], self.user, KMS_BETA)
        row_alfa = get_row_for_user(response.context['tables'], self.user, KMS_ALFA)
        self.assertTrue(row_beta.active)
        self.assertFalse(row_alfa.active)

    def test_alfa_only_user(self):
        UserProperty.objects.create(user=self.user, key=self.coeff_prop_key, value=1)
        points = [1, 2, 3, 4, 5]
        self.create_submits(self.user, points)
        response = self.client.get("%s?single_round=True" % self.url)
        self.assertEqual(response.status_code, 200)
        row_beta = get_row_for_user(response.context['tables'], self.user, KMS_BETA)
        row_alfa = get_row_for_user(response.context['tables'], self.user, KMS_ALFA)
        self.assertTrue(row_alfa.active)
        self.assertFalse(row_beta.active)

    def test_alfa_beta_user(self):
        UserProperty.objects.create(user=self.user, key=self.coeff_prop_key, value=1)
        points = [1, 2, 3, 4, 5, 6, 7, 8, 9, 9]
        self.create_submits(self.user, points)
        response = self.client.get("%s?single_round=True" % self.url)
        self.assertEqual(response.status_code, 200)
        row_beta = get_row_for_user(response.context['tables'], self.user, KMS_BETA)
        row_alfa = get_row_for_user(response.context['tables'], self.user, KMS_ALFA)
        self.assertEqual(row_alfa.cells_by_key['sum'].points, '25')
        self.assertEqual(row_beta.cells_by_key['sum'].points, '39')
