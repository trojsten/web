# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.encoding import force_text
from easy_select2 import select2_modelform
from import_export import fields, resources
from import_export.admin import ExportMixin

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
    form = select2_modelform(Event)
    list_display = ("name", "type", "place", "start_time", "end_time")
    inlines = [EventParticipantInline, EventOrganizerInline]

    def get_queryset(self, request):
        user_groups = request.user.groups.all()
        events_type_lst = EventType.objects.filter(organizers_group__in=user_groups)
        return super(EventAdmin, self).get_queryset(request).filter(type__in=events_type_lst)


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
