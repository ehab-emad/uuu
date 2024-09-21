from django.db import models
from website.generate_pk import generate_pk
from django.conf import settings


class Manufacturing_Process(models.Model):
    id = models.CharField(default=generate_pk, primary_key=True, max_length=255, unique=True)    
    name = models.CharField(max_length=100,  default= 'Not defined', editable=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey("ConceptMan.ProjectUser_ConceptMan_Ref", models.SET_NULL, blank=True,null=True,)

    class Meta:
        app_label = 'ConceptMan'
    def __str__(self):
        return str(self.name) 