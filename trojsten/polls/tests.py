from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from trojsten.people.models import User

from .models import Answer, Question, Vote


class PollTest(TestCase):
    def setUp(self):
        self.list_url = reverse("view_question")
        self.non_staff_user = User.objects.create_user(
            username="jozko",
            first_name="Jozko",
            last_name="Mrkvicka",
            password="pass",
            graduation=2100,
        )
        self.start_time_old = timezone.now() + timezone.timedelta(-10)
        self.end_time_old = timezone.now() + timezone.timedelta(-5)
        self.end_time_new = timezone.now() + timezone.timedelta(10)

    def test_no_question(self):
        response = self.client.get(self.list_url)
        self.assertContains(response, "Neexistujú žiadne ankety")
        self.client.force_login(self.non_staff_user)

        response = self.client.get(self.list_url)
        self.assertContains(response, "Neexistujú žiadne ankety")

    def test_expired_question(self):
        question = Question.objects.create(
            created_date=self.start_time_old, deadline=self.end_time_old, text="Kto si?"
        )
        Answer.objects.create(text="Clovek", question=question)
        Answer.objects.create(text="Robot", question=question)
        response = self.client.get(self.list_url)
        self.assertContains(response, "V tejto ankete už nie je možné hlasovať.")

        self.client.force_login(self.non_staff_user)
        response = self.client.get(self.list_url)
        self.assertContains(response, "V tejto ankete už nie je možné hlasovať.")

    def test_available_question(self):
        question = Question.objects.create(
            created_date=self.start_time_old, deadline=self.end_time_new, text="Kto si?"
        )
        answer = Answer.objects.create(text="Clovek", question=question)
        Answer.objects.create(text="Robot", question=question)
        response = self.client.get(self.list_url)
        self.assertContains(response, "Na hlasovanie sa musíš prihlásiť")
        self.assertContains(response, "Clovek")
        self.assertContains(response, "Robot")
        self.assertNotContains(response, "vote" + str(answer.pk))

        self.client.force_login(self.non_staff_user)
        response = self.client.get(self.list_url)
        self.assertNotContains(response, "Na hlasovanie sa musíš prihlásiť")
        self.assertContains(response, "Clovek")
        self.assertContains(response, "Robot")
        self.assertContains(response, "vote" + str(answer.pk))

    def test_voting(self):
        question = Question.objects.create(
            created_date=self.start_time_old, deadline=self.end_time_new, text="Kto si?"
        )
        human = Answer.objects.create(text="Clovek", question=question)
        robot = Answer.objects.create(text="Robot", question=question)
        count1 = 13
        count2 = 18
        for i in range(count1):
            user = User.objects.create_user(
                username="jozko" + str(i),
                first_name="Jozko",
                last_name="Mrkvicka",
                password="pass",
                graduation=2100,
            )
            Vote.objects.create(user=user, answer=human)
        for i in range(count2):
            user = User.objects.create_user(
                username="jozko" + str(i + 100),
                first_name="Jozko",
                last_name="Mrkvicka",
                password="pass",
                graduation=2100,
            )
            Vote.objects.create(user=user, answer=robot)
        response = self.client.get(self.list_url)
        self.assertContains(response, str(count1))
        self.assertContains(response, str(count2))

        self.client.force_login(self.non_staff_user)
        response = self.client.get(self.list_url)
        self.assertContains(response, str(count1))
        self.assertContains(response, str(count2))

        question2 = Question.objects.create(
            created_date=self.start_time_old, deadline=self.end_time_new, text="2+2?"
        )
        answer2 = Answer.objects.create(text="4", question=question2)
        Vote.objects.create(user=user, answer=answer2)
