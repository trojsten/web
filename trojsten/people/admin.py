# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.core.exceptions import PermissionDenied
from django.db import models
from django.forms import ModelForm
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.encoding import force_text
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from easy_select2 import select2_modelform
from easy_select2.widgets import Select2
from import_export import fields, resources
from import_export.admin import ExportMixin

from trojsten.contests.models import Competition, Semester
from trojsten.people.admin_urls import submitted_tasks_urls
from trojsten.submit.models import Submit
from trojsten.utils.utils import attribute_format

from . import constants
from .forms import MergeForm
from .helpers import get_similar_users, merge_users
from .models import Address, DuplicateUser, User, UserProperty, UserPropertyKey


class AddressAdmin(admin.ModelAdmin):
    list_display = ("street", "town", "postal_code", "country")
    search_fields = ("street", "town", "postal_code", "country")


class UserPropertyInLine(admin.TabularInline):
    model = UserProperty
    extra = 0


class StaffFilter(admin.SimpleListFilter):
    title = "postavenia"
    parameter_name = "is_staff"

    def lookups(self, request, model_admin):
        return (("veduci", "Vedúci"), ("ucastnik", "Účastník"))

    def queryset(self, request, queryset):
        if self.value() == "veduci":
            return queryset.filter(is_staff=True)
        elif self.value() == "ucastnik":
            return queryset.filter(is_staff=False)
        else:
            return queryset


class ActiveInCompetitionFilter(admin.SimpleListFilter):
    title = "účasti v súťaži"
    parameter_name = "competition"

    def lookups(self, request, model_admin):
        return ((c.id, force_text(c)) for c in Competition.objects.all())

    def queryset(self, request, queryset):
        if self.value():
            active_users = Submit.objects.filter(
                task__round__semester__competition__id=self.value()
            ).values_list("user", flat=True)
            return queryset.filter(id__in=active_users)
        else:
            return queryset


class ActiveInSemesterSubFilter(admin.SimpleListFilter):
    title = "účasti v časti"
    parameter_name = "semester"

    def lookups(self, request, model_admin):
        semester = Semester.objects
        if "competition" in request.GET:
            semester = semester.filter(competition__id=request.GET["competition"])
        return ((s.id, force_text(s)) for s in semester.all())

    def queryset(self, request, queryset):
        if self.value():
            active_users = Submit.objects.filter(
                task__round__semester__id=self.value()
            ).values_list("user", flat=True)
            return queryset.filter(id__in=active_users)
        else:
            return queryset


class UsersExport(resources.ModelResource):
    street = fields.Field()
    town = fields.Field()
    postal_code = fields.Field()
    country = fields.Field()

    class Meta:
        model = User
        export_order = fields = (
            "first_name",
            "last_name",
            "birth_date",
            "email",
            "graduation",
            "street",
            "town",
            "postal_code",
            "country",
            "school__verbose_name",
            "school__addr_name",
            "school__street",
            "school__city",
            "school__zip_code",
        )
        widgets = {"birth_date": {"format": "%d.%m.%Y"}}

    def dehydrate_street(self, obj):
        address = obj.get_mailing_address()
        return "" if address is None else address.street

    def dehydrate_town(self, obj):
        address = obj.get_mailing_address()
        return "" if address is None else address.town

    def dehydrate_postal_code(self, obj):
        address = obj.get_mailing_address()
        return "" if address is None else address.postal_code

    def dehydrate_country(self, obj):
        address = obj.get_mailing_address()
        return "" if address is None else str(address.country)


class AdminUserAddForm(ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "school", "graduation"]


