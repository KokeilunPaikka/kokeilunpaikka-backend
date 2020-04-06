from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase

from ..experiments.models import Experiment
from ..stages.models import Stage
from ..themes.models import Theme
from .models import LibraryItem


class LibraryItemModelTestCase(TestCase):

    def test_str(self):
        library_item = LibraryItem.objects.create(
            name='Item',
            slug='item'
        )
        self.assertEqual(str(library_item), 'Item')

    def test_visible_manager_method(self):
        LibraryItem.objects.create(
            name='Item',
            slug='item',
            is_visible=False
        )
        self.assertEqual(LibraryItem.objects.visible().count(), 0)
        LibraryItem.objects.create(
            name='Item',
            slug='item-2',
            is_visible=True
        )
        self.assertEqual(LibraryItem.objects.visible().count(), 1)


@freeze_time('2019-07-10 12:00:00')
class LibraryItemAPITestCase(APITestCase):
    maxDiff = None

    def setUp(self):
        self.owner = get_user_model().objects.create(
            username='owner',
        )
        self.first_stage = Stage.objects.create(
            stage_number=1,
            name='First stage',
        )
        self.library_item = LibraryItem.objects.create(
            description='Lorem ipsum',
            is_visible=True,
            lead_text='Lorem ipsum',
            name='Library Item',
            slug='library-item',
        )
        theme = Theme.objects.create()
        self.experiment = Experiment.objects.create(
            description='Lorem ipsum',
            is_published=True,
            name='Example Experiment',
        )
        self.experiment.themes.add(theme)
        self.library_item.themes.add(theme)

    def test_library_item_list(self):
        expected_response_body = [{
            'id': self.library_item.id,
            'description': 'Lorem ipsum',
            'image_url': '',
            'lead_text': 'Lorem ipsum',
            'name': 'Library Item',
            'slug': 'library-item',
        }]
        url = reverse('library-item-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_response_body)

    def test_library_item_list_with_pagination(self):
        url = '{}?page_size=1'.format(reverse('library-item-list'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['results']), 1)

    def test_library_item_retrieve(self):
        expected_response_body = {
            'id': self.library_item.id,
            'description': 'Lorem ipsum',
            'experiments': [{
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
                }
            }],
            'image_url': '',
            'lead_text': 'Lorem ipsum',
            'name': 'Library Item',
            'slug': 'library-item',
        }
        url = reverse('library-item-detail', kwargs={
            'translations__slug': self.library_item.slug
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_response_body)

    def test_library_item_retrieve_not_found_for_non_visible(self):
        non_visible_library_item = LibraryItem.objects.create(
            is_visible=False,
            name='Non Visible Library Item',
            slug='non-visible-library-item',
        )
        url = reverse('library-item-detail', kwargs={
            'translations__slug': non_visible_library_item.slug
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
