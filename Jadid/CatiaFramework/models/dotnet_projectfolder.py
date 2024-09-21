from django.db import models
from decimal import *
import os, json, uuid
from pathlib import Path
from .help_functions import *
from pathlib import Path
from CatiaFramework.scripts import *
import os


class DotNet_ProjectFolder(models.Model):
    UUID = models.UUIDField(primary_key=True, verbose_name="UUID",   default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=1000,   editable=True, blank=True,null=True,)
    description = models.CharField(max_length=1000,   editable=True, blank=True,null=True,)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey("CatiaFramework.ProjectUser_CatiaFramework_Ref", models.SET_NULL, blank=True,null=True,)
    is_public = models.BooleanField(default =False, verbose_name="Job will be visible for other colleagues within the same project" )
    thumbnail = models.ImageField(upload_to ='uploads/', null=True, blank=True, verbose_name = "Part Image")
    gif = models.ImageField(upload_to ='uploads/', null=True, blank=True, verbose_name = "Part Image")
    project_model=models.ForeignKey("CatiaFramework.Project_CatiaFramework_Ref", verbose_name="Project", on_delete=models.CASCADE, help_text ="Select a a project for Shared Component", default=None, blank=True, null=True,)

    group_depth_level = models.IntegerField(default=0)
    parent_folder = models.ForeignKey("CatiaFramework.DotNet_ProjectFolder", verbose_name="Parent Modeule", on_delete=models.CASCADE,  null=True, blank=True, )  
    dotnet_components = models.ManyToManyField("CatiaFramework.DotNet_Component", verbose_name=".Net Components", blank=True)
    ACCESSIBILITY_CHOICE= [
    ("PRIVATE", ("Private")),
    ("DATABASE_USERS", ("Database Users")),
    ("PROJECT_USERS", ("Project Users")),    
    ]

    accessibility = models.CharField(choices=ACCESSIBILITY_CHOICE, default="PRIVATE",  max_length=50)

    def as_dict(self) ->dict:
        '''convert instance to dictionary
        '''
        from django.forms import model_to_dict
        entry = {}

        entry.update({"UUID": str(self.UUID)})
        entry.update(model_to_dict(self))

        for field in DotNet_ProjectFolder._meta.get_fields():
            if type(field).__qualname__ == "ManyToManyField":
                entry[field.attname] =[str(object.UUID) for object in entry[field.attname]]
        return entry

    class Meta:
        app_label = 'CatiaFramework'
    def __str__(self):
        return str(f'DotNet_Module: {str(self.UUID)}')

