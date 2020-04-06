from django.test import TestCase
from django.urls import reverse

from rest_framework import status


class APIDocsTestCase(TestCase):

    def test_docs_available(self):
        url = reverse('api-docs:docs-index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
