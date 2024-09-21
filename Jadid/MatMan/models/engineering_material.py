from django.db import models
#from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from website.generate_pk import generate_pk
from django.conf import settings


class Engineering_Material(models.Model):
    id = models.CharField(default=generate_pk, primary_key=True, max_length=255, unique=True)   
    name = models.CharField(max_length=100,  default= 'Not defined', editable=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey("MatMan.ProjectUser_MatMan_Ref", models.SET_NULL, blank=True,null=True,)
    project_model=models.ForeignKey("MatMan.Project_MatMan_Ref", verbose_name="Project", on_delete=models.CASCADE, help_text ="Select a a project for analysis", default=None, blank=True, )

    #Names
    aisi = models.CharField(max_length=20,  default= 'Not defined', editable=True, blank=True, verbose_name= "AISI")
    din = models.CharField(max_length=20,  default= 'Not defined', editable=True, blank=True, verbose_name= "DIN")
    bs = models.CharField(max_length=20,  default= 'Not defined', editable=True, blank=True, verbose_name= "BS")
    af = models.CharField(max_length=20,  default= 'Not defined', editable=True, blank=True, verbose_name= "AF")
    uni = models.CharField(max_length=20,  default= 'Not defined', editable=True, blank=True, verbose_name= "UNI")
    une = models.CharField(max_length=20,  default= 'Not defined', editable=True, blank=True, verbose_name= "UNE")
    jis = models.CharField(max_length=20,  default= 'Not defined', editable=True, blank=True, verbose_name= "JIS")
    csn = models.CharField(max_length=20,  default= 'Not defined', editable=True, blank=True, verbose_name= "CSN")

    name_1 = models.CharField(max_length=30, verbose_name= "Name: ",  editable=True, default= None, blank=True, null=True)
    name_2 = models.CharField(max_length=30, verbose_name= "Alternative Name 1:",  editable=True, default= None, blank=True, null=True)
    name_3 = models.CharField(max_length=30, verbose_name= "Alternative Name 2:",  editable=True, default= None, blank=True, null=True)    

    #MECHANICAL
    poisonsratio = models.FloatField(editable=True, verbose_name= "Poisons Ratio")
    moeit = models.FloatField(editable=True, verbose_name= "Modulus of elasticity in tension")
    hec =  models.FloatField(editable=True, verbose_name= "Heat expansion coeficient")
    density = models.FloatField(editable=True, verbose_name= "Density")
    uts = models.FloatField(editable=True, verbose_name= "Ultimate Tensile Strength, Su(Mpa)")
    ys = models.FloatField(editable=True, verbose_name= "Yield strength, Sy(Mpa)")
    sh = models.FloatField(editable=True, verbose_name= "Shear strength (Mpa)")

    #CLASSIFICATION
    METALFERROUS = 'Metals Ferrous'
    METALNONFERROUS = 'Metals Non-Ferrous'
    PLASTIC = 'Plastic'
    CERAMIC = 'Ceramic'
    COMPOSITE = 'Composite'
    SPECIAL = 'Special'


    MATGROUP = [
        (METALFERROUS, ('Metal Ferrous')),
        (METALNONFERROUS, ('Metal Non-Ferrous')),
        (PLASTIC, ('Plastic')),
        (CERAMIC, ('Ceramic')),
        (COMPOSITE, ('Composite')),
        (SPECIAL, ('Special')),
    ]
    materialgroup = models.CharField(choices=MATGROUP, max_length=32, default=SPECIAL)

    #Costs
    matcost = models.FloatField(editable=True, verbose_name= "Material cost per metric ton", default= None, blank=True, null=True)

    class Meta:
        app_label = 'MatMan'
    def __str__(self):
        return str(self.name)