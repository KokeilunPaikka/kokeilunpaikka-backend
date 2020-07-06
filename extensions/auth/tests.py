from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from kokeilunpaikka.themes.models import Theme
from kokeilunpaikka.uploads.models import Image
from kokeilunpaikka.users.models import UserLookingForOption, UserStatusOption


class AuthenticationAPITestCase(APITestCase):
    maxDiff = None

    def setUp(self):
        self.user = get_user_model().objects.create(
            email='john.doe@example.com',
            first_name='John',
            last_name='Doe',
            username='john.doe@example.com',
            is_active=True,
        )
        self.user.set_password('password')
        self.user.save()

    def test_user_login(self):
        request_body = {
            'username': 'john.doe@example.com',
            'password': 'password'
        }
        url = reverse('rest_login')
        response = self.client.post(url, request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('key', response.data)
        key = response.data['key']
        token = Token.objects.get(key=key)
        self.assertEqual(token.user, self.user)

    def test_user_logout(self):
        request_body = {
            'username': 'john.doe@example.com',
            'password': 'password'
        }

        # Login first to be able to logout
        url = reverse('rest_login')
        response = self.client.post(url, request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        key = response.data['key']
        self.assertTrue(Token.objects.filter(key=key).exists())

        # Logout
        self.client.force_authenticate(user=self.user)
        url = reverse('rest_logout')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Token.objects.filter(key=key).exists())

    def test_user_password_reset(self):
        request_body = {
            'email': 'john.doe@example.com',
        }
        url = reverse('rest_password_reset')
        response = self.client.post(url, request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_password_change(self):
        request_body = {
            'new_password1': 'fmw48mafkdmsf',
            'new_password2': 'fmw48mafkdmsf',
        }
        self.client.force_authenticate(user=self.user)
        url = reverse('rest_password_change')
        response = self.client.post(url, request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_details(self):
        expected_response_body = {
            'id': self.user.id,
            'description': '',
            'email': 'john.doe@example.com',
            'experiments': [],
            'expose_email_address': False,
            'facebook_url': '',
            'first_name': 'John',
            'full_name': 'John Doe',
            'image_url': '',
            'instagram_url': '',
            'interested_in_themes': [],
            'last_name': 'Doe',
            'linkedin_url': '',
            'looking_for': [],
            'offering': None,
            'send_experiment_notification': None,
            'status': None,
            'twitter_url': '',
        }
        url = reverse('rest_user_details')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_response_body)

    def test_current_user_update(self):
        theme = Theme.objects.create(
            name='Theme'
        )
        looking_for = UserLookingForOption.objects.create(
            value='Help',
        )
        user_status = UserStatusOption.objects.create(
            value='Student',
        )
        request_body = {
            'description': 'Lorem ipsum',
            'expose_email_address': True,
            'facebook_url': 'https://www.facebook.com',
            'first_name': 'Jane',
            'instagram_url': 'https://www.instagram.com',
            'interested_in_theme_ids': [theme.id],
            'language': 'en',
            'last_name': 'Doe',
            'linkedin_url': 'https://fi.linkedin.com',
            'looking_for_ids': [looking_for.id],
            'status_id': user_status.id,
            'twitter_url': 'https://twitter.com',
        }
        expected_response_body = {
            'id': self.user.id,
            'description': 'Lorem ipsum',
            'experiments': [],
            'expose_email_address': True,
            'facebook_url': 'https://www.facebook.com',
            'email': 'john.doe@example.com',
            'first_name': 'Jane',
            'full_name': 'Jane Doe',
            'image_url': '',
            'instagram_url': 'https://www.instagram.com',
            'interested_in_themes': [{
                'id': theme.id,
                'name': 'Theme',
                'is_curated': False,
            }],
            'last_name': 'Doe',
            'linkedin_url': 'https://fi.linkedin.com',
            'looking_for': [{
                'id': looking_for.id,
                'value': 'Help',
                'offering_value': ''
            }],
            'offering': [],
            'send_experiment_notification': False,
            'status': {
                'id': user_status.id,
                'value': 'Student',
            },
            'twitter_url': 'https://twitter.com',
        }
        url = reverse('rest_user_details')
        self.client.force_authenticate(user=self.user)
        response = self.client.put(url, request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_response_body)
        self.assertEqual(self.user.profile.language, 'en')
        self.assertEqual(self.user.profile.status.id, user_status.id)

    def test_current_user_partial_update(self):
        request_body = {
            'description': 'Lorem ipsum'
        }
        expected_response_body = {
            'id': self.user.id,
            'description': 'Lorem ipsum',
            'email': 'john.doe@example.com',
            'experiments': [],
            'expose_email_address': False,
            'facebook_url': '',
            'first_name': 'John',
            'full_name': 'John Doe',
            'image_url': '',
            'instagram_url': '',
            'interested_in_themes': [],
            'last_name': 'Doe',
            'linkedin_url': '',
            'looking_for': [],
            'offering': [],
            'send_experiment_notification': False,
            'status': None,
            'twitter_url': '',
        }
        url = reverse('rest_user_details')
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(url, request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_response_body)

    def test_current_user_cant_set_image_not_uploaded_by_the_user(self):
        image = Image.objects.create(
            image=SimpleUploadedFile('test.jpeg', b'', content_type='image/jpeg'),
        )
        request_body = {
            'image_id': image.id
        }
        url = reverse('rest_user_details')
        self.client.force_authenticate(user=self.user)

        # Request should fail because the image was not marked as being
        # uploaded by the current user.
        response = self.client.patch(url, request_body)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('image_id', response.json())

        # Test with uploaded by current user to verify the success case
        image.uploaded_by = self.user
        image.save()
        response = self.client.patch(url, request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
