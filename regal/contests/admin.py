from django.contrib import admin
from regal.contests.models import *

class YearInline(admin.TabularInline):
    model = Year
    fk_name = 'competition'
    readonly_fields = ('number',)
    

class CompetitionAdmin(admin.ModelAdmin):
    fields = ('name', ('informatics', 'math', 'physics'))
    inlines = [
         YearInline,
    ]

admin.site.register(Competition, CompetitionAdmin)
admin.site.register(Year)
admin.site.register(Round)
admin.site.register(Task)
