from django.db import models
import uuid

class Bolt_Requirements(models.Model):
  
    UUID = models.UUIDField(primary_key=True, verbose_name="UUID",   default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100,  default= 'Not defined', editable=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey("BoltMan.ProjectUser_BoltMan_Ref", models.SET_NULL, blank=True,null=True,)

    meaf = models.FloatField(editable=True, verbose_name= "Maximum External Axial Force (N)", default= 1)
    mesf = models.FloatField(editable=True, verbose_name= "Maximum External Shear Force (N)", default= 1)
    maxtemp = models.IntegerField(verbose_name="Maximum Temperature (°C)", default= 70)  
    mintemp = models.IntegerField(verbose_name="Minimum Temperature (°C)", default= -40 )  

    EXTERNAL_LOADING_CLASS = [
    ('CS', ('Concentric - Static')),
    ('ES', ('Eccentric - Static')),
    ('CD', ('Concentric - Dynamic')),
    ('ED', ('Eccentric - Dynamic')),
    ('TR', ('Transverse')),
    ]
    elc= models.CharField(choices=EXTERNAL_LOADING_CLASS, verbose_name="External Loading Class", max_length=32, default='CS')  
    class Meta:
        app_label = 'BoltMan'
    def __str__(self):
        return 'Class' + str(self.bolt_class) + ' - M_axial ' + str(self.meaf) + 'N - M_shear '  + str(self.mesf) + 'N'
    

def on_create_default_requirement():
  settings = Bolt_Requirements(name= "default")
  settings.save()
  return settings.UUID