from django.db import models
from EcoMan.models import Lca_Part
from django.urls import reverse
from django.dispatch import receiver
from django.db.models.signals import post_save , pre_save  
from website.generate_pk import generate_pk
from django.conf import settings
from website.models import Vehicle
from EcoMan.models import Lca_Part
from EcoMan.models import Analysis
from EcoMan.scripts import get_random_color
from django.core.validators import MinValueValidator, MaxValueValidator
NONNEGATIVE_VALIDATOR = [MinValueValidator(0),]
class Circularity_Process(models.Model):
    id = models.CharField(default=generate_pk, primary_key=True, max_length=255, unique=True)    
    name = models.CharField(max_length=100,  default= 'Not defined', editable=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey("EcoMan.ProjectUser_EcoMan_Ref", models.SET_NULL, blank=True,null=True,)


    #specific elements
    
    lifetimeinkm = models.IntegerField(editable=True, verbose_name= "Part lifetime in km", default = 150000, blank=True, null=True, validators=NONNEGATIVE_VALIDATOR,) 
    ispartreused = models.BooleanField(default =False,)    
    notes = models.CharField(max_length=100,  default= 'Put your comment here...', editable=True, blank=True)

    service_intervals =[] # non database property (will not be saved in database)

    def check_bonusmalus(self, vehicle, tacho, calc_interval): 
        lca_step = Lca_Part.objects.filter(circularity_process_model__pk=self.pk).get()
         
        service_modulo = tacho % self.lifetimeinkm #check how far away we are from the service interval

        if service_modulo < calc_interval & tacho > 0.1 * calc_interval: #get rid of interval at tacho = 0
            bonusmalus = True
        else:
            bonusmalus = False

        return bonusmalus

    class Meta:
        app_label = 'EcoMan'
    def __str__(self):
        return str(self.name) 

    @receiver(pre_save, sender=Lca_Part)
    def create_circularity_process(sender, instance,  **kwargs):
        if instance._state.adding:
              Circularity_Process.objects.create(lca_part = instance)
        else:
            if hasattr(instance, 'circularity_process_model') and instance.circularity_process_model is None:
                  Circularity_Process.objects.create(lca_part = instance)