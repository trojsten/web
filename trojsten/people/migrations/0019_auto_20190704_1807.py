# Generated by Django 2.1.9 on 2019-07-04 16:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("people", "0018_merge_20190704_1554")]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="last_name",
            field=models.CharField(max_length=150, verbose_name="last name"),
        ),
        migrations.AlterField(
            model_name="user",
            name="school",
            field=models.ForeignKey(
                blank=True,
                default=None,
                help_text=(
                    "Do políčka napíšte skratku, časť názvu alebo adresy školy a následne vyberte"
                    " správnu možnosť zo zoznamu. Pokiaľ vaša škola nie je v&nbsp;zozname, vyberte"
                    ' "Iná škola" a&nbsp;pošlite nám e-mail.'
                ),
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="schools.School",
                verbose_name="škola",
            ),
        ),
    ]
