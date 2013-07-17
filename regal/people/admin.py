from django.contrib import admin
from regal.people.models import *

class PersonAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'surname', 'email')
    list_filter = ['surname',]

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
