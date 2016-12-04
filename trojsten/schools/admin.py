from django.contrib import admin

from .models import School


class SchoolAdmin(admin.ModelAdmin):
    list_display = ('verbose_name', 'abbreviation', 'addr_name', 'street', 'city', 'zip_code')
    search_fields = ('verbose_name', 'abbreviation', 'addr_name', 'street', 'city', 'zip_code')


admin.site.register(School, SchoolAdmin)
