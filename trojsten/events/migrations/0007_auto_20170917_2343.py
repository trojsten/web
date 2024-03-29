# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2017-09-17 21:43
from django.db import migrations

event_types = {"KSP sústredenie", "PRASK sústredenie"}


def update_event_attendance(apps, schema_editor):
    EventType = apps.get_model("events", "EventType")
    for event_type in EventType.objects.filter(name__in=event_types):
        for event in event_type.event_set.all():
            for participant in event.eventparticipant_set.filter(type=1, going=True):
                participant.going = False
                participant.save()


def reverse_update_event_attendance(apps, schema_editor):
    # We won't update anything.
    pass


class Migration(migrations.Migration):
    dependencies = [("events", "0006_auto_20170917_1657")]

    operations = [
        migrations.RunPython(update_event_attendance, reverse_code=reverse_update_event_attendance)
    ]
