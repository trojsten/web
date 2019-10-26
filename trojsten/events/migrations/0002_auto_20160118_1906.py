# -*- coding: utf-8 -*-
import django
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0001_initial"),
        ("sites", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("auth", "0006_require_contenttypes_0002"),
        ("people", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="registration",
            name="required_user_properties",
            field=models.ManyToManyField(
                related_name="_registration_required_user_properties_+",
                verbose_name="povinn\xe9 \xfadaje",
                to="people.UserPropertyKey",
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name="place",
            name="address",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                blank=True,
                to="people.Address",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="invitation",
            name="event",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="invitations",
                verbose_name="akcia",
                to="events.Event",
            ),
        ),
        migrations.AddField(
            model_name="invitation",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                verbose_name="pou\u017e\xedvate\u013e",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="eventtype",
            name="organizers_group",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                verbose_name="skupina ved\xfacich",
                to="auth.Group",
            ),
        ),
        migrations.AddField(
            model_name="eventtype", name="sites", field=models.ManyToManyField(to="sites.Site")
        ),
        migrations.AddField(
            model_name="event",
            name="links",
            field=models.ManyToManyField(
                to="events.Link", verbose_name="zoznam odkazov", blank=True
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="place",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                verbose_name="miesto",
                to="events.Place",
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="registration",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                verbose_name="prihl\xe1\u0161ka",
                blank=True,
                to="events.Registration",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                verbose_name="typ akcie",
                to="events.EventType",
            ),
        ),
        migrations.CreateModel(
            name="OrganizerInvitation",
            fields=[],
            options={
                "verbose_name": "ved\xfaci",
                "proxy": True,
                "verbose_name_plural": "ved\xfaci",
            },
            bases=("events.invitation",),
        ),
        migrations.AlterUniqueTogether(name="invitation", unique_together=set([("event", "user")])),
    ]
