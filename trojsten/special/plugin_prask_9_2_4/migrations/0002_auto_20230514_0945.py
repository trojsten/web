# Generated by Django 2.2.24 on 2023-05-14 09:45

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('plugin_prask_9_2_4', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userlevel',
            name='solved',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterUniqueTogether(
            name='userlevel',
            unique_together={('user', 'level')},
        ),
        migrations.RemoveField(
            model_name='userlevel',
            name='series',
        ),
    ]
