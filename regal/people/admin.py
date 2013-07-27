from django.contrib import admin
from regal.people.models import *

def createAlfabetFilter(field, requestget):
    kw = '__startswith'
    selected_choice = requestget.get(field+kw, 'All')
    choices = [{'title' : 'All', 'link':'?' , 'active':selected_choice == 'All'}]
    for x in range(26):
        letter = chr(ord('A')+x)
        choices.append({'title' : letter, 'link':'?'+field+kw+'='+letter, 'active':selected_choice == letter})
    return choices


class PersonAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'surname', 'email')
    list_filter = ['studies_in', 'teaches_in']
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['choices'] = createAlfabetFilter('surname', request.GET)
        return super(PersonAdmin, self).changelist_view(request, extra_context=extra_context)

class SchoolAdmin(admin.ModelAdmin):
    list_display = ('abbr', 'name', 'address','get_town')
    
    #does not work if because get_town is not field
    #TODO fix
    #list_filter = ['get_town',]

admin.site.register(Address)
admin.site.register(Person,PersonAdmin)
admin.site.register(School,SchoolAdmin)
admin.site.register(Student)
admin.site.register(Teacher)