class UserAdmin(ExportMixin, DefaultUserAdmin):
    change_form_template = "admin/people/submitted_tasks_button.html"
    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
        "get_school",
        "graduation",
        "get_is_staff",
        "get_groups",
        "is_active",
        "get_properties",
    )
    list_filter = ("groups", StaffFilter, ActiveInCompetitionFilter, ActiveInSemesterSubFilter)
    search_fields = ("username", "first_name", "last_name")

    add_form = AdminUserAddForm

    formfield_overrides = {models.ForeignKey: {"widget": Select2()}}

    add_fieldsets = ((None, {"fields": ("first_name", "last_name", "school", "graduation")}),)

    fieldsets = (
        (None, {"fields": ("username",)}),
        (
            _("Personal info"),
            {"fields": ("first_name", "last_name", "email", "gender", "birth_date")},
        ),
        (_("Address"), {"fields": ("home_address", "mail_to_school", "mailing_address")}),
        (_("School"), {"fields": ("school", "graduation")}),
        (_("Password"), {"fields": ("password",)}),
    )
    superuser_fieldsets = fieldsets + (
        (
            _("Permissions"),
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    inlines = (UserPropertyInLine,)

    resource_class = UsersExport

    def get_queryset(self, request):
        qs = super(UserAdmin, self).get_queryset(request)
        return qs.select_related("school").prefetch_related("groups", "properties__key")

    def get_fieldsets(self, request, obj=None):
        if obj is None or not request.user.is_superuser:
            return super(UserAdmin, self).get_fieldsets(request, obj)
        else:
            return self.superuser_fieldsets

    def get_groups(self, obj):
        return ", ".join(force_text(x) for x in obj.groups.all())

    get_groups.short_description = "skupiny"

    get_is_staff = attribute_format(attribute="is_staff", description="vedúci", boolean=True)

    def get_school(self, obj):
        if obj.school:
            if obj.school.has_abbreviation:
                show = obj.school.abbreviation
            else:
                show = obj.school.verbose_name
            return format_html(
                '<span title="{}">{}</span>',
                escape(force_text(obj.school)),
                escape(force_text(show)),
            )

    get_school.short_description = "škola"
    get_school.admin_order_field = "school"
    get_school.allow_tags = True

    def get_properties(self, obj):
        return mark_safe("<br />".join(escape(force_text(x)) for x in obj.properties.all()))

    get_properties.short_description = "dodatočné vlastnosti"
    get_properties.allow_tags = True

    def get_urls(self):
        return submitted_tasks_urls + super(UserAdmin, self).get_urls()

    def user_change_password(self, request, id, form_url=""):
        if not request.user.is_superuser:
            raise PermissionDenied
        return super(UserAdmin, self).user_change_password(request, id, form_url)


class DuplicateUserAdmin(admin.ModelAdmin):
    form = select2_modelform(DuplicateUser)
    list_display = ("user", "status")
    ordering = ("status", "user")
    list_filter = ("status",)

    def get_urls(self):
        urls = super(DuplicateUserAdmin, self).get_urls()
        my_urls = [
            url(
                r"^merge/(?P<target_user_id>[0-9]+)/(?P<candidate_id>[0-9]+)$",
                admin.site.admin_view(self.merge_users_view),
                name="duplicate_user_merge",
            )
        ]
        return my_urls + urls

    def change_view(self, request, object_id, form_url="", extra_context=None):
        target_user = DuplicateUser.objects.get(pk=object_id).user
        merge_candidates = get_similar_users(target_user)
        extra_context = extra_context or {}
        extra_context["target_user"] = target_user
        extra_context["merge_candidates"] = merge_candidates
        return super(DuplicateUserAdmin, self).change_view(
            request, object_id, form_url, extra_context=extra_context
        )

    def merge_users_view(self, request, target_user_id, candidate_id, *args, **kwargs):
        user = get_object_or_404(User, pk=target_user_id)
        candidate = get_object_or_404(User, pk=candidate_id)
        if request.method == "POST":
            form = MergeForm(user, candidate, request.POST)
            if form.is_valid():
                target_user, source_user = (
                    (user, candidate) if form.cleaned_data["id"] == user.id else (candidate, user)
                )

                src_fields = [
                    key
                    for key, val in form.cleaned_data.items()
                    if key != "id"
                    and not key.startswith(constants.USER_PROP_PREFIX)
                    and int(val) == source_user.pk
                ]
                src_user_props = [
                    int(key[len(constants.USER_PROP_PREFIX) :])
                    for key, val in form.cleaned_data.items()
                    if key.startswith(constants.USER_PROP_PREFIX) and int(val) == source_user.pk
                ]

                merge_users(target_user, source_user, src_fields, src_user_props)
                messages.add_message(request, messages.SUCCESS, _("Users merged succesfully."))
                return redirect("admin:people_duplicateuser_change", target_user.duplicateuser.pk)
        else:
            form = MergeForm(user, candidate)
        context = {
            "user": user,
            "candidate": candidate,
            "form": form,
            "opts": self.model._meta,
            "has_change_permission": self.has_change_permission(request, user.duplicateuser),
        }
        return render(request, "admin/people/duplicateuser/merge_duplicate_users.html", context)


admin.site.register(Address, AddressAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(DuplicateUser, DuplicateUserAdmin)
admin.site.register(UserPropertyKey)
