from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone

import trojsten.submit.constants as submit_constants
from trojsten.contests.models import Competition, Semester, Round, Task, Category
from trojsten.people.models import User, UserProperty, UserPropertyKey
from trojsten.rules.kms import KMS_ALFA, KMS_BETA, KMS_COEFFICIENT_PROP_NAME
from trojsten.rules.ksp import KSP_O, KSP_Z
from trojsten.submit.models import Submit

SOURCE = submit_constants.SUBMIT_TYPE_SOURCE
DESCRIPTION = submit_constants.SUBMIT_TYPE_DESCRIPTION


def get_row_for_user(tables, user, category):
    for table_object in tables:
        table = table_object.table
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

    def _create_submits(self, user, points):
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
        self._create_submits(self.user, points)

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
        self._create_submits(self.user, points)
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
        self._create_submits(self.user, points)
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
        self._create_submits(self.user, points)
        response = self.client.get("%s?single_round=True" % self.url)
        self.assertEqual(response.status_code, 200)
        row_beta = get_row_for_user(response.context['tables'], self.user, KMS_BETA)
        row_alfa = get_row_for_user(response.context['tables'], self.user, KMS_ALFA)
        self.assertTrue(row_beta.active)
        self.assertFalse(row_alfa.active)

    def test_alfa_only_user(self):
        UserProperty.objects.create(user=self.user, key=self.coeff_prop_key, value=1)
        points = [1, 2, 3, 4, 5]
        self._create_submits(self.user, points)
        response = self.client.get("%s?single_round=True" % self.url)
        self.assertEqual(response.status_code, 200)
        row_beta = get_row_for_user(response.context['tables'], self.user, KMS_BETA)
        row_alfa = get_row_for_user(response.context['tables'], self.user, KMS_ALFA)
        self.assertTrue(row_alfa.active)
        self.assertFalse(row_beta.active)

    def test_alfa_beta_user(self):
        UserProperty.objects.create(user=self.user, key=self.coeff_prop_key, value=1)
        points = [1, 2, 3, 4, 5, 6, 7, 8, 9, 9]
        self._create_submits(self.user, points)
        response = self.client.get("%s?single_round=True" % self.url)
        self.assertEqual(response.status_code, 200)
        row_beta = get_row_for_user(response.context['tables'], self.user, KMS_BETA)
        row_alfa = get_row_for_user(response.context['tables'], self.user, KMS_ALFA)
        self.assertEqual(row_alfa.cells_by_key['sum'].points, '25')
        self.assertEqual(row_beta.cells_by_key['sum'].points, '39')


