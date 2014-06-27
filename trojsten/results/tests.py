from django.test import TestCase
from trojsten.regal.tasks.models import Submit, Task
from trojsten.regal.people.models import Person, Address
from trojsten.regal.contests.models import Competition, Series, Round
from django.contrib.auth.models import User
import datetime


class ResultsTestCase(TestCase):
    def setUp(self):
        # create empty address
        self.address = Address.objects.create(street='test', town='test', number=10, postal_code='00000', country='test')
        # create users and persons
        usernames = [str(i) for i in range(10)]
        self.users = [User.objects.create(username=username) for username in usernames]
        self.persons = [Person.objects.create(user=user, birth_date=datetime.date.today()) for user in self.users]
        # create series
        self.competition = Competition.objects.create(name='test')
        self.series = Series.objects.create(competition=self.competition, name='test', number=1, year=1)
        # create rounds
        round_names = ['1', '2']
        self.rounds = [Round.objects.create(number=i, series=self.series, end_time=datetime.date.today(), visible=True) for i in round_names]
        # create tasks
        task_cnt = 5
        self.tasks = [Task.objects.create(number=i, round=round, name=str(i), task_type='source,description', description_points=10, source_points=10) for i in range(task_cnt) for round in self.rounds]
        # create submits
        descriptions = [
            [1,2,3],
            [1,2,3],
            [i for i in range(task_cnt)],
            [1,2,3,4,5],
            [4,5,6],
        ]
        sources = [
            [1,2,3],
            [1,2,3],
            [i for i in range(task_cnt)],
            [1,2,3,4,5],
            [4,5,6],
        ]
        self.submits = [
                Submit.objects.create(points=10, task=task, person=self.persons[i], submit_type='description') for i, tasks in enumerate(descriptions) for task in self.tasks
            ] + [
                Submit.objects.create(points=10, task=task, person=self.persons[i], submit_type='source') for i, tasks in enumerate(sources) for task in self.tasks
        ]


    def test_results_single_round(self):
        pass

    def test_results_multi_round(self):
        pass
