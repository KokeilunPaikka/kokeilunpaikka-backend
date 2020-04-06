import tempfile

from django.contrib.auth import get_user_model
from django.urls import reverse

from PIL import Image as PILImage
from rest_framework import status
from rest_framework.test import APITestCase


class ImageAPITestCase(APITestCase):
    maxDiff = None

    def setUp(self):
        self.user_1 = get_user_model().objects.create()

    def test_image_file_upload(self):
        self.client.force_authenticate(self.user_1)

        # Create temporary image for the test
        image = PILImage.new('RGB', (100, 100))
        tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(tmp_file)

        headers = {
            'HTTP_CONTENT_DISPOSITION': 'attachment; filename={}'.format(tmp_file.name),
        }

        tmp_file.seek(0)

        response = self.client.post(
            reverse('image-list'),
            tmp_file.read(),
            content_type='image/jpg',
            **headers,
        )

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertIn('id', response.json())
        self.assertIn('url', response.json())

    def test_image_file_upload_fails_for_unauthenticated(self):
        response = self.client.post(reverse('image-list'))
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
