# Generated by Django 2.2.5 on 2020-05-04 10:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0005_remove_experimentchallenge_lead_text_2'),
        ('stages', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='ignore_in_experiment_challenge',
            field=models.ManyToManyField(blank=True, help_text='Questions can be marked to be ignored in case of an experiment challenge.', related_name='ignored_questions', to='experiments.ExperimentChallenge', verbose_name='ignore in experiment challenge'),
        ),
    ]