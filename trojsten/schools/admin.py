from django.contrib import admin

from import_export import resources
from import_export.admin import ExportMixin

from .models import School


class SchoolExport(resources.ModelResource):
    class Meta:
        model = School
        export_order = fields = (
            "verbose_name",
            "abbreviation",
            "addr_name",
            "street",
            "city",
            "zip_code",
        )


class SchoolAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ("verbose_name", "abbreviation", "addr_name", "street", "city", "zip_code")
    search_fields = ("verbose_name", "abbreviation", "addr_name", "street", "city", "zip_code")
    resource_class = SchoolExport


admin.site.register(School, SchoolAdmin)
