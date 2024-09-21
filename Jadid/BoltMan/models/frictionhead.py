from django.db import models
import uuid

class Friction_Head(models.Model):
    UUID = models.UUIDField(primary_key=True, verbose_name="UUID",   default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100,  default= 'Not defined', editable=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey("BoltMan.ProjectUser_BoltMan_Ref", models.SET_NULL, blank=True,null=True,)



    mat_1_name = models.CharField(max_length=100, verbose_name= "Material 1",  editable=True, default= None)
    mat_2_name = models.CharField(max_length=100, verbose_name= "Material 2",  editable=True, default= None)
    plating = models.CharField(max_length=100, verbose_name= "Plating", editable=True, default= None)
    colour = models.CharField(max_length=100, verbose_name= "Colour", editable=True, default= None)
    lubrication = models.CharField(max_length=500, verbose_name= "Lubrication", editable=True, default= None)
    friction_av=models.FloatField(editable=True, verbose_name= "Avarage friction", default= None)
    friction_min=models.FloatField(editable=True, verbose_name= "Minimum friction", default= None)
    friction_max=models.FloatField(editable=True, verbose_name= "Maximum friction", default= None)
    source = models.CharField(max_length=100, verbose_name= "Source", editable=True, default= None)
    notes = models.CharField(max_length=500, verbose_name= "Notes", editable=True, default= None)
    class Meta:
        app_label = 'BoltMan'
    def __str__(self):
        return 'Surface1: ' +str(self.mat_1_name) + ',' + ' | Surface2:' +  str(self.mat_2_name) + '|Friciton av:' + str(self.friction_av)