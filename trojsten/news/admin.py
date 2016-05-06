from django.contrib import admin
from easy_select2.widgets import Select2Multiple

from trojsten.news.models import *


class EntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'pub_date', 'author')
    readonly_fields = ('slug',)
    exclude = ('author',)

    formfield_overrides = {
        models.ManyToManyField: {'widget': Select2Multiple()}
    }

    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
        obj.save()

admin.site.register(Entry, EntryAdmin)
