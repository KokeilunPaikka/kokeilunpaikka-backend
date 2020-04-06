from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from .models import Theme


class ThemeAPITestCase(APITestCase):
    maxDiff = None

    def setUp(self):
        self.user_1 = get_user_model().objects.create()
        self.theme = Theme.objects.create(
            name='Theme'
        )

    def test_theme_list(self):
        expected_response_body = [{
            'id': self.theme.id,
            'is_curated': False,
            'name': 'Theme',
        }]
        url = reverse('theme-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_response_body)

    def test_theme_create(self):
        request_body = {
            'name': 'Lorem ipsum'
        }
        url = reverse('theme-list')
        self.client.force_authenticate(user=self.user_1)
        response = self.client.post(url, request_body)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected_response_body = {
            'id': response.json()['id'],
            'is_curated': False,
            'name': 'Lorem ipsum',
        }
        self.assertEqual(response.json(), expected_response_body)

    def test_theme_create_fails_for_unauthenticated(self):
        url = reverse('theme-list')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_theme_retrieve(self):
        expected_response_body = {
            'id': self.theme.id,
            'is_curated': False,
            'name': 'Theme',
        }
        url = reverse('theme-detail', kwargs={'pk': self.theme.id})
        self.client.force_authenticate(user=self.user_1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_response_body)
