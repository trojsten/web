# -*- coding: utf-8 -*-
import django
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("plugin_prask_2_2_3", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="userlink",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                null=True,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        )
    ]
