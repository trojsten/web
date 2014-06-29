from django.test import TestCase, Client
from trojsten.regal.tasks.models import Submit, Task, Category, SubmitType
from trojsten.regal.people.models import Address
from trojsten.regal.contests.models import Competition, Series, Round
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
import datetime

from trojsten.results import views


class ResultsTestCase(TestCase):
    def setUp(self):
        # create empty address
        self.address = Address.objects.create(
            street='test', town='test', number=10, postal_code='00000', country='test'
        )
        # create users and persons
        usernames = [str(i) for i in range(10)]
        self.users = [User.objects.create(username=username) for username in usernames]
        # create series
        self.competition = Competition.objects.create(name='test')
        self.series = Series.objects.create(competition=self.competition, name='test', number=1, year=1)
        # create rounds
        round_names = [1, 2]
        self.rounds = [
            Round.objects.create(
                number=i, series=self.series, end_time=datetime.date.today(), visible=True
            ) for i in round_names
        ]
        # create tasks
        self.submit_types = {name: SubmitType.objects.create(name=name) for name in ['source', 'description']}
        self.categories = {
            name: Category.objects.create(name=name, competition=self.competition) for name in ['z', 'o']
        }
        self.task_cnt = 5
        self.tasks = [
            Task.objects.create(
                number=i, round=round, name=str(i), description_points=10, source_points=10
            ) for i in range(self.task_cnt) for round in self.rounds
        ]
        for t in self.tasks:
            t.task_types.add(self.submit_types['source'])
            t.task_types.add(self.submit_types['description'])
            t.category.add(self.categories['z'])
            t.category.add(self.categories['o'])
        # create submits
        descriptions = [
            [1, 2, 3],
            [1, 2, 3],
            [i for i in range(self.task_cnt)],
            [1, 2, 3, 4, 5],
            [4, 5, 6],
        ]
        sources = [
            [1, 2, 3],
            [1, 2, 3],
            [i for i in range(self.task_cnt)],
            [1, 2, 3, 4, 5],
            [4, 5, 6],
        ]
        self.submits = [
            Submit.objects.create(
                points=10, task=task, user=self.users[i], submit_type=self.submit_types['description']
            ) for i, tasks in enumerate(descriptions) for task in self.tasks
        ] + [
            Submit.objects.create(
                points=10, task=task, user=self.users[i], submit_type=self.submit_types['source']
            ) for i, tasks in enumerate(sources) for task in self.tasks
        ]

    def test_get_tasks_single_round_no_category(self):
        # test count
        tasks = views._get_tasks(str(self.rounds[0].id), None)

        # test all belong to one round
        self.assertEqual(len(tasks), self.task_cnt)
        for t in tasks:
            self.assertEqual(t.round, self.rounds[0])

        # test sorted
        last = None
        for t in tasks:
            if last is not None:
                self.assertLess(last.number, t.number)
            last = t

    def test_get_tasks_single_round_one_category(self):
        # test count
        tasks = views._get_tasks(str(self.rounds[0].id), str(self.categories['z'].id))

        # test all belong to one round
        self.assertEqual(len(tasks), self.task_cnt)
        for t in tasks:
            self.assertEqual(t.round, self.rounds[0])

        # test sorted
        last = None
        for t in tasks:
            if last is not None:
                self.assertLess(last.number, t.number)
            last = t

    def test_get_tasks_single_round_multi_category(self):
        # test count
        tasks = views._get_tasks(str(self.rounds[0].id), '%d,%d' % (self.categories['z'].id, self.categories['o'].id))

        # test all belong to one round
        self.assertEqual(len(tasks), self.task_cnt)
        for t in tasks:
            self.assertEqual(t.round, self.rounds[0])

        # test sorted
        last = None
        for t in tasks:
            if last is not None:
                self.assertLess(last.number, t.number)
            last = t

    def test_get_tasks_multi_round_no_category(self):
        # test count
        tasks = views._get_tasks('%s,%s' % (self.rounds[0].id, self.rounds[1].id), None)

        # test sorted
        last = None
        for t in tasks:
            if last is not None:
                if last.round == t.round:
                    self.assertLess(last.number, t.number)
            last = t

    def test_get_tasks_multi_round_one_category(self):
        # test count
        tasks = views._get_tasks('%s,%s' % (self.rounds[0].id, self.rounds[1].id), str(self.categories['z'].id))

        # test sorted
        last = None
        for t in tasks:
            if last is not None:
                if last.round == t.round:
                    self.assertLess(last.number, t.number)
            last = t

    def test_get_tasks_multi_round_multi_category(self):
        # test count
        tasks = views._get_tasks(
            '%s,%s' % (self.rounds[0].id, self.rounds[1].id),
            '%d,%d' % (self.categories['z'].id, self.categories['o'].id),
        )

        # test sorted
        last = None
        for t in tasks:
            if last is not None:
                if last.round == t.round:
                    self.assertLess(last.number, t.number)
            last = t

    def test_response(self):
        client = Client(HTTP_HOST='ksp.sk')
        response = client.get(reverse('view_results', kwargs={'round_ids': '%s' % self.rounds[0].id}))
        self.assertEqual(response.status_code, 200)

        response = client.get(
            reverse('view_results', kwargs={'round_ids': '%s,%s' % (self.rounds[0].id, self.rounds[1].id)})
        )
        self.assertEqual(response.status_code, 200)

        response = client.get(
            reverse(
                'view_results',
                kwargs={'round_ids': '%s' % self.rounds[0].id, 'category_ids': '%s' % self.categories['z'].id},
            )
        )
        self.assertEqual(response.status_code, 200)

        response = client.get(
            reverse(
                'view_results',
                kwargs={
                    'round_ids': '%s,%s' % (self.rounds[0].id, self.rounds[1].id),
                    'category_ids': '%s' % self.categories['o'].id,
                },
            )
        )
        self.assertEqual(response.status_code, 200)

        response = client.get(
            reverse(
                'view_results',
                kwargs={
                    'round_ids': '%s' % self.rounds[0].id,
                    'category_ids': '%s,%s' % (self.categories['z'].id, self.categories['o'].id),
                },
            )
        )
        self.assertEqual(response.status_code, 200)

        response = client.get(
            reverse(
                'view_results',
                kwargs={
                    'round_ids': '%s,%s' % (self.rounds[0].id, self.rounds[1].id),
                    'category_ids': '%s,%s' % (self.categories['z'].id, self.categories['o'].id),
                },
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_get_submits_single_task(self):
        task = Task.objects.create(number=47, round=self.rounds[0], name='', description_points=10, source_points=10)
        task.task_types.add(self.submit_types['source'])
        submit_cnt = 10
        submits = [
            Submit.objects.create(
                points=10, task=task, user=self.users[0], submit_type=self.submit_types['source']
            ) for _ in range(submit_cnt)
        ]
        task_submits = views._get_submits([task])
        self.assertEqual(len(task_submits), 1)
        self.assertEqual(task_submits[0], submits[-1])

        task = Task.objects.create(number=42, round=self.rounds[0], name='', description_points=10, source_points=10)
        task.task_types.add(self.submit_types['description'])
        submit_cnt = 10
        submits = [
            Submit.objects.create(
                points=10, task=task, user=self.users[0], submit_type=self.submit_types['source']
            ) for _ in range(submit_cnt)
        ]
        task_submits = views._get_submits([task])
        self.assertEqual(len(task_submits), 1)
        self.assertEqual(task_submits[0], submits[-1])

    def test_results_single_round(self):
        pass

    def test_results_multi_round(self):
        pass
