# -*- coding: utf-8 -*-

import re

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.db.models import Value as V
from django.db.models.functions import Concat, Lower
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.encoding import force_text
from easy_select2 import select2_modelform
from import_export import fields, resources
from import_export.admin import ExportMixin

from trojsten.people.models import User

from .models import Event, EventOrganizer, EventParticipant, EventPlace, EventType


class EventTypeAdmin(admin.ModelAdmin):
    form = select2_modelform(EventType)
    list_display = ("name", "organizers_group", "get_sites", "is_camp")

    def get_sites(self, obj):
        return ", ".join(force_text(x) for x in obj.sites.all())

    get_sites.short_description = "zobraziť na"


class EventParticipantInline(admin.TabularInline):
    model = EventParticipant
    extra = 1
    fields = (("user", "type", "going"),)
    verbose_name = "účastník"
    verbose_name_plural = "účastníci"
    autocomplete_fields = ("user",)

    def get_queryset(self, request):
        qs = super(EventParticipantInline, self).get_queryset(request)
        return qs.exclude(type=EventParticipant.ORGANIZER).select_related("user", "event")

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "type":
            kwargs["choices"] = [
                choice
                for choice in db_field.get_choices(include_blank=False)
                if choice[0] != EventParticipant.ORGANIZER
            ]
        return super(EventParticipantInline, self).formfield_for_choice_field(
            db_field, request, **kwargs
        )


class EventOrganizerInline(admin.TabularInline):
    model = EventOrganizer
    fields = ("user",)
    extra = 1
    autocomplete_fields = ("user",)

    def get_queryset(self, request):
        qs = super(EventOrganizerInline, self).get_queryset(request)
        return qs.select_related("user", "event")


class EventAdmin(admin.ModelAdmin):
    change_form_template = "admin/event_change.html"
    form = select2_modelform(Event)
    list_display = ("name", "type", "place", "start_time", "end_time")
    inlines = [EventParticipantInline, EventOrganizerInline]

    def get_queryset(self, request):
        user_groups = request.user.groups.all()
        events_type_lst = EventType.objects.filter(organizers_group__in=user_groups)
        return super(EventAdmin, self).get_queryset(request).filter(type__in=events_type_lst)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        if request.method == "POST" and "participants_list" in request.POST:
            raw_data = request.POST.get("participants_list")
            possible_names = [
                element.lower().strip()
                for row in raw_data.split("\n")
                for element in row.split("\t")
                if re.search("\\w.*\\w", element)
            ]
            users = User.objects.annotate(
                full_name=Lower(Concat("first_name", V(" "), "last_name"))
            ).filter(full_name__in=possible_names)
            this_event = Event.objects.get(pk=object_id)
            for user in users:
                EventParticipant.objects.get_or_create(
                    event=this_event, user=user, type=EventParticipant.PARTICIPANT, going=True
                )
            # Redirect back to the change form after processing the form data
            change_url = reverse(
                "admin:%s_%s_change"
                % (
                    Event._meta.app_label,
                    Event._meta.model_name,
                ),
                args=[object_id],
                current_app=self.admin_site.name,
            )
            return HttpResponseRedirect(change_url)

        return super().change_view(request, object_id, form_url, extra_context)


class EventParticipantExport(resources.ModelResource):
    type = fields.Field()

    street = fields.Field()
    town = fields.Field()
    postal_code = fields.Field()
    country = fields.Field()

    class Meta:
        model = EventParticipant
        export_order = fields = [
            "user__first_name",
            "user__last_name",
            "user__birth_date",
            "user__email",
            "street",
            "town",
            "postal_code",
            "country",
            "user__school__verbose_name",
            "type",
            "going",
        ]
        widgets = {"user__birth_date": {"format": "%d.%m.%Y"}}

    def dehydrate_type(self, obj):
        return obj.get_type_display()

    def dehydrate_street(self, obj):
        address = obj.user.get_mailing_address()
        return "" if address is None else address.street

    def dehydrate_town(self, obj):
        address = obj.user.get_mailing_address()
        return "" if address is None else address.town

    def dehydrate_postal_code(self, obj):
        address = obj.user.get_mailing_address()
        return "" if address is None else address.postal_code

    def dehydrate_country(self, obj):
        address = obj.user.get_mailing_address()
        return "" if address is None else str(address.country)


class EventParticipantAdmin(ExportMixin, admin.ModelAdmin):
    form = select2_modelform(EventParticipant)
    list_display = ("event", "user", "type", "going")
    resource_class = EventParticipantExport
    list_filter = ("event", "going", "type")

    def get_queryset(self, request):
        user_groups = request.user.groups.all()
        events_type_lst = EventType.objects.filter(organizers_group__in=user_groups)
        events_lst = Event.objects.filter(type__in=events_type_lst)
        return super(EventParticipantAdmin, self).get_queryset(request).filter(event__in=events_lst)


admin.site.register(EventType, EventTypeAdmin)
admin.site.register(EventPlace)
admin.site.register(Event, EventAdmin)
admin.site.register(EventParticipant, EventParticipantAdmin)
