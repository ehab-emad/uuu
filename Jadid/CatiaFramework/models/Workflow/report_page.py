from django.db import models
from math import *
from django.db.models import Q
import uuid
from CatiaFramework.models.help_functions import *
from CatiaFramework.scripts import *

class Workflow_Report_Page(models.Model):   #should be LCA_Process

    #standard fields
    UUID = models.UUIDField(primary_key=True, verbose_name="UUID",   default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=1000,   editable=True, blank=True,null=True,)
    description = models.CharField(max_length=1000,   editable=True, blank=True,null=True,)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey("CatiaFramework.ProjectUser_CatiaFramework_Ref", models.SET_NULL, blank=True,null=True,)
    thumbnail = models.ImageField(upload_to ='uploads/', null=True, blank=True, verbose_name = "Thumbnail")
    
  
    
    parent_page = models.ForeignKey("CatiaFramework.Workflow_Stage", verbose_name="Parent Stage", related_name='reportpages_children_pagess', on_delete=models.CASCADE, default=None, blank=True, null = True)
                                                                        
    class Meta:
        app_label = 'CatiaFramework'        

    