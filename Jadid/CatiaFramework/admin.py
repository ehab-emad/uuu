from django.contrib import admin
from CatiaFramework.models import *
# Register your models here.

class MyModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'type')
    list_filter = ('type',)

admin.site.register(Workflow_Object, MyModelAdmin)



admin.site.register(Workflow)
admin.site.register(Workflow_Stage)
admin.site.register(Workflow_Action)

admin.site.register(DotNet_ProjectFolder)
admin.site.register(DotNet_Component)