from django.db import models 
import uuid

class Bolt_Material(models.Model):
    UUID = models.UUIDField(primary_key=True, verbose_name="UUID",   default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100,  default= 'Not defined', editable=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey("BoltMan.ProjectUser_BoltMan_Ref", models.SET_NULL, blank=True,null=True,)
    
    poisonsratio = models.FloatField(editable=True, verbose_name= "Poisons Ratio", default = 0)
    moeit = models.FloatField(editable=True, verbose_name= "Modulus of elasticity in tension", default = 0)
    hec =  models.FloatField(editable=True, verbose_name= "Heat expansion coeficient", default = 0)
    density = models.FloatField(editable=True, verbose_name= "Density", default = 0)
    ys20 = models.FloatField(editable=True, verbose_name= "Yield strength at 20°C(Mpa)", default = 0)
    ys100 = models.FloatField(editable=True, verbose_name= "Yield strength at 100°C(Mpa)", default = 0)
    ys200 = models.FloatField(editable=True, verbose_name= "Yield strength at 200°C(Mpa)", default = 0)
    ys250 = models.FloatField(editable=True, verbose_name= "Yield strength at 250°C(Mpa)", default = 0)
    ys300 = models.FloatField(editable=True, verbose_name= "Yield strength at 300°C(Mpa)", default = 0)
    uts = models.FloatField(editable=True, verbose_name= "Ultimate Tensile Strength, Su(Mpa)", default = 0)
    es = models.FloatField(editable=True, verbose_name= "Endurance Strength (Mpa)", default = 0)
    vh_min = models.FloatField(editable=True, verbose_name= "Minimum Vickers Hardness HV30", default = 0)
    vh_max = models.FloatField(editable=True, verbose_name= "Maximum Vickers Hardness HV30", default = 0)
    ss = models.FloatField(editable=True, verbose_name= "Shear Strength (MPa) [DIN EN ISO 898-1]", default = 0)

    STEEL = 'Steel'
    ALUMINIUM = 'Aluminium'
    DIFFERENT = 'Different'
    PLASTIC = 'Plastic'

    MATGROUP = [
        (STEEL, ('Steel')),
        (ALUMINIUM, ('Aluminium/Aluminium alloy')),
        (DIFFERENT, ('Different')),
        (PLASTIC, ('Plastic')),        
    ]
    materialgroup = models.CharField(choices=MATGROUP, max_length=32, default=DIFFERENT)

    class Meta:
        app_label = 'BoltMan'

    def __str__(self):
        return str(self.name)