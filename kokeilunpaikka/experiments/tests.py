import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase

from ..stages.models import Question, QuestionAnswer, Stage
from ..themes.models import Theme
from .models import (
    Experiment,
    ExperimentChallenge,
    ExperimentChallengeMembership,
    ExperimentChallengeTimelineEntry,
    ExperimentExternalLink,
    ExperimentLookingForOption,
    ExperimentPost,
    ExperimentPostComment
)


class ExperimentExternalLinkModelTestCase(TestCase):

    def test_str(self):
        stage = Stage.objects.create(stage_number=1)
        experiment = Experiment.objects.create(stage=stage)
        looking_for_option = ExperimentExternalLink.objects.create(
            url='www.example.com',
            experiment=experiment,
        )
        str(looking_for_option)


class ExperimentLookingForOptionModelTestCase(TestCase):

    def test_str(self):
        looking_for_option = ExperimentLookingForOption.objects.create(
            value='Funding'
        )
        str(looking_for_option)


class ExperimentChallengeModelTestCase(TestCase):

    def test_str(self):
        experiment_challenge = ExperimentChallenge.objects.create(
            name='Challenge',
            slug='challenge'
        )
        str(experiment_challenge)


class ExperimentPostModelTestCase(TestCase):

    def test_str(self):
        stage = Stage.objects.create(stage_number=1)
        experiment = Experiment.objects.create(stage=stage)
        experiment_post = ExperimentPost.objects.create(experiment=experiment)
        str(experiment_post)


class ExperimentPostCommentModelTestCase(TestCase):

    def test_str(self):
        stage = Stage.objects.create(stage_number=1)
        experiment = Experiment.objects.create(stage=stage)
        experiment_post = ExperimentPost.objects.create(experiment=experiment)
        experiment_post_comment = ExperimentPostComment.objects.create(
            experiment_post=experiment_post,
        )
        str(experiment_post_comment)


@freeze_time('2019-07-10 12:00:00')
class ExperimentModelTestCase(TestCase):

    def setUp(self):
        self.stage = Stage.objects.create(
            stage_number=1,
        )

    def test_str(self):
        experiment = Experiment.objects.create(
            stage=self.stage,
        )
        str(experiment)

    def test_created_published_experiment_has_published_at_timestamp(self):
        experiment = Experiment.objects.create(
            is_published=True,
            stage=self.stage,
        )
        self.assertEqual(
            experiment.published_at,
            datetime.datetime(2019, 7, 10, 12, 00, tzinfo=timezone.utc)
        )

    def test_unpublished_experiment_has_no_published_at_timestamp(self):
        experiment = Experiment.objects.create(
            is_published=False,
            stage=self.stage,
        )
        self.assertEqual(experiment.published_at, None)

    def test_unpublished_experiment_gets_published_at_timestamp_after_publishing(self):
        experiment = Experiment.objects.create(
            is_published=False,
            stage=self.stage,
        )
        self.assertEqual(experiment.published_at, None)
        experiment.is_published = True
        experiment.save()
        self.assertEqual(
            experiment.published_at,
            datetime.datetime(2019, 7, 10, 12, 00, tzinfo=timezone.utc)
        )

    def test_auto_slug_field(self):
        experiment_1 = Experiment.objects.create(
            stage=self.stage,
            name='Example Experiment'
        )
        experiment_2 = Experiment.objects.create(
            stage=self.stage,
            name='Example Experiment'
        )
        self.assertEqual(experiment_1.slug, 'example-experiment')
        self.assertEqual(experiment_2.slug, 'example-experiment-2')


