# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-09-10 11:02
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("contests", "0003_category_task")]

    operations = [
        migrations.RenameField(model_name="task", old_name="category", new_name="categories")
    ]
