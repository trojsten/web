from django.contrib import admin

from easy_select2.widgets import Select2, Select2Multiple

from trojsten.results.models import *


class FrozenResultsAdmin(admin.ModelAdmin):
    list_display = ('round', 'category', 'is_single_round')

    formfield_overrides = {
        models.ForeignKey: {'widget': Select2()},
    }


class FrozenPointsAdmin(admin.ModelAdmin):
    list_display = ('task', 'description_points', 'source_points')

    formfield_overrides = {
        models.ForeignKey: {'widget': Select2()},
    }


class FrozenUserResultAdmin(admin.ModelAdmin):
    list_display = (
        'frozenresults', 'fullname', 'rank', 'school_year', 'school',
        'previous_points', 'sum',
    )

    formfield_overrides = {
        models.ForeignKey: {'widget': Select2()},
        models.ManyToManyField: {'widget': Select2Multiple()},
    }


admin.site.register(FrozenResults, FrozenResultsAdmin)
admin.site.register(FrozenPoints, FrozenPointsAdmin)
admin.site.register(FrozenUserResult, FrozenUserResultAdmin)
