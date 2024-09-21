
from django.db import models
from datetime import datetime
from website.generate_pk import generate_pk
from django.conf import settings
from EcoMan.models.lca_property import Lca_Property
from .lca_part import Lca_Part
from ConceptMan.models import Part
from django.shortcuts import get_object_or_404
import json
from django.core.validators import MinValueValidator, MaxValueValidator

class Analysis_Settings(models.Model):


   id = models.CharField(default=generate_pk, primary_key=True, max_length=255, unique=True)
   name = models.CharField(max_length=100,  default= 'Settings', editable=True, blank=True)
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)
   owner = models.ForeignKey("EcoMan.ProjectUser_EcoMan_Ref", models.SET_NULL, blank=True,null=True,)
   primary_property = models.ForeignKey("EcoMan.Lca_Property", verbose_name="Primary Property Of Interest",  on_delete = models.SET_DEFAULT,  default=Lca_Property.get_default_pk, related_name='%(class)s_primary')
   secondary_properties = models.ManyToManyField("EcoMan.Lca_Property", verbose_name="Secondary Properties of Interst", blank=True, related_name='%(class)s_secondary')

   PROTECTIONCLASS_CHOICES= [
    ("PUBLIC", ("Public")),
    ("INTERNAL", ("Internal")),
    ("CONFIDENTIAL", ("Confidential")),
    ("STRICTLY_CONFIDENTIAL", ("Strictly Confidential")),
    ]
   protection_class = models.CharField(choices=PROTECTIONCLASS_CHOICES, verbose_name="Analysis protection class",max_length=100, default="CONFIDENTIAL",)




   #settings
   is_public = models.BooleanField(default =False, verbose_name="Job will be visible for other colleagues within the same project" )
   is_automotive = models.BooleanField(default =False, verbose_name="Job functionality tailored as automotive application" )
   is_playground = models.BooleanField(default =False, verbose_name="Job will be a comparison not visible as two column")
   include_upstream = models.BooleanField(default =True, verbose_name="Manufacturing Emissions includes upstream")
   include_core = models.BooleanField(default =True, verbose_name="Manufacturing Emissions includes core")
   include_downstream = models.BooleanField(default =True, verbose_name="Manufacturing Emissions includes downstrem")
   include_circularity = models.BooleanField(default =True, verbose_name="Manufacturing Emissions includes circularity")
   include_utilisation = models.BooleanField(default =True, verbose_name="Manufacturing Emissions includes vehicle utilisation")


   #settings #report
   report_include_object_ids = models.BooleanField(default =True, verbose_name="Report includes object IDs")
   report_include_title_and_summ_pages = models.BooleanField(default =True, verbose_name="Report includes title and summary page")
   report_include_part_list_pages = models.BooleanField(default =True, verbose_name="Report includes detailed parts lists")
   report_include_processes_list_pages = models.BooleanField(default =True, verbose_name="Report includes detailed process lists")
   report_include_goal_definition = models.BooleanField(default =True, verbose_name="Report includes decription of goal definition")
   report_include_scope_definition = models.BooleanField(default =True, verbose_name="Report includes description of scope definition")
   report_is_anonymized = models.BooleanField(default =True, verbose_name="User personal id visible")



   VISUALISATION_CHOICES= [
   ("ROWS", ("Expandable Menus")),
   ("ICONS", ("Icons")),
   ]

   process_visualisation = models.CharField(choices=VISUALISATION_CHOICES, verbose_name="Processes Visualisation Style",max_length=32, default="ROWS",)

   WEIGHT_UNIT_CHOICES= [
   ("KILOGRAMS", ("Kilograms [kg]")),
   ("GRAMS", ("Grams [g]")),
   ]

   weight_units = models.CharField(choices=WEIGHT_UNIT_CHOICES, verbose_name="Weight unit",max_length=32, default="KILOGRAMS",)
   weight_decimal_points = models.IntegerField(verbose_name="Decimal Points For Weight", default =3, validators=[MinValueValidator(0),MaxValueValidator(6)])



   def as_list(self):
      class Settings:
         def __init__(self, name, verbose, value):
            self.name = name
            self.verbose = verbose
            self.value = value

      data_list = []
      for f in self._meta.get_fields():
         if f.name == 'analysis_comparison' or f.name == 'analysis':
            continue
         data_list.append(Settings(
            f.name,
            self._meta.get_field(f.name).verbose_name,
            getattr(self, f.name)
         ))

      return data_list
   
   class Meta:
        app_label = 'EcoMan'
   def __str__(self):
        return str(self.name)



def on_create_default_settings():
    settings = Analysis_Settings()
    settings.save()
    return settings.pk