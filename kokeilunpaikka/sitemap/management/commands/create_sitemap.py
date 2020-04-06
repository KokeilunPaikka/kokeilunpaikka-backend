import os
from django.core.management.base import BaseCommand
from django.conf import settings
import requests

from core.settings.base import BASE_DIR
from kokeilunpaikka.experiments.models import Experiment, ExperimentChallenge
from kokeilunpaikka.library.models import LibraryItem
from kokeilunpaikka.users.models import UserProfile


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        front_base = os.environ.get('BASE_FRONTEND_URL', '')
        wp_api = os.environ.get('WP_API', '')
        urls = []
        react_urls = [
            'kokeilijat',
            'kokeiluhaut',
            'ajankohtaista',
            'kirjasto',
            'kokeilut',
        ]

        for language in settings.LANGUAGES:
            lang = language[0]

            # Language home page
            urls.append({
                'url': '{}/{}'.format(front_base, lang)
            })

            # Users
            profiles = UserProfile.objects.all()
            for profile in profiles:
                urls.append({
                    'url': '{}/{}/kokeilija/{}'.format(front_base, lang, profile.user.id)
                })

            # Experiments
            experiments = Experiment.objects.all()
            for experiment in experiments:
                urls.append({
                    'url': '{}/{}/kokeilu/{}'.format(front_base, lang, experiment.slug)
                })

            # Library items
            library_items = LibraryItem.objects.all()
            for library_item in library_items:
                library_item.set_current_language(lang)
                urls.append({
                    'url': '{}/{}/kirjasto/{}'.format(front_base, lang, library_item.slug)
                })

            # Experiment challanges
            experiment_challenges = ExperimentChallenge.objects.all()
            for experiment_challenge in experiment_challenges:
                experiment_challenge.set_current_language(lang)
                urls.append({
                    'url': '{}/{}/kokeiluhaku/{}'.format(front_base, lang,
                                                         experiment_challenge.slug)
                })

            # React listing views
            for react_url in react_urls:
                urls.append({
                    'url': '{}/{}/{}'.format(front_base, lang, react_url)
                })

        # Posts from WP
        posts_per_page = 100
        r = requests.get('{}/wp-json/wp/v2/posts?per_page={}'.format(wp_api, posts_per_page))
        page = 1
        for post in r.json():
            urls.append({
                'url': post['link']
            })

        total_pages = int(r.headers['X-WP-TotalPages'])
        while page < total_pages:
            page += 1
            r = requests.get(
                '{}/wp-json/wp/v2/posts?per_page={}&page={}'.format(wp_api, posts_per_page, page))
            for post in r.json():
                urls.append({
                    'url': post['link']
                })

        # Pages from WP
        r = requests.get('{}/wp-json/wp/v2/pages?per_page={}'.format(wp_api, posts_per_page))
        page = 1
        for post in r.json():
            urls.append({
                'url': post['link']
            })

        total_pages = int(r.headers['X-WP-TotalPages'])
        while page < total_pages:
            page += 1
            r = requests.get(
                '{}/wp-json/wp/v2/pages?per_page={}&page={}'.format(wp_api, posts_per_page, page))
            for post in r.json():
                urls.append({
                    'url': post['link']
                })

        f = open(BASE_DIR + "/files/sitemap.xml", "w")
        f.write('<?xml version="1.0" encoding="UTF-8"?>')
        f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

        for url in urls:
            f.write("<url>")
            f.write("<loc>{}</loc>".format(url['url']))

            f.write("</url>")

        f.write('</urlset> ')
        f.close()
