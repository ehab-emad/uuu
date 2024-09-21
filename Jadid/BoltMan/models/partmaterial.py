from django.db import models
from django.conf import settings
import uuid

class Part_Material(models.Model):
    UUID = models.UUIDField(primary_key=True, verbose_name="UUID",   default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100,  default= 'Not defined', editable=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey("BoltMan.ProjectUser_BoltMan_Ref", models.SET_NULL, blank=True,null=True,)

    aisi = models.CharField(max_length=20,  default= 'Not defined', editable=True, blank=True, verbose_name= "AISI")
    din = models.CharField(max_length=20,  default= 'Not defined', editable=True, blank=True, verbose_name= "DIN")
    bs = models.CharField(max_length=20,  default= 'Not defined', editable=True, blank=True, verbose_name= "BS")
    af = models.CharField(max_length=20,  default= 'Not defined', editable=True, blank=True, verbose_name= "AF")
    uni = models.CharField(max_length=20,  default= 'Not defined', editable=True, blank=True, verbose_name= "UNI")
    une = models.CharField(max_length=20,  default= 'Not defined', editable=True, blank=True, verbose_name= "UNE")
    jis = models.CharField(max_length=20,  default= 'Not defined', editable=True, blank=True, verbose_name= "JIS")
    csn = models.CharField(max_length=20,  default= 'Not defined', editable=True, blank=True, verbose_name= "CSN")
    poisonsratio = models.FloatField(editable=True, verbose_name= "Poisons Ratio")
    moeit = models.FloatField(editable=True, verbose_name= "Modulus of elasticity in tension")
    hec =  models.FloatField(editable=True, verbose_name= "Heat expansion coefficient (10^-6/°C)")
    density = models.FloatField(editable=True, verbose_name= "Density (kg/m3)")
    uts = models.FloatField(editable=True, verbose_name= "Ultimate Tensile Strength, Su(Mpa)")
    ys = models.FloatField(editable=True, verbose_name= "Yield strength, Sy(Mpa)")
    ppubh =models.FloatField(editable=True, verbose_name= "Permitted pressure under bolt head (Mpa)")
    sh = models.FloatField(editable=True, verbose_name= "Shear strength (Mpa)")


    ppubh = models.FloatField(editable=True, verbose_name= "Permitted pressure under bolt head (MPa)")
    mpfpp = models.FloatField(editable=True, verbose_name= "Max. preload from permitted pressure (N)")


    STEEL = 'Steel'
    ALUMINIUM = 'Aluminium'
    CASTIRON = 'Castiron'
    DIFFERENT = 'Different'
    PLASTIC = 'Plastic'

    MATGROUP = [
        (STEEL, ('Steel')),
        (ALUMINIUM, ('Aluminium/Aluminium alloy')),
        (CASTIRON, ('Cast iron')),
        (DIFFERENT, ('Different')),
        (PLASTIC, ('Plastic')),        
    ]
    materialgroup = models.CharField(choices=MATGROUP, max_length=32, default=DIFFERENT)

    class Meta:
        app_label = 'BoltMan'
    def __str__(self):
        return str(self.name)