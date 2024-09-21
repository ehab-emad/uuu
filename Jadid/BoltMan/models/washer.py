from django.db import models
from django.conf import settings
import uuid

class Washer(models.Model):
    UUID = models.UUIDField(primary_key=True, verbose_name="UUID",   default=uuid.uuid4, editable=False) 
    name = models.CharField(max_length=100,  default= 'Not defined', editable=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey("BoltMan.ProjectUser_BoltMan_Ref", models.SET_NULL, blank=True,null=True,)

    material = models.ForeignKey("BoltMan.Bolt_Material", verbose_name= "Part material", on_delete=models.CASCADE,blank=True,null=True,)
    norm = models.CharField(max_length=15,  default= 'Not defined', blank=True)
    thickness = models.FloatField(editable=True, verbose_name= "Thickness (mm)", default=0)    
    odiameter = models.FloatField(editable=True, verbose_name= "Outside Diameter (mm)", default=0) 
    idiameter = models.FloatField(editable=True, verbose_name= "Inside Diameter (mm)", default=0) 

    FLAT = 'Flat'
    FENDER = 'Fender'
    SPLIT_LOCK = 'Split Lock'
    I_TOOTH_LOCK = 'Internal Tooth Lock'   
    E_TOOTH_LOCK = 'External Tooth Lock'
    FINISHING = 'Finishing'
    CLIPPED = 'Clipped'
    SPRING = 'Spring'
    WAVE = 'Wave'
    SQUARE = 'Square'
    WEDGE_LOCK = 'Wedge Lock'   

    WASHER_CLASS = [
        (FLAT, ('Bolted Joint')),
        (FENDER, ('Fender')),
        (SPLIT_LOCK, ('Split Lock')),
        (I_TOOTH_LOCK, ('Internal Tooth Lock')),
        (E_TOOTH_LOCK, ('External Tooth Lock')),
        (FINISHING, ('Finishing')),
        (CLIPPED, ('Clipped')),
        (SPRING, ('Spring')),
        (WAVE, ('Wave')),
        (SQUARE, ('Square')),
        (WEDGE_LOCK, ('Wedge Lock')),

    ]
    washer_type= models.CharField(choices=WASHER_CLASS, max_length=32, default=FLAT) 

    class Meta:
        app_label = 'BoltMan'

    def __str__(self):
        return str(self.name) 