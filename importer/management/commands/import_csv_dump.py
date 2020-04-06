import csv
from collections import defaultdict
from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.utils.timezone import make_aware

import pytz

from kokeilunpaikka.experiments.models import (
    Experiment,
    ExperimentExternalLink,
    ExperimentPost
)
from kokeilunpaikka.stages.models import QuestionAnswer
from kokeilunpaikka.themes.models import Theme
from kokeilunpaikka.uploads.models import Image
from kokeilunpaikka.users.models import UserProfile


class Command(BaseCommand):
    help = 'Imports data from a given .csv file by data type'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str)
        parser.add_argument('--type', type=str)

    def handle(self, *args, **options):
        if not options['file']:
            raise CommandError('Invalid file path given.')

        with open(options['file'], newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')

            if options['type'] == 'themes':
                num_added, num_updated = self.import_themes(reader)
            elif options['type'] == 'users':
                num_added, num_updated = self.import_users(reader)
            elif options['type'] == 'experiments':
                num_added, num_updated = self.import_experiments(reader)
            elif options['type'] == 'experiment_data':
                num_added, num_updated = self.import_experiment_data(reader)
            else:
                raise CommandError('Invalid import type given.')

        self.stdout.write(self.style.SUCCESS(
            'Successfully added {} rows, updated {} rows.'.format(num_added, num_updated)
        ))

    def import_themes(self, reader):
        counter_created = 0
        counter_updated = 0
        for row in reader:
            obj, created = Theme.objects.language('fi').update_or_create(
                id=row['id'],
                defaults={
                    'name': row['name'],
                    'is_curated': False,
                }
            )

            # Override automatically set default timestamps on creation.
            # This must be done with the update method of an queryset.
            created_at = make_aware(
                datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S'),
                timezone=pytz.timezone('Europe/Helsinki')
            ) if row['created_at'] != '' else timezone.now()
            updated_at = make_aware(
                datetime.strptime(row['updated_at'], '%Y-%m-%d %H:%M:%S'),
                timezone=pytz.timezone('Europe/Helsinki')
            ) if row['updated_at'] != '' else created_at

            Theme.objects.filter(pk=obj.id).update(
                created_at=created_at,
                updated_at=updated_at,
            )

            if created:
                counter_created += 1
            else:
                counter_updated += 1
        return counter_created, counter_updated

    def import_users(self, reader):
        if not Theme.objects.exists():
            raise CommandError('Themes must be imported before experiments.')

        counter_created = 0
        counter_updated = 0
        for row in reader:
            user_obj, created = get_user_model().objects.update_or_create(
                id=row['id'],
                defaults={
                    'first_name': row['first_name'],
                    'is_staff': False,
                    'is_active': True,
                    'last_name': row['last_name'],
                    'username': row['email'],
                    'email': row['email'],
                    'last_login': make_aware(
                        datetime.strptime(row['last_login'], '%Y-%m-%d %H:%M:%S'),
                        timezone=pytz.timezone('Europe/Helsinki')
                    ) if row['last_login'] != '' else None,
                    'date_joined': make_aware(
                        datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S'),
                        timezone=pytz.timezone('Europe/Helsinki')
                    ) if row['created_at'] != '' else timezone.now(),
                }
            )

            # Remove existing photo instance if updating
            if not created and user_obj.profile.image:
                user_obj.profile.image.delete()

            if row['image_filename']:
                image = Image.objects.create(
                    image=row['image_filename'],
                    uploaded_by_id=user_obj.id
                )
            else:
                image = None

            theme_ids = [
                int(x)
                for x
                in row['tags'].replace('[', '').replace(']', '').split(', ')
                if x.isdigit()
            ]

            link_urls = [
                x
                for x
                in row['links'].replace('[', '').replace(']', '').split(', ')
                if x
            ]

            # Parse URLs per type for new profile model. Only the first
            # occurence is taken into account.
            links = {
                'facebook_url': next((x for x in link_urls if x.find('facebook.com') != -1), ''),
                'instagram_url': next((x for x in link_urls if x.find('instagram.com') != -1), ''),
                'linkedin_url': next((x for x in link_urls if x.find('linkedin.com') != -1), ''),
                'twitter_url': next((x for x in link_urls if x.find('twitter.com') != -1), ''),
            }

            profile_obj, profile_created = UserProfile.objects.update_or_create(
                user_id=user_obj.id,
                defaults={
                    'description': row['description'],
                    'expose_email_address': False,
                    'language': settings.LANGUAGE_CODE,
                    'status': None,
                    'image': image,
                    **links
                }
            )
            profile_obj.interested_in_themes.set(theme_ids)
            profile_obj.looking_for.clear()

            if created:
                counter_created += 1
            else:
                counter_updated += 1
        return counter_created, counter_updated

    def import_experiments(self, reader):
        if not Theme.objects.exists():
            raise CommandError('Themes must be imported before experiments.')

        counter_created = 0
        counter_updated = 0

        for row in reader:

            stage_id = int(row['stage_id'])

            # Convert stage_id to match the new states in the system
            if stage_id in (0, 1, 2, 3):
                converted_stage_id = 1
            elif stage_id == 4:
                converted_stage_id = 2
            elif stage_id == 5:
                converted_stage_id = 3
            else:
                raise CommandError('Invalid stage number')

            # Remove existing photo and link instances if updating
            existing_object = Experiment.objects.filter(pk=row['id']).first()
            if existing_object:
                if existing_object.image:
                    existing_object.image.delete()
                existing_object.external_links.all().delete()

            if row['image_filename']:
                image = Image.objects.create(
                    image=row['image_filename'],
                    uploaded_by_id=row['created_by_id']
                )
            else:
                image = None

            theme_ids = [
                int(x)
                for x
                in row['tags'].replace('[', '').replace(']', '').split(', ')
                if x.isdigit()
            ]

            link_urls = [
                x
                for x
                in row['links'].replace('[', '').replace(']', '').split(', ')
                if x
            ]

            if row['name_fi'] != '':
                language = 'fi'
            elif row['name_sv'] != '':
                language = 'sv'
            elif row['name_en'] != '':
                language = 'en'
            else:
                CommandError('Could not detect language for experiment content.')

            obj, created = Experiment.objects.update_or_create(
                id=row['id'],
                defaults={
                    'is_published': row['is_published'],
                    'created_by_id': row['created_by_id'],
                    'image': image,
                    'language': language,
                    'success_rating': None,
                    'name': row[f'name_{language}'],
                    'description': row[f'description_{language}'],
                    'organizer': row[f'organizer_{language}'],
                    'stage_id': converted_stage_id,
                    'published_at': make_aware(
                        datetime.strptime(row['published_at'], '%Y-%m-%d %H:%M:%S'),
                        timezone=pytz.timezone('Europe/Helsinki')
                    ) if row['published_at'] != '' else None,
                }
            )
            obj.themes.set(theme_ids)
            obj.responsible_users.set([row['created_by_id']])
            obj.looking_for.clear()

            for link_url in link_urls:
                ExperimentExternalLink.objects.create(
                    url=link_url,
                    experiment=obj,
                )

            # Override automatically set default timestamps on creation.
            # This must be done with the update method of an queryset.
            created_at = make_aware(
                datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S'),
                timezone=pytz.timezone('Europe/Helsinki')
            ) if row['created_at'] != '' else timezone.now()
            updated_at = make_aware(
                datetime.strptime(row['updated_at'], '%Y-%m-%d %H:%M:%S'),
                timezone=pytz.timezone('Europe/Helsinki')
            ) if row['updated_at'] != '' else created_at

            Experiment.objects.filter(pk=obj.id).update(
                created_at=created_at,
                updated_at=updated_at,
                description=obj.description + '\n\n' + '\n'.join(link_urls)
            )

            if created:
                counter_created += 1
            else:
                counter_updated += 1
        return counter_created, counter_updated

    def import_experiment_data(self, reader):
        if not Experiment.objects.exists():
            raise CommandError('Experiments must be imported before data.')

        counter_created = 0
        counter_updated = 0

        grouped_by_experiment_id = defaultdict(dict)

        for row in reader:
            experiment_id = int(row.pop('experiment_id'))
            lang_code = row.pop('lang_code')

            if lang_code not in grouped_by_experiment_id[experiment_id]:
                grouped_by_experiment_id[experiment_id][lang_code] = {}
            grouped_by_experiment_id[experiment_id][lang_code][row['content_key']] = (
                row['content'],
                row['created_at'],
                row['updated_at'],
                row['stage'],
            )

        for experiment_id, language_data in grouped_by_experiment_id.items():
            try:
                experiment = Experiment.objects.get(pk=experiment_id)
            except Experiment.DoesNotExist:
                continue

            # Remove all related posts in case there are any to prevent
            # duplicates if the command is run multiple times.
            experiment.posts.all().delete()

            stage_id = int(language_data[experiment.language]['title'][3])

            long_description = ''
            lookup = f'{stage_id}_long_description'
            if lookup in language_data[experiment.language].keys():
                long_description = language_data[experiment.language][lookup][0]
                created_at_str = language_data[experiment.language][lookup][1]
                updated_at_str = language_data[experiment.language][lookup][2]

            if long_description != '':
                counter_updated += 1

                experiment_post = ExperimentPost.objects.create(
                    experiment=experiment,
                    created_by=experiment.created_by,
                    content=long_description,
                    title='',
                )
                experiment_post.images.clear()

                # Override automatically set default timestamps on creation.
                # This must be done with the update method of an queryset.
                created_at = make_aware(
                    datetime.strptime(created_at_str, '%Y-%m-%d %H:%M:%S'),
                    timezone=pytz.timezone('Europe/Helsinki')
                ) if created_at_str != '' else timezone.now()
                updated_at = make_aware(
                    datetime.strptime(updated_at_str, '%Y-%m-%d %H:%M:%S'),
                    timezone=pytz.timezone('Europe/Helsinki')
                ) if updated_at_str != '' else created_at

                ExperimentPost.objects.filter(pk=experiment_post.id).update(
                    created_at=created_at,
                    updated_at=updated_at,
                )

            # Dictionary in format:
            # - key: question id in new django database to which this answer
            # should be assigned to
            # - value: list of content_key identifiers for question answers in
            # the old database, in the order of presentation (and the order in
            # which these answers should be concatenated)
            question_answer_conversion_table = {
                1: ['0_short_description', '2_point_of_exp'],
                2: ['1_short_description', '2_what', '2_when'],
                3: ['2_who'],
                4: ['5_short_description'],
                5: ['what_learned'],
                6: ['what_next'],
                8: ['3_short_description'],
                9: ['2_skills'],
            }

            # Remove all related answers in case there are any to prevent
            # duplicates if the command is run multiple times.
            experiment.questionanswer_set.all().delete()

            for question_id, old_keys in question_answer_conversion_table.items():
                answer = ''
                for old_key in old_keys:
                    key_found_and_not_empty = (
                        old_key in language_data[experiment.language].keys() and
                        language_data[experiment.language][old_key][0]
                    )

                    if key_found_and_not_empty:
                        # Add two linebreaks as separator if there are already
                        # answer content concatenated.
                        if answer != '':
                            answer += '\n\n'

                        answer += language_data[experiment.language][old_key][0]
                        created_at_str = language_data[experiment.language][old_key][1]
                        updated_at_str = language_data[experiment.language][old_key][2]

                if answer != '':
                    counter_updated += 1

                    question_answer = QuestionAnswer.objects.create(
                        answered_by=experiment.created_by,
                        experiment=experiment,
                        question_id=question_id,
                        value=answer,
                    )

                    # Override automatically set default timestamps on creation.
                    # This must be done with the update method of an queryset.
                    created_at = make_aware(
                        datetime.strptime(created_at_str, '%Y-%m-%d %H:%M:%S'),
                        timezone=pytz.timezone('Europe/Helsinki')
                    ) if created_at_str != '' else timezone.now()
                    updated_at = make_aware(
                        datetime.strptime(updated_at_str, '%Y-%m-%d %H:%M:%S'),
                        timezone=pytz.timezone('Europe/Helsinki')
                    ) if updated_at_str != '' else created_at

                    QuestionAnswer.objects.filter(pk=question_answer.id).update(
                        created_at=created_at,
                        updated_at=updated_at,
                    )

        return counter_created, counter_updated
