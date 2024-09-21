from django.db import models
from website.generate_pk import generate_pk
from EcoMan.scripts import get_random_color
from django.core.validators import MinValueValidator
from django.dispatch import receiver
from django.db.models.signals import post_save
import uuid
NONNEGATIVE_VALIDATOR = [MinValueValidator(0),]
class Bolted_Part(models.Model):   #should be renamed to Lca_Part
    UUID = models.UUIDField(primary_key=True, verbose_name="UUID",   default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100,  default= 'Not defined', editable=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey("EcoMan.ProjectUser_EcoMan_Ref", models.SET_NULL, blank=True,null=True,)
    part_model =  models.ForeignKey("ConceptMan.Part", on_delete=models.CASCADE, blank=True, null=True)
    is_active = models.BooleanField(verbose_name= "Is Active", default=True)  

    color = models.CharField(max_length=7,  default= get_random_color, editable=True, blank=False)
    notes = models.CharField(max_length=600,  default= "Not defined", editable=True, blank=True)
    project_model=models.ForeignKey("EcoMan.Project_EcoMan_Ref", verbose_name="Project", on_delete=models.CASCADE, help_text ="Select a project for part", default=None, blank=True, null=True, )
    thickness = models.FloatField(verbose_name= "Thread size:", default = 0, validators=NONNEGATIVE_VALIDATOR,)
    material = models.ForeignKey("BoltMan.Bolt_Material", models.SET_NULL, blank=True,null=True,)
    def get_weight_conceptman(self, units="KILOGRAMS"):
        if units =="KILOGRAMS":
            try:
                return self.part_model.weight
            except:
                return 0
        elif units =="GRAMS":
            try:
                return self.part_model.weight * 1000
            except:
                return 0           

  