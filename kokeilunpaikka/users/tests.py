from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from django.utils import translation

from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase

from ..experiments.models import Experiment
from ..stages.models import Stage
from ..themes.models import Theme
from .models import UserLookingForOption, UserProfile, UserStatusOption


class UserAPITestCase(APITestCase):
    maxDiff = None

    def setUp(self):
        self.user = get_user_model().objects.create(
            username='john@example.com',
            email='john@example.com',
            first_name='John',
            last_name='Doe'
        )
        UserProfile.objects.create(
            user=self.user,
        )

    def test_user_list(self):
        expected_response_body = [{
            'id': self.user.id,
            'first_name': 'John',
            'full_name': 'John Doe',
            'image_url': '',
            'last_name': 'Doe',
        }]
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_response_body)

    def test_user_list_simplified(self):
        expected_response_body = [{
            'id': self.user.id,
            'first_name': 'John',
            'full_name': 'John Doe',
            'last_name': 'Doe',
        }]
        url = '{}?simplified'.format(reverse('user-list'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_response_body)

    def test_user_list_search_by_name_matches(self):
        url = '{}?search=Doe'.format(reverse('user-list'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_user_list_search_by_name_when_no_match(self):
        url = '{}?search=Smith'.format(reverse('user-list'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 0)

    def test_user_list_with_pagination(self):
        url = '{}?page_size=1'.format(reverse('user-list'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['results']), 1)

    def test_user_create(self):
        request_body = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'password': 'password',
        }
        expected_response_body = {
            'id': None,
            'facebook_url': '',
            'description': '',
            'experiments': [],
            'first_name': 'John',
            'full_name': 'John Doe',
            'image_url': '',
            'instagram_url': '',
            'interested_in_themes': [],
            'last_name': 'Doe',
            'linkedin_url': '',
            'looking_for': [],
            'twitter_url': '',
        }
        url = reverse('user-list')
        response = self.client.post(url, request_body)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Set id manually for expected response body before the comparison as
        # it's unknown before the creation
        expected_response_body['id'] = response.data['id']
        self.assertEqual(response.json(), expected_response_body)

        # Test (empty) user profile was automatically created
        self.assertTrue(
            UserProfile.objects.filter(user=response.data['id']).exists()
        )

        # Test user is able to login with given credentials
        request_body = {
            'username': 'john.doe@example.com',
            'password': 'password'
        }
        url = reverse('rest_login')
        response = self.client.post(url, request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test confirmation email was sent
        self.assertEqual(len(mail.outbox), 1)
        with translation.override('en'):
            self.assertIn(
                'Thank you for your registration',
                mail.outbox[0].subject
            )

    def test_user_create_without_email_fails(self):
        request_body = {
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'password',
        }
        url = reverse('user-list')
        response = self.client.post(url, request_body)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_create_with_duplicate_username_fails(self):
        get_user_model().objects.create(
            username='joe@example.com',
            first_name='Joe',
            last_name='Doe'
        )
        request_body = {
            'email': 'joe@example.com',
            'first_name': 'Joe',
            'last_name': 'Doe',
            'password': 'password',
        }
        url = reverse('user-list')
        response = self.client.post(url, request_body)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    @patch('extensions.auth.models.send_template_mail')
    def test_user_create_when_confirmation_mail_sending_fails(self, test_patch):
        test_patch.return_value = 0
        request_body = {
            'email': 'jill@example.com',
            'first_name': 'Jill',
            'last_name': 'Doe',
            'password': 'password',
        }
        url = reverse('user-list')
        with self.assertLogs('extensions.auth.models', level='ERROR') as cm:
            self.client.post(url, request_body)
            self.assertEqual(len(cm.records), 1)
            self.assertIn(
                'Could not send registration notification email for user',
                cm.output[0]
            )

    def test_user_retrieve(self):
        expected_response_body = {
            'id': self.user.id,
            'facebook_url': '',
            'description': '',
            'experiments': [],
            'first_name': 'John',
            'full_name': 'John Doe',
            'image_url': '',
            'instagram_url': '',
            'interested_in_themes': [],
            'last_name': 'Doe',
            'linkedin_url': '',
            'looking_for': [],
            'twitter_url': '',
        }
        url = reverse('user-detail', kwargs={'pk': self.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_response_body)

    def test_user_retrieve_with_filled_profile(self):
        theme = Theme.objects.create(
            name='Theme'
        )
        self.user.profile.description = 'Lorem ipsum'
        self.user.profile.save()
        self.user.profile.interested_in_themes.add(
            theme
        )
        looking_for = UserLookingForOption.objects.create(
            value='Help',
        )
        self.user.profile.looking_for.add(
            looking_for
        )
        expected_response_body = {
            'id': self.user.id,
            'facebook_url': '',
            'description': 'Lorem ipsum',
            'experiments': [],
            'first_name': 'John',
            'full_name': 'John Doe',
            'image_url': '',
            'instagram_url': '',
            'interested_in_themes': [{
                'id': theme.id,
                'is_curated': False,
                'name': 'Theme'
            }],
            'last_name': 'Doe',
            'linkedin_url': '',
            'looking_for': [{
                'id': looking_for.id,
                'value': 'Help'
            }],
            'twitter_url': '',
        }
        url = reverse('user-detail', kwargs={'pk': self.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_response_body)

    def test_user_retrieve_with_email_exposed(self):
        self.user.profile.expose_email_address = True
        self.user.profile.save()
        url = reverse('user-detail', kwargs={'pk': self.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('email', response.data)
        self.assertEqual(response.data['email'], 'john@example.com')

    def test_user_retrieve_with_email_not_exposed(self):
        self.user.profile.expose_email_address = False
        self.user.profile.save()
        url = reverse('user-detail', kwargs={'pk': self.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('email', response.data)

    @freeze_time('2019-07-10 12:00:00')
    def test_user_retrieve_published_experiments_listed(self):
        responsible = get_user_model().objects.create(
            username='jane.doe@example.com',
            first_name='Jane',
            last_name='Doe'
        )
        UserProfile.objects.create(user=responsible)
        stage = Stage.objects.create(stage_number=1, name='Stage')
        experiment = Experiment.objects.create(
            is_published=True,
            stage=stage,
            name='Test',
        )
        experiment.responsible_users.add(responsible)
        url = reverse('user-detail', kwargs={'pk': responsible.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['experiments']), 1)
        self.assertEqual(response.json()['experiments'][0], {
            'id': response.data['experiments'][0]['id'],
            'image_url': '',
            'is_published': True,
            'name': 'Test',
            'published_at': '2019-07-10T12:00:00Z',
            'short_description': '',
            'slug': 'test',
            'stage': {
                'description': '',
                'name': 'Stage',
                'stage_number': 1,
            },
        })

    def test_user_retrieve_unpublished_experiments_listed_for_authenticated_responsible(self):
        responsible = get_user_model().objects.create(
            username='jane.doe@example.com',
            first_name='Jane',
            last_name='Doe'
        )
        secondary_responsible = get_user_model().objects.create(
            username='john.doe@example.com',
            first_name='John',
            last_name='Doe'
        )
        UserProfile.objects.create(user=responsible)
        stage = Stage.objects.create(stage_number=1, name='Stage')
        experiment = Experiment.objects.create(
            is_published=False,
            stage=stage,
            name='Test',
        )
        experiment.responsible_users.set([responsible, secondary_responsible])
        url = reverse('user-detail', kwargs={'pk': responsible.id})

        # Experiments should not be listed when responsible is not
        # authenticated themselves.
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['experiments']), 0)

        # Should be listed after authentication
        self.client.force_authenticate(user=responsible)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['experiments']), 1)

        # Should be listed after authentication even for other responsible of
        # the same experiment
        self.client.force_authenticate(user=secondary_responsible)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['experiments']), 1)

    def test_user_retrieve_not_found_for_user_without_profile(self):
        user_without_profile = get_user_model().objects.create(
            username='jane.doe@example.com',
            first_name='Jane',
            last_name='Doe'
        )
        url = reverse('user-detail', kwargs={'pk': user_without_profile.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_retrieve_not_found_for_inactive_user(self):
        inactive_user = get_user_model().objects.create(
            username='jane.doe@example.com',
            first_name='Jane',
            last_name='Doe',
            is_active=False,
        )
        UserProfile.objects.create(
            user=inactive_user,
        )
        url = reverse('user-detail', kwargs={'pk': inactive_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_looking_for_options(self):
        looking_for_option = UserLookingForOption.objects.create(
            value='Help'
        )
        expected_response_body = [{
            'id': looking_for_option.id,
            'value': 'Help',
        }]
        url = reverse('user-looking-for-options')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_response_body)

    def test_user_status_options(self):
        status_option = UserStatusOption.objects.create(
            value='Student'
        )
        expected_response_body = [{
            'id': status_option.id,
            'value': 'Student',
        }]
        url = reverse('user-status-options')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_response_body)