class KSPRulesSubmitsAfterDeadlineTest(TestCase):
    def setUp(self):
        competition = Competition.objects.create(name='TestKSP', pk=2)  # pk = 2 sets rules to KSPRules
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        self.semester = Semester.objects.create(number=1, name='Test semester', competition=competition, year=1)
        self.start = timezone.now() - timezone.timedelta(days=21)
        self.end = timezone.now() - timezone.timedelta(days=14)
        self.second_end = timezone.now() - timezone.timedelta(days=7)
        self.round = Round.objects.create(number=1, semester=self.semester, visible=True, solutions_visible=False,
                                          start_time=self.start, end_time=self.end, second_end_time=self.second_end)

        category_z = Category.objects.create(name=KSP_Z, competition=competition)
        category_o = Category.objects.create(name=KSP_O, competition=competition)

        self.tasks = []
        for i in range(1, 4):
            self.tasks.append(Task.objects.create(number=i, name='Test task {}'.format(i), round=self.round))
            self.tasks[-1].categories = [category_z, category_o]
            self.tasks[-1].save()

        self.tasks[2].integer_source_points = False
        self.tasks[2].save()

        graduation = timezone.now().year + 2
        self.user = User.objects.create(username='TestUser', password='password',
                                        first_name='Jozko', last_name='Mrkvicka', graduation=graduation)

        self.url = reverse('view_latest_results')

    def _create_submits(self, submit_definitions):
        for task_number, submit_type, submit_time, points in submit_definitions:
            submit = Submit.objects.create(task=self.tasks[task_number-1], user=self.user,
                                           submit_type=submit_type, points=points)
            submit.time = submit_time
            if submit_type == DESCRIPTION:
                submit.testing_status = 'reviewed'
            submit.save()

    def _get_point_cells_for_tasks(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        row = get_row_for_user(response.context['tables'], self.user, KSP_Z)
        return row.cells_by_key

    def test_submits_in_first_phase(self):
        self._create_submits([
            (1, SOURCE, self.start + timezone.timedelta(days=1), 10),
            (2, SOURCE, self.start + timezone.timedelta(days=2), 8)
        ])

        cells = self._get_point_cells_for_tasks()
        self.assertEqual(cells[1].points, '10')
        self.assertEqual(cells[2].points, '8')
        self.assertEqual(cells[3].points, '')
        self.assertEqual(cells['sum'].points, '18')

    def test_last_submit_in_first_phase(self):
        self._create_submits([
            (1, SOURCE, self.start + timezone.timedelta(days=1), 7),
            (1, SOURCE, self.start + timezone.timedelta(days=2), 9),
            (1, SOURCE, self.start + timezone.timedelta(days=3), 6),

            (2, SOURCE, self.start + timezone.timedelta(days=1), 3),
            (2, SOURCE, self.start + timezone.timedelta(days=4), 2),
        ])

        cells = self._get_point_cells_for_tasks()
        self.assertEqual(cells[1].points, '6')
        self.assertEqual(cells[2].points, '2')

    def test_submits_in_second_phase(self):
        self._create_submits([
            (1, SOURCE, self.end + timezone.timedelta(days=1), 7),
            (2, SOURCE, self.end + timezone.timedelta(days=2), 4)
        ])

        cells = self._get_point_cells_for_tasks()
        self.assertEqual(cells[1].points, '3.5')
        self.assertEqual(cells[2].points, '2')
        self.assertEqual(cells[3].points, '')
        self.assertEqual(cells['sum'].points, '5.5')

    def test_last_submit_in_second_phase(self):
        self._create_submits([
            (1, SOURCE, self.end + timezone.timedelta(days=1), 8),
            (1, SOURCE, self.end + timezone.timedelta(days=2), 3),
        ])
        cells = self._get_point_cells_for_tasks()
        self.assertEqual(cells[1].points, '1.5')

    def test_submits_after_round_end(self):
        self._create_submits([
            (1, SOURCE, self.start + timezone.timedelta(days=1), 7),
            (1, SOURCE, self.second_end + timezone.timedelta(seconds=1), 10),
            (1, SOURCE, self.second_end + timezone.timedelta(days=1), 10),

            (2, SOURCE, self.second_end + timezone.timedelta(seconds=1), 13),

            (3, SOURCE, self.end + timezone.timedelta(seconds=1), 9),
            (3, SOURCE, self.second_end + timezone.timedelta(seconds=1), 10),
        ])
        cells = self._get_point_cells_for_tasks()
        self.assertEqual(cells[1].points, '7')
        self.assertEqual(cells[2].points, '')
        self.assertEqual(cells[3].points, '4.50')

    def test_submits_in_all_phases(self):
        self._create_submits([
            (1, SOURCE, self.start + timezone.timedelta(days=1), 6),
            (1, SOURCE, self.end + timezone.timedelta(days=1), 9),
            (1, SOURCE, self.second_end + timezone.timedelta(days=1), 10),

            (2, SOURCE, self.start + timezone.timedelta(days=1), 4),
            (2, SOURCE, self.end + timezone.timedelta(days=1), 8),
            (2, SOURCE, self.second_end + timezone.timedelta(days=1), 9),

            (3, SOURCE, self.start + timezone.timedelta(days=1), 4.32),
            (3, SOURCE, self.end + timezone.timedelta(days=1), 4.32 + 6.57),
            (3, SOURCE, self.second_end + timezone.timedelta(days=1), 20)
        ])

        cells = self._get_point_cells_for_tasks()
        self.assertEqual(cells[1].points, '7.5')
        self.assertEqual(cells[2].points, '6')
        self.assertEqual(cells[3].points, '{:.3f}'.format(4.32 + 6.57/2))

    def test_fewer_points_in_second_phase(self):
        self._create_submits([
            (1, SOURCE, self.start + timezone.timedelta(days=1), 7),
            (1, SOURCE, self.end + timezone.timedelta(days=1), 4),
            (1, SOURCE, self.second_end + timezone.timedelta(days=1), 10),

            (2, SOURCE, self.start + timezone.timedelta(days=1), 10),
            (2, SOURCE, self.end + timezone.timedelta(days=1), 0),
            (2, SOURCE, self.second_end + timezone.timedelta(days=1), 5),
        ])

        cells = self._get_point_cells_for_tasks()
        self.assertEqual(cells[1].points, '7')
        self.assertEqual(cells[2].points, '10')

    def test_submits_with_desriptions(self):
        self._create_submits([
            (1, SOURCE, self.start + timezone.timedelta(days=1), 6),
            (1, SOURCE, self.end + timezone.timedelta(days=1), 8),
            (1, SOURCE, self.second_end + timezone.timedelta(days=1), 10),
            (1, DESCRIPTION, self.start + timezone.timedelta(days=1), 5),

            (2, SOURCE, self.start + timezone.timedelta(days=1), 9),
            (2, SOURCE, self.end + timezone.timedelta(days=1), 10),
            (2, SOURCE, self.second_end + timezone.timedelta(days=1), 5),
            (2, DESCRIPTION, self.start + timezone.timedelta(days=1), 3),
            (2, DESCRIPTION, self.second_end + timezone.timedelta(days=1), 9),
        ])

        cells = self._get_point_cells_for_tasks()
        self.assertEqual(cells[1].auto_points, '7')
        self.assertEqual(cells[1].manual_points, '5')
        self.assertEqual(cells[1].points, '12')

        self.assertEqual(cells[2].auto_points, '9.5')
        self.assertEqual(cells[2].manual_points, '9')
        self.assertEqual(cells[2].points, '18.5')

    def test_round_without_second_end(self):
        self.round.second_end_time = None
        self.round.save()

        self._create_submits([
            (1, SOURCE, self.start + timezone.timedelta(days=1), 2),
            (1, SOURCE, self.start + timezone.timedelta(days=2), 6),
            (1, SOURCE, self.end + timezone.timedelta(days=1), 10),
            (1, DESCRIPTION, self.start + timezone.timedelta(days=1), 4),

            (2, SOURCE, self.start + timezone.timedelta(days=1), 9),
            (2, SOURCE, self.start + timezone.timedelta(days=2), 5),
            (2, SOURCE, self.end + timezone.timedelta(days=1), 10),
            (2, DESCRIPTION, self.start + timezone.timedelta(days=1), 3),
            (2, DESCRIPTION, self.end + timezone.timedelta(days=10), 9),
        ])

        cells = self._get_point_cells_for_tasks()
        self.assertEqual(cells[1].auto_points, '6')
        self.assertEqual(cells[1].manual_points, '4')
        self.assertEqual(cells[1].points, '10')

        self.assertEqual(cells[2].auto_points, '5')
        self.assertEqual(cells[2].manual_points, '9')
        self.assertEqual(cells[2].points, '14')
