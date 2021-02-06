from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from trojsten.contests.constants import TASK_ROLE_REVIEWER
from trojsten.contests.models import Competition, Round, Semester, Task, TaskPeople
from trojsten.events.models import Event, EventParticipant, EventPlace, EventType
from trojsten.people.models import User
from trojsten.submit.constants import (
    SUBMIT_STATUS_IN_QUEUE,
    SUBMIT_STATUS_REVIEWED,
    SUBMIT_TYPE_DESCRIPTION,
)
from trojsten.submit.models import Submit


class TestTop30(TestCase):
    def setUp(self):
        self.site = Site.objects.get(pk=settings.SITE_ID)
        grad_year = timezone.now().year + 1
        self.users = [
            User.objects.create_user(
                username="jozko",
                first_name="Jozko",
                last_name="Mrkvicka",
                password="pass",
                graduation=grad_year,
            ),
            User.objects.create_user(
                username="janko",
                first_name="Janko",
                last_name="Hrasko",
                password="pass",
                graduation=grad_year,
            ),
            User.objects.create_user(
                username="veduci",
                first_name="Veduci",
                last_name="Zodpovedny",
                password="pass",
                graduation=2010,
            ),
            User.objects.create_user(
                username="marienka",
                first_name="Marienka",
                last_name="Mala",
                password="pass",
                graduation=2010,
            ),
        ]
        self.group = Group.objects.create(name="staff")
        self.group.user_set.add(self.users[2])
        self.group.user_set.add(self.users[3])
        self.users[2].groups.add(self.group)
        self.users[3].groups.add(self.group)
        competition = Competition.objects.create(
            name="TestCompetition", organizers_group=self.group
        )
        competition.sites.add(self.site)
        self.start_time_old = timezone.now() + timezone.timedelta(-10)
        self.start_time_new = timezone.now() + timezone.timedelta(5)
        self.end_time_old = timezone.now() + timezone.timedelta(-5)
        self.end_time_new = timezone.now() + timezone.timedelta(10)
        semester = Semester.objects.create(
            number=1, name="Test semester", competition=competition, year=1
        )
        round = Round.objects.create(
            number=1,
            semester=semester,
            visible=True,
            solutions_visible=False,
            start_time=self.start_time_old,
            end_time=self.end_time_old,
        )
        self.task1 = Task.objects.create(
            number=1, name="Test task", round=round, has_description=True
        )
        self.task2 = Task.objects.create(
            number=1, name="Test task", round=round, has_description=True
        )
        self.url = reverse("view_leaderboard")

    def test_most_submits_reviewed(self):
        Submit.objects.create(
            task=self.task1,
            user=self.users[0],
            submit_type=SUBMIT_TYPE_DESCRIPTION,
            points=0,
            testing_status=SUBMIT_STATUS_REVIEWED,
        )
        Submit.objects.create(
            task=self.task1,
            user=self.users[1],
            submit_type=SUBMIT_TYPE_DESCRIPTION,
            points=0,
            testing_status=SUBMIT_STATUS_REVIEWED,
        )
        Submit.objects.create(
            task=self.task1,
            user=self.users[1],
            submit_type=SUBMIT_TYPE_DESCRIPTION,
            points=0,
            testing_status=SUBMIT_STATUS_IN_QUEUE,
        )
        Submit.objects.create(
            task=self.task2,
            user=self.users[0],
            submit_type=SUBMIT_TYPE_DESCRIPTION,
            points=0,
            testing_status=SUBMIT_STATUS_REVIEWED,
        )
        TaskPeople.objects.create(task=self.task1, user=self.users[2], role=TASK_ROLE_REVIEWER)
        TaskPeople.objects.create(task=self.task2, user=self.users[2], role=TASK_ROLE_REVIEWER)
        TaskPeople.objects.create(task=self.task2, user=self.users[3], role=TASK_ROLE_REVIEWER)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        leaderboards = [leaderboard for name, leaderboard in response.context["leaderboards"]]
        self.assertIn(
            [(2.5, self.users[2].get_full_name()), (0.5, self.users[3].get_full_name())],
            leaderboards,
        )

    def _create_camps(self):
        place = EventPlace.objects.create(name="Camp place")
        type_camp = EventType.objects.create(name="Camp", organizers_group=self.group, is_camp=True)
        type_camp.sites.add(self.site)
        type_other = EventType.objects.create(
            name="Camp", organizers_group=self.group, is_camp=True
        )
        camp1 = Event.objects.create(
            name="Camp event1",
            type=type_camp,
            place=place,
            start_time=self.start_time_old,
            end_time=self.end_time_old,
        )
        camp2 = Event.objects.create(
            name="Camp event2",
            type=type_camp,
            place=place,
            start_time=self.start_time_old,
            end_time=self.end_time_old,
        )
        camp_other = Event.objects.create(
            name="Camp event2",
            type=type_other,
            place=place,
            start_time=self.start_time_old,
            end_time=self.end_time_old,
        )
        return camp1, camp2, camp_other

    def test_most_camps_attended(self):
        camp1, camp2, camp_other = self._create_camps()
        EventParticipant.objects.create(
            event=camp1, user=self.users[0], going=True, type=EventParticipant.PARTICIPANT
        )
        EventParticipant.objects.create(
            event=camp2, user=self.users[0], going=True, type=EventParticipant.RESERVE
        )
        EventParticipant.objects.create(
            event=camp1, user=self.users[1], going=True, type=EventParticipant.PARTICIPANT
        )
        EventParticipant.objects.create(
            event=camp2, user=self.users[1], going=False, type=EventParticipant.PARTICIPANT
        )
        EventParticipant.objects.create(
            event=camp_other, user=self.users[1], going=True, type=EventParticipant.PARTICIPANT
        )
        EventParticipant.objects.create(
            event=camp1, user=self.users[2], going=True, type=EventParticipant.ORGANIZER
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        leaderboards = [leaderboard for name, leaderboard in response.context["leaderboards"]]
        self.assertIn(
            [(2, self.users[0].get_full_name()), (1, self.users[1].get_full_name())], leaderboards
        )

    def test_most_camps_organized(self):
        camp1, camp2, camp_other = self._create_camps()
        EventParticipant.objects.create(
            event=camp1, user=self.users[0], going=True, type=EventParticipant.PARTICIPANT
        )
        EventParticipant.objects.create(
            event=camp1, user=self.users[3], going=True, type=EventParticipant.ORGANIZER
        )
        EventParticipant.objects.create(
            event=camp2, user=self.users[3], going=True, type=EventParticipant.ORGANIZER
        )
        EventParticipant.objects.create(
            event=camp1, user=self.users[2], going=True, type=EventParticipant.ORGANIZER
        )
        EventParticipant.objects.create(
            event=camp_other, user=self.users[2], going=True, type=EventParticipant.ORGANIZER
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        leaderboards = [leaderboard for name, leaderboard in response.context["leaderboards"]]
        self.assertIn(
            [(2, self.users[3].get_full_name()), (1, self.users[2].get_full_name())], leaderboards
        )
