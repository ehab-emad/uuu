from django.db import models
from django.urls import reverse
from decimal import *
from website.generate_pk import generate_pk
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
import os, json, uuid
from pathlib import Path
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator, MaxLengthValidator
from EcoMan.QLCA_Idemat_Calculation import import_lca_constant
from .help_functions import *
from pathlib import Path
from NormMan.scripts import *
PERCENTAGE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(100)]
NONNEGATIVE_VALIDATOR = [MinValueValidator(0),]
import os


class Component_Group_Level(models.Model):
    UUID = models.CharField(primary_key=True, verbose_name="UUID",   default=uuid.uuid4, editable=False, max_length= 200)   
    name = models.CharField(max_length=100,  default= 'Not defined', editable=True,)
    name_de = models.CharField(max_length=100,  default= 'Not defined', editable=True,)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.CharField(max_length=100,  default= 'Put your comment here...', editable=True, blank=True)
    thumbnail = models.ImageField(upload_to = get_upload_to, null=True, blank=True, verbose_name = "Part Image")
    stl_thumbnail = models.FileField(upload_to = get_upload_to, blank= True)   
    data_path = models.FileField(max_length=10000, blank= True) #os.path.join("media/norm_parts/db_structure/") 
    group_depth_level = models.IntegerField(default=0)
    parent_group = models.ForeignKey("NormMan.Component_Group_Level", verbose_name="Parent Category of the Group", on_delete=models.CASCADE,  null=True,)  

    normparts_shared_components = models.ManyToManyField("NormMan.NormParts_Shared_Component", verbose_name="Shared Component", blank=True)

    def as_dict(self) ->dict:
        '''this function will create custom instance process dictionary
        '''
        from django.forms import model_to_dict
        entry = {}

        entry.update({"UUID": self.UUID})
        entry.update(model_to_dict(self))

        for field in Component_Group_Level._meta.get_fields():
            if type(field).__qualname__ == "ManyToManyField":
                entry[field.attname] =[object.UUID for object in entry[field.attname]]
        return entry

    def save(self, *args, **kwargs):
        Path(self.data_path.path).mkdir(parents=True, exist_ok=True)
        super(Component_Group_Level, self).save(*args, **kwargs)         
        #generate json for other frameworks
        entry = {}
        entry[type(self).__name__] = self.as_dict()
        out_file = open(os.path.join(self.data_path.path, "meta.json"), "w")
        json.dump(entry, out_file, indent = 6, cls=ExtendedEncoder)
        out_file.close()


    class Meta:
        app_label = 'NormMan'
    def __str__(self):
        return str(self.name) 

