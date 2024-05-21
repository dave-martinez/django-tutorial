import datetime

from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from .models import Question


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


def create_user(username, password):
    user = get_user_model().objects.create(username=username)
    user.set_password(password)
    user.save()
    EmailAddress.objects.create(
        user=user,
        email=f"{username}@example.org",
        primary=True,
        verified=True,
    )


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """

        create_user('foo', 'bar')
        self.client.post(
            reverse("account_login"),
            {"login": "foo", "password": "bar"},
        )

        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        create_user('foo', 'bar')
        self.client.post(
            reverse("account_login"),
            {"login": "foo", "password": "bar"},
        )

        q = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [q]
        )


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        create_user('foo', 'bar')
        self.client.post(
            reverse("account_login"),
            {"login": "foo", "password": "bar"},
        )
        future_question = create_question(
            question_text="Future question.", days=5)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        create_user('foo', 'bar')
        self.client.post(
            reverse("account_login"),
            {"login": "foo", "password": "bar"},
        )
        past_question = create_question(
            question_text="Past Question.", days=-5)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
