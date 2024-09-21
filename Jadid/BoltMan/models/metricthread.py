from django.db import models 
import uuid

class Metric_Thread(models.Model):
    UUID = models.UUIDField(primary_key=True, verbose_name="UUID",   default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100,  default= 'Not defined', editable=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey("BoltMan.ProjectUser_BoltMan_Ref", models.SET_NULL, blank=True,null=True,)

    nominaldiameter = models.PositiveIntegerField(verbose_name= "Nominal Diameter (mm)")
    pitch = models.FloatField(editable=True, verbose_name= "Pitch (mm)")
    pitchdiameter = models.FloatField(editable=True, verbose_name= "Pitch diameter (mm)")
    tensilestressarea = models.FloatField(editable=True, verbose_name= "Tensile Stress Area (mm^2)")
    minordiameter = models.FloatField(editable=True, verbose_name= "Minor Diameter (mm)")
    flankangle = models.FloatField(editable=True, verbose_name= "Flank angle (°)")
    pitch = models.FloatField(editable=True, verbose_name= "Pitch β (°)")
    depth = models.FloatField(editable=True, verbose_name= "Depth (Total height of V Shape) (mm)")
    depthh3 = models.FloatField(editable=True, verbose_name= "Depth h3 (mm)")
    
    nmaxmd = models.FloatField(editable=True, verbose_name= "Nut - Maximum Minor Diameter (mm)")
    sminpd = models.FloatField(editable=True, verbose_name= "Screw - Minimum Pitch Diameter (mm)")
    nmaxpd = models.FloatField(editable=True, verbose_name= "Nut - Maximum Pitch Diameter (mm)")
    sminmd = models.FloatField(editable=True, verbose_name= "Screw - Minimum Major Diameter (mm)")

    sapuls = models.FloatField(editable=True, verbose_name= "Shear Area per unit length - Screw (mm)")
    sapuln = models.FloatField(editable=True, verbose_name= "Shear Area per unit length - Nut (mm)")

    chd = models.FloatField(editable=True, verbose_name= "Clearance hole diameter (mm)")
    nutheight = models.FloatField(editable=True, verbose_name= "Nut height (mm)")

    # helicoils
    helmaxpd = models.FloatField(editable=True, verbose_name= "Helicoil Max pitch diameter (mm)")
    helmd = models.FloatField(editable=True, verbose_name= "Helicoil Major diameter (mm)")    
    helsapul = models.FloatField(editable=True, verbose_name= "Helicoil Shear Area per unit length (mm)") 


    washerheight = models.FloatField(editable=True, verbose_name= "Washer height (mm)") 
    keywidth = models.FloatField(editable=True, verbose_name= "Key-width (mm)") 


    class Meta:
        app_label = 'BoltMan'

    def __str__(self):
        return str(self.name)