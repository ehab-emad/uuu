from django.contrib import admin
from NormMan.models import *
# Register your models here.

class CustomNormParts_Subgroup_admin(admin.ModelAdmin):
   list_display = ['id', 'name',]
   class Meta:
      model = Component_Group_Level

admin.site.register(Component_Group_Level)