@freeze_time('2019-07-10 12:00:00')
class ExperimentAPITestCase(APITestCase):
    maxDiff = None

    def setUp(self):
        self.owner = get_user_model().objects.create(
            first_name='John',
            last_name='Doe',
            username='owner',
        )
        self.non_owner = get_user_model().objects.create(
            username='non-owner',
        )
        self.first_stage = Stage.objects.create(
            stage_number=1,
            name='First stage',
        )
        self.second_stage = Stage.objects.create(
            stage_number=2,
            name='Second stage',
        )
        self.experiment_challenge = ExperimentChallenge.objects.create(
            name='Challenge',
            slug='challenge'
        )
        self.theme = Theme.objects.create(
            name='Theme',
        )
        self.experiment = Experiment.objects.create(
            description='Lorem ipsum',
            is_published=True,
            name='Example Experiment',
            organizer='Company Oy',
        )
        ExperimentChallengeMembership.objects.create(
            experiment=self.experiment,
            experiment_challenge=self.experiment_challenge,
            is_approved=True,
        )
        self.experiment.responsible_users.add(
            self.owner
        )
        self.experiment.themes.add(
            self.theme
        )
        self.looking_for_option = ExperimentLookingForOption.objects.create(
            value='Funding'
        )
        self.experiment_post = ExperimentPost.objects.create(
            content='Lorem ipsum.',
            created_by=self.owner,
            experiment=self.experiment,
            title='New post'
        )
        self.experiment_post_comment = ExperimentPostComment.objects.create(
            content='Comment content.',
            created_by=self.owner,
            experiment_post=self.experiment_post,
        )

    def test_experiment_list(self):
        expected_response_body = [{
            'id': self.experiment.id,
            'image_url': '',
            'is_published': True,
            'name': 'Example Experiment',
            'published_at': '2019-07-10T12:00:00Z',
            'short_description': 'Lorem ipsum',
            'slug': 'example-experiment',
            'stage': {
                'description': '',
                'name': 'First stage',
                'stage_number': self.first_stage.stage_number,
            },
        }]
        url = reverse('experiment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_response_body)

    def test_experiment_list_with_pagination(self):
        url = '{}?page_size=1'.format(reverse('experiment-list'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['results']), 1)

    def test_experiment_list_search_by_name_matches(self):
        url = '{}?search=Example'.format(reverse('experiment-list'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_experiment_list_search_by_name_when_no_match(self):
        url = '{}?search=Lorem'.format(reverse('experiment-list'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 0)

    def test_experiment_list_filter_by_theme_matches(self):
        url = '{}?theme_ids={}'.format(reverse('experiment-list'), self.theme.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_experiment_list_filter_by_theme_when_no_match(self):
        url = '{}?theme_ids=999'.format(reverse('experiment-list'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('theme_ids', response.data)

    def test_experiment_list_filter_by_stage_matches(self):
        url = '{}?stage_id={}'.format(reverse('experiment-list'), self.first_stage.stage_number)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_experiment_list_filter_by_stage_when_no_match(self):
        url = '{}?stage_id=999'.format(reverse('experiment-list'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('stage_id', response.data)

    def test_experiment_create(self):
        request_body = {
            'description': 'Lorem ipsum',
            'experiment_challenge_ids': [
                self.experiment_challenge.id
            ],
            'looking_for_ids': [
                self.looking_for_option.id
            ],
            'name': 'Test Experiment',
            'organizer': 'Company Oy',
            'theme_ids': [
                self.theme.id
            ]
        }
        url = reverse('experiment-list')
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(url, request_body)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected_response_body = {
            'description': 'Lorem ipsum',
            'experiment_challenges': [{
                'id': self.experiment_challenge.id,
                'ends_at': None,
                'name': 'Challenge',
                'slug': 'challenge',
                'starts_at': None
            }],
            'id': response.json()['id'],
            'image_url': '',
            'is_published': False,
            'looking_for': [{
                'id': self.looking_for_option.id,
                'value': 'Funding'
            }],
            'name': 'Test Experiment',
            'organizer': 'Company Oy',
            'posts': [],
            'published_at': None,
            'question_answers': [],
            'responsible_users': [{
                'id': self.owner.id,
                'full_name': 'John Doe',
                'image_url': ''
            }],
            'slug': 'test-experiment',
            'stage': {
                'description': '',
                'name': 'First stage',
                'stage_number': self.first_stage.stage_number
            },
            'themes': [{
                'id': self.theme.id,
                'is_curated': False,
                'name': 'Theme'
            }]
        }
        self.assertEqual(response.json(), expected_response_body)
        self.assertEqual(
            Experiment.objects.get(pk=response.json()['id']).looking_for.count(),
            1
        )

    def test_experiment_create_current_user_is_automatically_set_as_responsible(self):
        request_body = {
            'description': 'Lorem ipsum',
            'experiment_challenge_ids': [
                self.experiment_challenge.id
            ],
            'name': 'Test Experiment',
            'organizer': 'Company Oy',
            'theme_ids': [
                self.theme.id
            ]
        }
        url = reverse('experiment-list')
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(url, request_body)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected_responsible_users = [{
            'id': self.owner.id,
            'full_name': 'John Doe',
            'image_url': ''
        }]
        self.assertEqual(response.json()['responsible_users'], expected_responsible_users)

    def test_experiment_create_current_user_is_owner_despite_explicitly_set_responsibles(self):
        another_owner = get_user_model().objects.create(
            username='another-owner',
        )
        request_body = {
            'description': 'Lorem ipsum',
            'experiment_challenge_ids': [
                self.experiment_challenge.id
            ],
            'name': 'Test Experiment',
            'organizer': 'Company Oy',
            'responsible_user_ids': [
                another_owner.id
            ],
            'theme_ids': [
                self.theme.id
            ]
        }
        url = reverse('experiment-list')
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(url, request_body)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected_responsible_users = [{
            'id': self.owner.id,
            'full_name': 'John Doe',
            'image_url': ''
        }, {
            'id': another_owner.id,
            'full_name': '',
            'image_url': ''
        }]
        self.assertEqual(response.json()['responsible_users'], expected_responsible_users)

    def test_experiment_create_fails_for_non_active_experiment_challenge(self):
        experiment_challenge = ExperimentChallenge.objects.create(
            starts_at=timezone.now() - datetime.timedelta(days=30),
            ends_at=timezone.now() - datetime.timedelta(days=10),
        )
        request_body = {
            'experiment_challenge_ids': [
                experiment_challenge.id
            ],
        }
        url = reverse('experiment-list')
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(url, request_body)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('experiment_challenge_ids', response.json())

    def test_experiment_create_fails_for_non_authenticated(self):
        url = reverse('experiment-list')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_experiment_create_fails_for_non_first_stage(self):
        request_body = {
            'description': 'Lorem ipsum',
            'name': 'Test Experiment',
            'stage_number': self.second_stage.stage_number
        }
        url = reverse('experiment-list')
        self.client.force_authenticate(user=self.owner)
        headers = {'HTTP_ACCEPT_LANGUAGE': 'en'}
        response = self.client.post(url, request_body, **headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json()['stage_number'][0]['message'],
            'Newly created experiment must be placed on the first stage.'
        )

    def test_experiment_looking_for_options(self):
        expected_response_body = [{
            'id': self.looking_for_option.id,
            'value': 'Funding',
        }]
        url = reverse('experiment-looking-for-options')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_response_body)

    def test_experiment_statistics(self):
        url = reverse('experiment-statistics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('active_users_count', response.data)
        self.assertIn('experiment_success_rating_average', response.data)
        self.assertIn('users_with_experiments_count', response.data)
        self.assertIn('visible_experiments_count', response.data)

    def test_experiment_retrieve(self):
        expected_response_body = {
            'description': 'Lorem ipsum',
            'experiment_challenges': [{
                'id': self.experiment_challenge.id,
                'ends_at': None,
                'name': 'Challenge',
                'slug': 'challenge',
                'starts_at': None
            }],
            'id': self.experiment.id,
            'image_url': '',
            'is_published': True,
            'looking_for': [],
            'name': 'Example Experiment',
            'organizer': 'Company Oy',
            'posts': [{
                'comments': [{
                    'content': 'Comment content.',
                    'created_at': '2019-07-10T12:00:00Z',
                    'created_by': {
                        'full_name': 'John Doe',
                        'id': self.owner.id,
                        'image_url': ''
                    },
                    'id': self.experiment_post_comment.id
                }, ],
                'content': 'Lorem ipsum.',
                'count_of_comments': 1,
                'created_at': '2019-07-10T12:00:00Z',
                'created_by': {
                    'full_name': 'John Doe',
                    'id': self.owner.id,
                    'image_url': ''
                },
                'id': self.experiment_post.id,
                'images': [],
                'title': 'New post'
            }],
            'published_at': '2019-07-10T12:00:00Z',
            'question_answers': [],
            'responsible_users': [{
                'id': self.owner.id,
                'full_name': 'John Doe',
                'image_url': ''
            }],
            'slug': 'example-experiment',
            'stage': {
                'description': '',
                'name': 'First stage',
                'stage_number': self.first_stage.stage_number
            },
            'themes': [{
                'id': self.theme.id,
                'is_curated': False,
                'name': 'Theme'
            }]
        }
        url = reverse('experiment-detail', kwargs={'slug': self.experiment.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_response_body)

    def test_experiment_retrieve_show_all_experiment_challenges(self):
        experiment = Experiment.objects.create(
            is_published=True,
            name='Experiment with one approved experiment challenge membership'
        )
        experiment_challenge_1 = ExperimentChallenge.objects.create(
            name='Experiment Challenge 1',
            slug='exp1',
        )
        experiment_challenge_2 = ExperimentChallenge.objects.create(
            name='Experiment Challenge 2',
            slug='exp2',
        )
        ExperimentChallengeMembership.objects.create(
            experiment=experiment,
            experiment_challenge=experiment_challenge_1,
            is_approved=True,
        )
        ExperimentChallengeMembership.objects.create(
            experiment=experiment,
            experiment_challenge=experiment_challenge_2,
            is_approved=False,
        )
        url = reverse('experiment-detail', kwargs={'slug': experiment.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['experiment_challenges']), 2)

    def test_experiment_retrieve_exposes_question_answers(self):
        question = Question.objects.create(
            stage=self.first_stage,
            question='Question',
        )
        question_answer = QuestionAnswer.objects.create(
            question=question,
            experiment=self.experiment,
            value='My answer',
        )
        url = reverse('experiment-detail', kwargs={'slug': self.experiment.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['question_answers'], [{
            'id': question_answer.id,
            'value': 'My answer',
            'question': 'Question',
            'question_id': question.id,
            'stage_id': self.first_stage.stage_number,
        }])

    def test_experiment_retrieve_does_not_expose_non_public_question_answers(self):
        question = Question.objects.create(
            stage=self.first_stage,
            question='Question',
            is_public=False,
        )
        QuestionAnswer.objects.create(
            question=question,
            experiment=self.experiment,
            value='My answer',
        )
        url = reverse('experiment-detail', kwargs={'slug': self.experiment.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['question_answers'], [])

    def test_experiment_retrieve_found_for_published_experiment(self):
        experiment = Experiment.objects.create(
            is_published=True,
            name='Published experiment'
        )
        url = reverse('experiment-detail', kwargs={'slug': experiment.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_experiment_retrieve_not_found_for_unpublished_experiment(self):
        experiment = Experiment.objects.create(
            is_published=False,
            name='Unpublished experiment'
        )
        url = reverse('experiment-detail', kwargs={'slug': experiment.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_experiment_retrieve_found_for_unpublished_experiment_owned_by_logged_in_user(self):
        experiment = Experiment.objects.create(
            is_published=False,
            name='Unpublished experiment'
        )
        owner = get_user_model().objects.create(
            username='asdfgh',
        )
        experiment.responsible_users.add(owner)
        url = reverse('experiment-detail', kwargs={'slug': experiment.slug})

        # Not found when not logged-in
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Found when logged-in
        self.client.force_authenticate(user=owner)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_experiment_update(self):
        request_body = {
            'description': 'Lorem ipsum',
            'experiment_challenge_ids': [
                self.experiment_challenge.id
            ],
            'name': 'Example Experiment 2',
            'responsible_user_ids': [
                self.owner.id
            ],
            'theme_ids': []
        }
        expected_response_body = {
            'description': 'Lorem ipsum',
            'experiment_challenges': [{
                'id': self.experiment_challenge.id,
                'ends_at': None,
                'name': 'Challenge',
                'slug': 'challenge',
                'starts_at': None
            }],
            'id': self.experiment.id,
            'image_url': '',
            'is_published': True,
            'looking_for': [],
            'name': 'Example Experiment 2',
            'organizer': 'Company Oy',
            'posts': [{
                'comments': [{
                    'content': 'Comment content.',
                    'created_at': '2019-07-10T12:00:00Z',
                    'created_by': {
                        'full_name': 'John Doe',
                        'id': self.owner.id,
                        'image_url': ''
                    },
                    'id': self.experiment_post_comment.id
                }],
                'content': 'Lorem ipsum.',
                'count_of_comments': 1,
                'created_at': '2019-07-10T12:00:00Z',
                'created_by': {
                    'full_name': 'John Doe',
                    'id': self.owner.id,
                    'image_url': ''
                },
                'id': self.experiment_post.id,
                'images': [],
                'title': 'New post'
            }],
            'published_at': '2019-07-10T12:00:00Z',
            'question_answers': [],
            'responsible_users': [{
                'id': self.owner.id,
                'full_name': 'John Doe',
                'image_url': ''
            }],
            'slug': 'example-experiment',
            'stage': {
                'description': '',
                'name': 'First stage',
                'stage_number': self.first_stage.stage_number
            },
            'themes': []
        }
        url = reverse('experiment-detail', kwargs={'slug': self.experiment.slug})
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(url, request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_response_body)

    def test_experiment_update_fails_for_non_authenticated(self):
        url = reverse('experiment-detail', kwargs={'slug': self.experiment.slug})
        response = self.client.put(url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_experiment_update_for_stage_number_succeeds_without_experiment_challeges(self):
        experiment_without_experiment_challeges = Experiment.objects.create(
            is_published=True,
            name='experiment_without_experiment_challeges',
        )
        experiment_without_experiment_challeges.responsible_users.add(
            self.owner
        )
        request_body = {
            'description': 'Lorem ipsum',
            'name': 'Example Experiment 2',
            'stage_number': self.second_stage.stage_number,
        }
        url = reverse('experiment-detail', kwargs={
            'slug': experiment_without_experiment_challeges.slug
        })
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(url, request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_experiment_update_for_stage_number_succeeds_with_approved_experiment_challeges(self):
        active_experiment_challenge = ExperimentChallenge.objects.create(
            description='Lorem ipsum',
            ends_at=timezone.now() + datetime.timedelta(hours=1),
            is_visible=True,
            name='Experiment Challenge',
            starts_at=timezone.now(),
        )
        experiment_with_approved_experiment_challeges = Experiment.objects.create(
            is_published=True,
            name='experiment_without_experiment_challeges',
        )
        experiment_with_approved_experiment_challeges.responsible_users.add(
            self.owner
        )
        ExperimentChallengeMembership.objects.create(
            experiment=experiment_with_approved_experiment_challeges,
            experiment_challenge=active_experiment_challenge,
            is_approved=True,
        )
        request_body = {
            'description': 'Lorem ipsum',
            'name': 'Example Experiment 2',
            'stage_number': self.second_stage.stage_number,
        }
        url = reverse('experiment-detail', kwargs={
            'slug': experiment_with_approved_experiment_challeges.slug
        })
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(url, request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_experiment_update_for_stage_number_fails_with_unapproved_experiment_challeges(self):
        first_active_experiment_challenge = ExperimentChallenge.objects.create(
            description='Lorem ipsum',
            ends_at=timezone.now() + datetime.timedelta(hours=1),
            is_visible=True,
            name='Experiment Challenge 1',
            starts_at=timezone.now(),
            slug='1',
        )
        second_active_experiment_challenge = ExperimentChallenge.objects.create(
            description='Lorem ipsum',
            ends_at=timezone.now() + datetime.timedelta(hours=1),
            is_visible=True,
            name='Experiment Challenge 2',
            starts_at=timezone.now(),
            slug='2',
        )
        experiment_with_unapproved_experiment_challeges = Experiment.objects.create(
            is_published=True,
            name='experiment_without_experiment_challeges',
        )
        experiment_with_unapproved_experiment_challeges.responsible_users.add(
            self.owner
        )
        ExperimentChallengeMembership.objects.create(
            experiment=experiment_with_unapproved_experiment_challeges,
            experiment_challenge=first_active_experiment_challenge,
            is_approved=True,
        )
        ExperimentChallengeMembership.objects.create(
            experiment=experiment_with_unapproved_experiment_challeges,
            experiment_challenge=second_active_experiment_challenge,
            is_approved=False,
        )
        request_body = {
            'description': 'Lorem ipsum',
            'name': 'Example Experiment 2',
            'stage_number': self.second_stage.stage_number,
        }
        url = reverse('experiment-detail', kwargs={
            'slug': experiment_with_unapproved_experiment_challeges.slug
        })
        self.client.force_authenticate(user=self.owner)
        headers = {'HTTP_ACCEPT_LANGUAGE': 'en'}
        response = self.client.put(url, request_body, **headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json()['stage_number'][0]['message'],
            'The experiment is not approved to all selected experiment '
            'challenges and thus cannot be moved to the next stage.'
        )

    def test_experiment_update_fails_for_non_owner(self):
        url = reverse('experiment-detail', kwargs={'slug': self.experiment.slug})
        self.client.force_authenticate(user=self.non_owner)
        response = self.client.put(url, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_experiment_update_fails_for_empty_responsible_user_ids(self):
        request_body = {
            'description': 'Lorem ipsum',
            'name': 'Example Experiment 2',
            'responsible_user_ids': [],
        }
        url = reverse('experiment-detail', kwargs={'slug': self.experiment.slug})
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(url, request_body)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('responsible_user_ids', response.json())

    def test_experiment_partial_update(self):
        request_body = {
            'stage_number': self.second_stage.stage_number,
        }
        expected_response_body = {
            'description': 'Lorem ipsum',
            'experiment_challenges': [{
                'id': self.experiment_challenge.id,
                'ends_at': None,
                'name': 'Challenge',
                'slug': 'challenge',
                'starts_at': None
            }],
            'id': self.experiment.id,
            'image_url': '',
            'is_published': True,
            'looking_for': [],
            'name': 'Example Experiment',
            'organizer': 'Company Oy',
            'posts': [{
                'comments': [{
                    'content': 'Comment content.',
                    'created_at': '2019-07-10T12:00:00Z',
                    'created_by': {
                        'full_name': 'John Doe',
                        'id': self.owner.id,
                        'image_url': ''
                    },
                    'id': self.experiment_post_comment.id
                }],
                'content': 'Lorem ipsum.',
                'count_of_comments': 1,
                'created_at': '2019-07-10T12:00:00Z',
                'created_by': {
                    'full_name': 'John Doe',
                    'id': self.owner.id,
                    'image_url': ''
                },
                'id': self.experiment_post.id,
                'images': [],
                'title': 'New post'
            }],
            'published_at': '2019-07-10T12:00:00Z',
            'question_answers': [],
            'responsible_users': [{
                'id': self.owner.id,
                'full_name': 'John Doe',
                'image_url': ''
            }],
            'slug': 'example-experiment',
            'stage': {
                'description': '',
                'name': 'Second stage',
                'stage_number': self.second_stage.stage_number
            },
            'themes': [{
                'id': self.theme.id,
                'is_curated': False,
                'name': 'Theme'
            }]
        }
        url = reverse('experiment-detail', kwargs={'slug': self.experiment.slug})
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(url, request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_response_body)

    def test_experiment_partial_update_for_success_rating(self):
        url = reverse('experiment-detail', kwargs={'slug': self.experiment.slug})
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(url, {'success_rating': 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Experiment.objects.get(pk=self.experiment.id).success_rating,
            10
        )

    def test_experiment_partial_update_fails_when_trying_to_empty_resposible_users(self):
        request_body = {
            'responsible_user_ids': [],
        }
        url = reverse('experiment-detail', kwargs={'slug': self.experiment.slug})
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(url, request_body)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('responsible_user_ids', response.json())

    def test_experiment_partial_update_fails_for_non_authenticated(self):
        url = reverse('experiment-detail', kwargs={'slug': self.experiment.slug})
        response = self.client.patch(url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_experiment_partial_update_fails_for_non_owner(self):
        url = reverse('experiment-detail', kwargs={'slug': self.experiment.slug})
        self.client.force_authenticate(user=self.non_owner)
        response = self.client.patch(url, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_experiment_partial_update_for_stage_number_succeeds_without_experiment_challeges(self):
        experiment_without_experiment_challeges = Experiment.objects.create(
            is_published=True,
            name='experiment_without_experiment_challeges',
        )
        experiment_without_experiment_challeges.responsible_users.add(
            self.owner
        )
        request_body = {
            'stage_number': self.second_stage.stage_number,
        }
        url = reverse('experiment-detail', kwargs={
            'slug': experiment_without_experiment_challeges.slug
        })
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(url, request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_experiment_partial_update_for_stage_number_succeeds_with_approved_experiment_challeges(self):  # noqa
        active_experiment_challenge = ExperimentChallenge.objects.create(
            description='Lorem ipsum',
            ends_at=timezone.now() + datetime.timedelta(hours=1),
            is_visible=True,
            name='Experiment Challenge',
            starts_at=timezone.now(),
        )
        experiment_with_approved_experiment_challeges = Experiment.objects.create(
            is_published=True,
            name='experiment_without_experiment_challeges',
        )
        experiment_with_approved_experiment_challeges.responsible_users.add(
            self.owner
        )
        ExperimentChallengeMembership.objects.create(
            experiment=experiment_with_approved_experiment_challeges,
            experiment_challenge=active_experiment_challenge,
            is_approved=True,
        )
        request_body = {
            'stage_number': self.second_stage.stage_number,
        }
        url = reverse('experiment-detail', kwargs={
            'slug': experiment_with_approved_experiment_challeges.slug
        })
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(url, request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_experiment_partial_update_for_stage_number_fails_with_unapproved_experiment_challeges(self):  # noqa
        first_active_experiment_challenge = ExperimentChallenge.objects.create(
            description='Lorem ipsum',
            ends_at=timezone.now() + datetime.timedelta(hours=1),
            is_visible=True,
            name='Experiment Challenge 1',
            starts_at=timezone.now(),
            slug='1',
        )
        second_active_experiment_challenge = ExperimentChallenge.objects.create(
            description='Lorem ipsum',
            ends_at=timezone.now() + datetime.timedelta(hours=1),
            is_visible=True,
            name='Experiment Challenge 2',
            starts_at=timezone.now(),
            slug='2',
        )
        experiment_with_unapproved_experiment_challeges = Experiment.objects.create(
            is_published=True,
            name='experiment_without_experiment_challeges',
        )
        experiment_with_unapproved_experiment_challeges.responsible_users.add(
            self.owner
        )
        ExperimentChallengeMembership.objects.create(
            experiment=experiment_with_unapproved_experiment_challeges,
            experiment_challenge=first_active_experiment_challenge,
            is_approved=True,
        )
        ExperimentChallengeMembership.objects.create(
            experiment=experiment_with_unapproved_experiment_challeges,
            experiment_challenge=second_active_experiment_challenge,
            is_approved=False,
        )
        request_body = {
            'stage_number': self.second_stage.stage_number,
        }
        url = reverse('experiment-detail', kwargs={
            'slug': experiment_with_unapproved_experiment_challeges.slug
        })
        self.client.force_authenticate(user=self.owner)
        headers = {'HTTP_ACCEPT_LANGUAGE': 'en'}
        response = self.client.patch(url, request_body, **headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json()['stage_number'][0]['message'],
            'The experiment is not approved to all selected experiment '
            'challenges and thus cannot be moved to the next stage.'
        )

    def test_experiment_destroy(self):
        url = reverse('experiment-detail', kwargs={'slug': self.experiment.slug})
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b'')

    def test_experiment_destroy_fails_for_non_authenticated(self):
        url = reverse('experiment-detail', kwargs={'slug': self.experiment.slug})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_experiment_destroy_fails_for_non_owner(self):
        url = reverse('experiment-detail', kwargs={'slug': self.experiment.slug})
        self.client.force_authenticate(user=self.non_owner)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_experiment_answer_questions(self):
        question_1 = Question.objects.create(
            stage=self.first_stage,
            question='Question 1'
        )
        question_2 = Question.objects.create(
            stage=self.first_stage,
            question='Question 2'
        )
        request_body = [{
            'question_id': question_1.id,
            'value': 'Answer 1'
        }, {
            'question_id': question_2.id,
            'value': 'Answer 2'
        }]
        url = reverse('experiment-answer-questions', kwargs={'slug': self.experiment.slug})
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(url, request_body)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(QuestionAnswer.objects.count(), 2)

    def test_experiment_answer_questions_update(self):
        question_1 = Question.objects.create(
            stage=self.first_stage,
            question='Question 1'
        )
        request_body = [{
            'question_id': question_1.id,
            'value': 'Answer 1'
        }]
        self.client.force_authenticate(user=self.owner)
        url = reverse('experiment-answer-questions', kwargs={'slug': self.experiment.slug})
        response = self.client.put(url, request_body)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(QuestionAnswer.objects.get(question_id=question_1).value, 'Answer 1')
        request_body = [{
            'question_id': question_1.id,
            'value': 'Answer 2'
        }]
        response = self.client.put(url, request_body)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(QuestionAnswer.objects.get(question_id=question_1).value, 'Answer 2')

    def test_experiment_answer_questions_fails_for_non_responsible(self):
        experiment = Experiment.objects.create(
            is_published=True,
        )
        question = Question.objects.create(
            stage=self.first_stage,
            question='Question',
        )
        request_body = [{
            'question_id': question.id,
            'value': 'Answer 1'
        }]
        url = reverse('experiment-answer-questions', kwargs={'slug': experiment.slug})
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(url, request_body)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_experiment_answer_questions_fails_for_question_for_another_experiment(self):
        experiment = Experiment.objects.create(
            is_published=True,
        )
        experiment.responsible_users.add(
            self.owner
        )
        experiment_challenge = ExperimentChallenge.objects.create(
            name='Experiment Challenge'
        )
        question = Question.objects.create(
            stage=self.first_stage,
            question='Question',
            experiment_challenge=experiment_challenge,
        )
        request_body = [{
            'question_id': question.id,
            'value': 'Answer 1'
        }]
        url = reverse('experiment-answer-questions', kwargs={'slug': experiment.slug})
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(url, request_body)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


@freeze_time('2019-07-10 12:00:00')
class ExperimentChallengeAPITestCase(APITestCase):
    maxDiff = None

    def setUp(self):
        self.owner = get_user_model().objects.create(
            username='owner',
        )
        self.first_stage = Stage.objects.create(
            stage_number=1,
            name='First stage',
        )
        self.theme = Theme.objects.create(
            name='Theme',
        )
        self.experiment_challenge = ExperimentChallenge.objects.create(
            description='Lorem ipsum',
            ends_at=timezone.now() + datetime.timedelta(hours=1),
            is_visible=True,
            lead_text='Lorem ipsum',
            name='Experiment Challenge',
            slug='experiment-challenge',
            starts_at=timezone.now(),
        )
        self.experiment_challenge.themes.add(
            self.theme
        )
        self.experiment = Experiment.objects.create(
            description='Lorem ipsum',
            is_published=True,
            name='Example Experiment',
        )
        self.experiment.experiment_challenges.add(
            self.experiment_challenge
        )
        self.experiment.responsible_users.add(
            self.owner
        )
        self.experiment.themes.add(
            self.theme
        )
        self.timeline_entry = ExperimentChallengeTimelineEntry.objects.create(
            content='Content',
            date=timezone.now(),
            experiment_challenge=self.experiment_challenge,
        )

    def test_experiment_challenge_list(self):
        expected_response_body = [{
            'id': self.experiment_challenge.id,
            'description': 'Lorem ipsum',
            'ends_at': '2019-07-10T13:00:00Z',
            'starts_at': '2019-07-10T12:00:00Z',
            'image_url': '',
            'is_active': True,
            'lead_text': 'Lorem ipsum',
            'name': 'Experiment Challenge',
            'slug': 'experiment-challenge',
            'theme_ids': [
                self.theme.id
            ]
        }]
        url = reverse('experiment-challenge-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_response_body)

    def test_experiment_challenge_list_with_pagination(self):
        url = '{}?page_size=1'.format(reverse('experiment-challenge-list'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['results']), 1)

    def test_experiment_challenge_list_search_by_name_matches(self):
        url = '{}?search=Challenge'.format(reverse('experiment-challenge-list'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_experiment_challenge_list_search_by_name_when_no_match(self):
        url = '{}?search=Lorem'.format(reverse('experiment-challenge-list'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 0)

    def test_experiment_challenge_list_filter_by_theme_matches(self):
        url = '{}?theme_ids={}'.format(reverse('experiment-challenge-list'), self.theme.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_experiment_challenge_list_filter_by_theme_when_no_match(self):
        url = '{}?theme_ids=999'.format(reverse('experiment-challenge-list'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('theme_ids', response.data)

    def test_experiment_challenge_retrieve(self):
        expected_response_body = {
            'id': self.experiment_challenge.id,
            'description': 'Lorem ipsum',
            'ends_at': '2019-07-10T13:00:00Z',
            'experiments': [{
                'image_url': '',
                'is_approved': False,
                'is_published': True,
                'name': 'Example Experiment',
                'published_at': '2019-07-10T12:00:00Z',
                'short_description': 'Lorem ipsum',
                'slug': 'example-experiment',
                'stage': {
                    'description': '',
                    'name': 'First stage',
                    'stage_number': self.first_stage.stage_number,
                }
            }],
            'starts_at': '2019-07-10T12:00:00Z',
            'image_url': '',
            'is_active': True,
            'lead_text': 'Lorem ipsum',
            'name': 'Experiment Challenge',
            'slug': 'experiment-challenge',
            'theme_ids': [
                self.theme.id
            ],
            'timeline_entries': [
                {
                    'id': self.timeline_entry.id,
                    'content': 'Content',
                    'created_at': '2019-07-10T12:00:00Z',
                    'date': '2019-07-10',
                }
            ]
        }
        url = reverse('experiment-challenge-detail', kwargs={
            'translations__slug': self.experiment_challenge.slug
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_response_body)

    def test_experiment_challenge_retrieve_not_found_for_non_visible(self):
        non_visible_experiment_challenge = ExperimentChallenge.objects.create(
            ends_at=timezone.now() + datetime.timedelta(hours=1),
            is_visible=False,
            name='Non Visible Experiment Challenge',
            slug='non-visible-experiment-challenge',
            starts_at=timezone.now(),
        )
        url = reverse('experiment-challenge-detail', kwargs={
            'translations__slug': non_visible_experiment_challenge.slug
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_experiment_challenge_retrieve_found_for_not_active_but_visible(self):
        not_active_visible_experiment_challenge = ExperimentChallenge.objects.create(
            ends_at=timezone.now() - datetime.timedelta(hours=1),
            is_visible=True,
            name='Not Active Experiment Challenge',
            slug='not-active-experiment-challenge',
            starts_at=timezone.now() - datetime.timedelta(hours=2),
        )
        url = reverse('experiment-challenge-detail', kwargs={
            'translations__slug': not_active_visible_experiment_challenge.slug
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_experiment_challenge_retrieve_doesnt_show_unpublished_experiments(self):
        experiment_challenge = ExperimentChallenge.objects.create(
            ends_at=timezone.now() + datetime.timedelta(hours=1),
            is_visible=True,
            name='Experiment Challenge 2',
            slug='experiment-challenge-2',
            starts_at=timezone.now(),
        )
        unpublished_experiment = Experiment.objects.create(
            description='Lorem ipsum',
            is_published=False,
            name='Not published experiment',
        )
        unpublished_experiment.experiment_challenges.add(
            experiment_challenge
        )
        unpublished_experiment.responsible_users.add(
            self.owner
        )

        url = reverse('experiment-challenge-detail', kwargs={
            'translations__slug': experiment_challenge.slug
        })
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['experiments']), 0)


@freeze_time('2019-07-10 12:00:00')
class ExperimentPostAPITestCase(APITestCase):
    maxDiff = None

    def setUp(self):
        # Model instances
        self.creator = get_user_model().objects.create(
            first_name='John',
            last_name='Doe',
            username='owner',
        )
        self.responsible = get_user_model().objects.create(
            username='responsible',
        )
        self.non_owner = get_user_model().objects.create(
            username='non-owner',
        )
        self.first_stage = Stage.objects.create(
            stage_number=1,
            name='First stage',
        )
        self.experiment = Experiment.objects.create(
            description='Lorem ipsum',
            is_published=True,
            name='Example Experiment',
        )
        self.experiment.responsible_users.add(
            self.creator,
            self.responsible
        )
        self.experiment_post = ExperimentPost.objects.create(
            content='Lorem ipsum.',
            created_by=self.creator,
            experiment=self.experiment,
            title='New post'
        )

        # Urls
        self.detail_url = reverse('experiment-post-detail', kwargs={
            'experiment_slug': self.experiment.slug,
            'pk': self.experiment_post.id
        })
        self.list_url = reverse('experiment-post-list', kwargs={
            'experiment_slug': self.experiment.slug
        })

    def test_experiment_post_list(self):
        expected_response_body = [{
            'id': self.experiment_post.id,
            'comments': [],
            'content': 'Lorem ipsum.',
            'count_of_comments': 0,
            'created_at': '2019-07-10T12:00:00Z',
            'created_by': {
                'id': self.creator.id,
                'full_name': 'John Doe',
                'image_url': ''
            },
            'images': [],
            'title': 'New post'
        }]
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_response_body)

    def test_experiment_post_create(self):
        request_body = {
            'content': 'Lorem ipsum.',
            'title': 'New post',
        }
        self.client.force_authenticate(user=self.creator)
        response = self.client.post(self.list_url, request_body)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected_response_body = {
            'id': response.json()['id'],
            'comments': [],
            'content': 'Lorem ipsum.',
            'count_of_comments': 0,
            'created_at': '2019-07-10T12:00:00Z',
            'created_by': {
                'id': self.creator.id,
                'full_name': 'John Doe',
                'image_url': ''
            },
            'images': [],
            'title': 'New post',
        }
        self.assertEqual(response.json(), expected_response_body)

    def test_experiment_post_create_filters_unsafe_content(self):
        request_body = {
            'content': (
                '<p>Lorem ipsum</p>'
                '<img src="http://example.com">'
                '<iframe src="http://example.com"></iframe>'
                '<script>alert("example");</script>'
                '<a onClick="alert("Hello World!");">Link</a>'
            ),
            'title': 'Post',
        }
        self.client.force_authenticate(user=self.creator)
        response = self.client.post(self.list_url, request_body)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('<p>', response.json()['content'])
        self.assertIn('<img src=', response.json()['content'])
        self.assertIn('<iframe src=', response.json()['content'])
        self.assertNotIn('<script>', response.json()['content'])
        self.assertNotIn('onClick', response.json()['content'])

    def test_experiment_post_create_fails_for_not_authenticated(self):
        response = self.client.post(self.list_url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_experiment_post_create_fails_for_non_owner(self):
        self.client.force_authenticate(user=self.non_owner)
        response = self.client.post(self.list_url, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_experiment_post_retrieve(self):
        expected_response_body = {
            'id': self.experiment_post.id,
            'comments': [],
            'content': 'Lorem ipsum.',
            'count_of_comments': 0,
            'created_at': '2019-07-10T12:00:00Z',
            'created_by': {
                'id': self.creator.id,
                'full_name': 'John Doe',
                'image_url': ''
            },
            'images': [],
            'title': 'New post'
        }
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_response_body)

    def test_experiment_post_update_succeeds_for_creator(self):
        request_body = {
            'content': 'Lorem ipsum.',
            'title': 'New post',
        }
        expected_response_body = {
            'id': self.experiment_post.id,
            'comments': [],
            'content': 'Lorem ipsum.',
            'count_of_comments': 0,
            'created_at': '2019-07-10T12:00:00Z',
            'created_by': {
                'id': self.creator.id,
                'full_name': 'John Doe',
                'image_url': ''
            },
            'images': [],
            'title': 'New post',
        }
        self.client.force_authenticate(user=self.creator)
        response = self.client.put(self.detail_url, request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_response_body)

    def test_experiment_post_update_succeeds_for_responsible(self):
        request_body = {
            'content': 'Lorem ipsum.',
            'title': 'New post',
        }
        self.client.force_authenticate(user=self.responsible)
        response = self.client.put(self.detail_url, request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_experiment_post_update_fails_for_not_authenticated(self):
        response = self.client.put(self.list_url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_experiment_post_update_fails_for_non_owner(self):
        self.client.force_authenticate(user=self.non_owner)
        response = self.client.put(self.list_url, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_experiment_post_partial_update_succeeds_for_creator(self):
        request_body = {
            'content': 'Example.',
        }
        expected_response_body = {
            'id': self.experiment_post.id,
            'comments': [],
            'content': 'Example.',
            'count_of_comments': 0,
            'created_at': '2019-07-10T12:00:00Z',
            'created_by': {
                'id': self.creator.id,
                'full_name': 'John Doe',
                'image_url': ''
            },
            'images': [],
            'title': 'New post',
        }
        self.client.force_authenticate(user=self.creator)
        response = self.client.patch(self.detail_url, request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_response_body)

    def test_experiment_post_partial_update_succeeds_for_responsible(self):
        request_body = {
            'content': 'Example.',
        }
        self.client.force_authenticate(user=self.responsible)
        response = self.client.patch(self.detail_url, request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_experiment_post_partial_update_fails_for_non_authenticated(self):
        response = self.client.patch(self.detail_url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_experiment_post_partial_update_fails_for_non_owner(self):
        self.client.force_authenticate(user=self.non_owner)
        response = self.client.patch(self.detail_url, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_experiment_post_destroy_succeeds_for_creator(self):
        self.client.force_authenticate(user=self.creator)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b'')

    def test_experiment_post_destroy_succeeds_for_responsible(self):
        self.client.force_authenticate(user=self.responsible)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b'')

    def test_experiment_post_destroy_fails_for_non_authenticated(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_experiment_post_destroy_fails_for_non_owner(self):
        self.client.force_authenticate(user=self.non_owner)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


@freeze_time('2019-07-10 12:00:00')
class ExperimentPostCommentAPITestCase(APITestCase):
    maxDiff = None

    def setUp(self):
        # Model instances
        self.creator = get_user_model().objects.create(
            first_name='John',
            last_name='Doe',
            username='owner',
        )
        self.responsible = get_user_model().objects.create(
            username='responsible',
        )
        self.non_owner = get_user_model().objects.create(
            username='non-owner',
        )
        self.first_stage = Stage.objects.create(
            stage_number=1,
            name='First stage',
        )
        self.experiment = Experiment.objects.create(
            description='Lorem ipsum',
            is_published=True,
            name='Example Experiment',
        )
        self.experiment.responsible_users.add(
            self.responsible
        )
        self.experiment_post = ExperimentPost.objects.create(
            content='Lorem ipsum.',
            experiment=self.experiment,
            title='New post'
        )
        self.experiment_post_comment = ExperimentPostComment.objects.create(
            content='Comment content.',
            created_by=self.creator,
            experiment_post=self.experiment_post,
        )

        # Urls
        self.detail_url = reverse('experiment-post-comment-detail', kwargs={
            'experiment_slug': self.experiment.slug,
            'post_id': self.experiment_post.id,
            'pk': self.experiment_post_comment.id
        })
        self.list_url = reverse('experiment-post-comment-list', kwargs={
            'experiment_slug': self.experiment.slug,
            'post_id': self.experiment_post.id,
        })

    def test_experiment_post_comment_list(self):
        expected_response_body = [{
            'id': self.experiment_post_comment.id,
            'content': 'Comment content.',
            'created_at': '2019-07-10T12:00:00Z',
            'created_by': {
                'id': self.creator.id,
                'full_name': 'John Doe',
                'image_url': ''
            },
        }]
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_response_body)

    def test_experiment_post_comment_create_succeeds_for_authenticated(self):
        request_body = {
            'content': 'Second comment.',
        }
        self.client.force_authenticate(user=self.creator)
        response = self.client.post(self.list_url, request_body)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected_response_body = {
            'id': response.json()['id'],
            'content': 'Second comment.',
            'created_at': '2019-07-10T12:00:00Z',
            'created_by': {
                'id': self.creator.id,
                'full_name': 'John Doe',
                'image_url': ''
            }
        }
        self.assertEqual(response.json(), expected_response_body)

    def test_experiment_post_comment_create_succeeds_for_unauthenticated(self):
        request_body = {
            'content': 'Anonymous comment.',
        }
        response = self.client.post(self.list_url, request_body)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected_response_body = {
            'id': response.json()['id'],
            'content': 'Anonymous comment.',
            'created_at': '2019-07-10T12:00:00Z',
            'created_by': None
        }
        self.assertEqual(response.json(), expected_response_body)

    def test_experiment_post_comment_retrieve(self):
        expected_response_body = {
            'id': self.experiment_post_comment.id,
            'content': 'Comment content.',
            'created_at': '2019-07-10T12:00:00Z',
            'created_by': {
                'id': self.creator.id,
                'full_name': 'John Doe',
                'image_url': ''
            }
        }
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_response_body)

    def test_experiment_post_comment_update_succeeds_for_creator(self):
        request_body = {
            'content': 'Updated comment.',
        }
        expected_response_body = {
            'id': self.experiment_post_comment.id,
            'content': 'Updated comment.',
            'created_at': '2019-07-10T12:00:00Z',
            'created_by': {
                'id': self.creator.id,
                'full_name': 'John Doe',
                'image_url': ''
            }
        }
        self.client.force_authenticate(user=self.creator)
        response = self.client.put(self.detail_url, request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_response_body)

    def test_experiment_post_comment_update_fails_for_not_authenticated(self):
        response = self.client.put(self.list_url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_experiment_post_comment_update_fails_for_non_owner(self):
        self.client.force_authenticate(user=self.non_owner)
        response = self.client.put(self.list_url, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_experiment_post_comment_update_fails_for_responsible(self):
        self.client.force_authenticate(user=self.responsible)
        response = self.client.put(self.list_url, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_experiment_post_comment_partial_update_succeeds_for_creator(self):
        request_body = {
            'content': 'Updated comment.',
        }
        expected_response_body = {
            'id': self.experiment_post_comment.id,
            'content': 'Updated comment.',
            'created_at': '2019-07-10T12:00:00Z',
            'created_by': {
                'id': self.creator.id,
                'full_name': 'John Doe',
                'image_url': ''
            }
        }
        self.client.force_authenticate(user=self.creator)
        response = self.client.patch(self.detail_url, request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_response_body)

    def test_experiment_post_comment_partial_update_fails_for_non_authenticated(self):
        response = self.client.patch(self.detail_url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_experiment_post_comment_partial_update_fails_for_non_owner(self):
        self.client.force_authenticate(user=self.non_owner)
        response = self.client.patch(self.detail_url, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_experiment_post_comment_partial_update_fails_for_responsible(self):
        self.client.force_authenticate(user=self.responsible)
        response = self.client.patch(self.detail_url, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_experiment_post_comment_destroy_succeeds_for_creator(self):
        self.client.force_authenticate(user=self.creator)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b'')

    def test_experiment_post_comment_destroy_succeeds_for_responsible(self):
        self.client.force_authenticate(user=self.responsible)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b'')

    def test_experiment_post_comment_destroy_fails_for_non_authenticated(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_experiment_post_comment_destroy_fails_for_non_owner(self):
        self.client.force_authenticate(user=self.non_owner)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
