# -*- coding: utf-8 -*-

from django.contrib import admin

from trojsten.rules.models import KSPLevel


class KSPLevelAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "new_level",
        "source_semester",
        "source_camp",
        "last_semester_before_level_up",
    )
    search_fields = ("user__username", "user__first_name", "user__last_name")
    list_filter = (
        ("source_semester", admin.RelatedOnlyFieldListFilter),
        ("source_camp", admin.RelatedOnlyFieldListFilter),
    )


admin.site.register(KSPLevel, KSPLevelAdmin)
