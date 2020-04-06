from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from ..experiments.models import Experiment, ExperimentChallenge
from .models import Question, QuestionAnswer, Stage


class StageModelTestCase(TestCase):

    def test_str(self):
        stage = Stage.objects.create(
            stage_number=1,
        )
        str(stage)


class QuestionModelTestCase(TestCase):

    def test_str(self):
        stage = Stage.objects.create(
            stage_number=1,
        )
        question = Question.objects.create(
            stage=stage,
            question='Question'
        )
        str(question)


class QuestionAnswerModelTestCase(TestCase):

    def test_str(self):
        stage = Stage.objects.create(
            stage_number=1,
        )
        experiment = Experiment.objects.create()
        question = Question.objects.create(
            stage=stage,
            question='Question'
        )
        question_answer = QuestionAnswer.objects.create(
            experiment=experiment,
            question=question,
        )
        str(question_answer)


class StageAPITestCase(APITestCase):
    maxDiff = None

    def setUp(self):
        self.stage = Stage.objects.create(
            description='Lorem ipsum',
            name='First phase',
            stage_number=1,
        )

    def test_stage_list(self):
        expected_response_body = [{
            'description': 'Lorem ipsum',
            'name': 'First phase',
            'stage_number': 1,
        }]
        url = reverse('stage-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_response_body)

    def test_stage_retrieve(self):
        expected_response_body = {
            'description': 'Lorem ipsum',
            'name': 'First phase',
            'stage_number': 1,
        }
        url = reverse('stage-detail', kwargs={'pk': self.stage.stage_number})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_response_body)


class QuestionAPITestCase(APITestCase):
    maxDiff = None

    def setUp(self):
        self.user = get_user_model().objects.create(
            first_name='John',
            last_name='Doe'
        )
        self.stage = Stage.objects.create(
            name='First phase',
            stage_number=1,
        )
        self.experiment_challenge = ExperimentChallenge.objects.create()
        self.question = Question.objects.create(
            description='Description',
            experiment_challenge=None,
            question='Question 1',
            stage=self.stage,
        )
        self.question_with_experiment_challenge = Question.objects.create(
            experiment_challenge=self.experiment_challenge,
            question='Question 2',
            stage=self.stage,
        )

    def test_question_list(self):
        expected_response_body = [{
            'id': self.question.id,
            'description': 'Description',
            'experiment_challenge_id': None,
            'is_public': True,
            'question': 'Question 1',
        }, {
            'id': self.question_with_experiment_challenge.id,
            'description': '',
            'experiment_challenge_id': self.experiment_challenge.id,
            'is_public': True,
            'question': 'Question 2',
        }]
        url = reverse('question-list', kwargs={
            'stage_id': self.stage.stage_number
        })
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_response_body)

    def test_question_list_denied_for_not_authenticated(self):
        url = reverse('question-list', kwargs={
            'stage_id': self.stage.stage_number
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_question_list_filtering_with_experiment_challenge_id(self):
        expected_response_body = [{
            'id': self.question_with_experiment_challenge.id,
            'description': '',
            'experiment_challenge_id': self.experiment_challenge.id,
            'is_public': True,
            'question': 'Question 2',
        }]
        url = '{}?experiment_challenge_id={}'.format(
            reverse('question-list', kwargs={
                'stage_id': self.stage.stage_number
            }),
            self.experiment_challenge.id
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_response_body)

    def test_question_list_filtering_with_experiment_challenge_id_as_null(self):
        expected_response_body = [{
            'id': self.question.id,
            'description': 'Description',
            'experiment_challenge_id': None,
            'is_public': True,
            'question': 'Question 1',
        }]
        url = '{}?experiment_challenge_id__isnull=true'.format(
            reverse('question-list', kwargs={
                'stage_id': self.stage.stage_number
            })
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_response_body)

    def test_question_retrieve(self):
        expected_response_body = {
            'id': self.question.id,
            'description': 'Description',
            'experiment_challenge_id': None,
            'is_public': True,
            'question': 'Question 1',
        }
        url = reverse('question-detail', kwargs={
            'pk': self.question.id,
            'stage_id': self.stage.stage_number
        })
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_response_body)

    def test_question_retrieve_denied_for_not_authenticated(self):
        url = reverse('question-detail', kwargs={
            'pk': self.question.id,
            'stage_id': self.stage.stage_number
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_question_retrieve_not_found_for_another_stage(self):
        stage_2 = Stage.objects.create(
            name='First phase',
            stage_number=2,
        )
        url = reverse('question-detail', kwargs={
            'pk': self.question.id,
            'stage_id': stage_2.stage_number
        })
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
