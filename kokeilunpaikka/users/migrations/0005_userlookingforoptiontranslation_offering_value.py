# Generated by Django 2.2.5 on 2020-05-15 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_userprofile_send_experiment_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='userlookingforoptiontranslation',
            name='offering_value',
            field=models.CharField(blank=True, default='', help_text='An alternative for value, used in what the user can offer', max_length=255, verbose_name='offering value'),
        ),
    ]
