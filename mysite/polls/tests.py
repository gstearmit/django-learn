import datetime

from django.utils import timezone
from django.test import TestCase
from django.urls import reverse

from .models import Question, Choice


def create_question(question_text, days, choices=1):
    """
    Creates a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published)
    in the past, positive for question that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    question = Question.objects.create(question_text=question_text, pub_date=time)
    for x in range(0, choices):
        create_choice('Choice {}.'.format(x), question)
    return question

def create_choice(choice_text, question):
    """
    Add a choice to `question`
    """
    choice = Choice(choice_text=choice_text, question=question)
    choice.save()
    return choice


class QuestionViewTests(TestCase):
    def test_index_view_with_no_questions(self):
        """
        If no questions exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_with_a_past_question(self):
        """
        Questions with a pub_date in the past should be displayed on the
        index page.
        """
        create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_index_view_with_a_future_question(self):
        """
        Questions with a pub_date in the future should not be displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.",
                            status_code=200)
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        should be displayed.
        """
        create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_index_view_with_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        create_question(question_text="Past question 1.", days=-30)
        create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )


class QuestionMethodTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() should return False for questions whose
        pub_date is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)

        self.assertEqual(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() should return False for questions whose
        pub_date is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=30)
        old_question = Question(pub_date=time)
        self.assertEqual(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() should return True for questions whose
        pub_date is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=1)
        recent_question = Question(pub_date=time)
        self.assertEqual(recent_question.was_published_recently(), True)


class QuestionDetailTests(TestCase):
    def test_detail_view_with_a_future_question(self):
        """
        The detail view of a question with a pub_date in the future should
        return a 404 not found.
        """
        future_question = create_question(question_text='Future question.',
                                          days=5)
        response = self.client.get(reverse('polls:detail',
                                   args=(future_question.id,)))
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_question(self):
        """
        The detail view of a question with a pub_date in the past should
        display the question's text.
        """
        past_question = create_question(question_text='Past question.',
                                        days=-5)
        response = self.client.get(reverse('polls:detail',
                                   args=(past_question.id,)))
        self.assertContains(response, past_question.question_text,
                            status_code=200)

    def test_detail_view_with_a_question_without_choices(self):
        """
        The detail view of a question without choices should return a 404
        not found.
        """
        question_without_choices = create_question(
            question_text='Question without choices.', days=0, choices=0)
        response = self.client.get(reverse('polls:detail',
                                   args=(question_without_choices.id,)))
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_question_with_choices(self):
        """
        The detail view of a question without choices should display the
        question's text.
        """
        question_with_choices = create_question(
            question_text='Question with choices.', days=0)
        response = self.client.get(reverse('polls:detail',
                                   args=(question_with_choices.id,)))
        self.assertContains(response, question_with_choices.question_text,
                            status_code=200)


class QuestionResultsTests(TestCase):
    def test_results_view_with_a_future_question(self):
        """
        The results view of a question with a pub_date in the future should
        return a 404 not found.
        """
        future_question = create_question(question_text='Future question.',
                                          days=5)
        response = self.client.get(reverse('polls:results',
                                   args=(future_question.id,)))
        self.assertEqual(response.status_code, 404)

    def test_results_view_with_a_past_question(self):
        """
        The results view of a question with a pub_date in the past should
        display the question's text.
        """
        past_question = create_question(question_text='Past question.',
                                        days=-5)
        response = self.client.get(reverse('polls:results',
                                   args=(past_question.id,)))
        self.assertContains(response, past_question.question_text,
                            status_code=200)

    def test_results_view_with_a_question_without_choices(self):
        """
        The results view of a question without choices should return a 404
        not found.
        """
        question_without_choices = create_question(
            question_text='Question without choices.', days=0, choices=0)
        response = self.client.get(reverse('polls:results',
                                   args=(question_without_choices.id,)))
        self.assertEqual(response.status_code, 404)

    def test_results_view_with_a_question_with_choices(self):
        """
        The results view of a question without choices should display the
        question's text.
        """
        question_with_choices = create_question(
            question_text='Question with choices.', days=0)
        response = self.client.get(reverse('polls:results',
                                   args=(question_with_choices.id,)))
        self.assertContains(response, question_with_choices.question_text,
                            status_code=200)


class QuestionVoteTests(TestCase):
    def test_vote_method_without_select_choice(self):
        """
        If no choice was selected, an appropriate message should be displayed.
        """
        question = create_question(question_text="A question.", days=-30)
        response = self.client.get(reverse('polls:vote',
                                   args=(question.id,)))
        self.assertIsNotNone(response.context['error_message'])

    def test_vote_method(self):
        """
        The vote method should increase `votes` of a selected choice and
        return a redirect.
        """
        question = create_question(question_text="A question.", days=-30)
        choice = question.choice_set.get(pk=1)
        response = self.client.post(reverse('polls:vote',
                                   args=(question.id,)),
                                   data={'choice':choice.id})
        self.assertGreater(question.choice_set.get(pk=1).votes, choice.votes)
        self.assertRedirects(response,
                             expected_url=reverse('polls:results',
                                                  args=(question.id,)))
