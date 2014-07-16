from django.contrib import admin

from trojsten.news.models import Entry, Label


class EntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'pub_date', 'author')
    readonly_fields = ('slug',)
    exclude = ('author',)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
        obj.save()

admin.site.register(Entry, EntryAdmin)
admin.site.register(Label)
