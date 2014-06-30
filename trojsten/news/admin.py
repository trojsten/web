from django.contrib import admin

from trojsten.news.models import Entry


class EntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'pub_date', 'author')
    prepopulated_fields = {'slug': ['title']}
    exclude = ('author',)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
        obj.save()

admin.site.register(Entry, EntryAdmin)
