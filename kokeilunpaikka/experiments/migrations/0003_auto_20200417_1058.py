# Generated by Django 2.2.5 on 2020-04-17 10:58

from django.db import migrations, models
from django.conf import settings
import django.db.models.deletion
import parler.models


def forwards_func(apps, schema_editor):
    ExperimentChallengeTimelineEntry = apps.get_model('experiments', 'ExperimentChallengeTimelineEntry')
    ExperimentChallengeTimelineEntryTranslation = apps.get_model('experiments', 'ExperimentChallengeTimelineEntryTranslation')

    for object in ExperimentChallengeTimelineEntry.objects.all():
        ExperimentChallengeTimelineEntryTranslation.objects.create(
            master_id=object.pk,
            language_code=settings.LANGUAGE_CODE,
            content=object.content
        )

def backwards_func(apps, schema_editor):
    ExperimentChallengeTimelineEntry = apps.get_model('experiments', 'ExperimentChallengeTimelineEntry')
    ExperimentChallengeTimelineEntryTranslation = apps.get_model('experiments', 'ExperimentChallengeTimelineEntryTranslation')

    for object in ExperimentChallengeTimelineEntry.objects.all():
        translation = _get_translation(object, ExperimentChallengeTimelineEntryTranslation)
        object.content = translation.content
        object.save()

def _get_translation(object, ExperimentChallengeTimelineEntryTranslation):
    translations = ExperimentChallengeTimelineEntryTranslation.objects.filter(master_id=object.pk)
    try:
        return translations.get(language_code=settings.LANGUAGE_CODE)
    except ObjectDoesNotExist:
        try:
            return translations.get(language_code=settings.PARLER_DEFAULT_LANGUAGE_CODE)
        except ObjectDoesNotExist:
            return translations.get()


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0002_auto_20190923_0702'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExperimentChallengeTimelineEntryTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('content', models.TextField(verbose_name='content')),
                ('master', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='experiments.ExperimentChallengeTimelineEntry')),
            ],
            options={
                'unique_together': {('language_code', 'master')},
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
        migrations.RunPython(forwards_func, backwards_func),
        migrations.RemoveField(
            model_name='experimentchallengetimelineentry',
            name='content'
        ),
    ]
