# Generated by Django 2.1.9 on 2019-12-12 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("contests", "0018_task_description_points_visible")]

    operations = [
        migrations.AlterField(
            model_name="task",
            name="description_points_visible",
            field=models.BooleanField(
                default=False, verbose_name="Zobrazovať body za popis vo výsledkovke"
            ),
        )
    ]
