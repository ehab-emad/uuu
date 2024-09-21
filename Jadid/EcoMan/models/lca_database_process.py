from django.db import models

from website.generate_pk import generate_pk

from math import *
from django.db.models.signals import post_save
from django.dispatch import receiver

class Lca_Database_Process(models.Model):   #should be LCA_Process
    id = models.CharField(default=generate_pk, primary_key=True, max_length=255, unique=True)
    name = models.CharField(max_length=1000,   editable=True, blank=True,null=True,)
    name_DE = models.CharField(max_length=1000,   editable=True, blank=True,null=True,)
    idemat_id = models.CharField(max_length=30,   editable=True, blank=True,null=True,)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey("EcoMan.ProjectUser_EcoMan_Ref", models.SET_NULL, blank=True,null=True,)

    ACCESSIBILITY_CHOICE= [
    ("PRIVATE", ("Private")),
    ("DATABASE_USERS", ("Database Users")),  
    ("HIDDEN", ("Hidden")),   #with this setting process will be used only for internal lca engine
    ("ARCHIVE", ("Archive"))   #with this setting process will be used only for internal lca engine 
    ]

    accessibility = models.CharField(choices=ACCESSIBILITY_CHOICE, default="PRIVATE",  max_length=50)
    database_model = models.ForeignKey("EcoMan.Lca_Database", models.CASCADE, blank=True, null=True)
    process_id = models.CharField(max_length=30,   editable=True, blank=True,null=True,)


    category_model = models.ForeignKey("EcoMan.Lca_Database_Category", verbose_name="Category", on_delete=models.CASCADE,  null=True,)
    group_model = models.ForeignKey("EcoMan.Lca_Database_Group", verbose_name="Group of the Category", on_delete=models.CASCADE,  null=True,)
    subgroup_model = models.ForeignKey("EcoMan.Lca_Database_Subgroup", verbose_name="Subgroup of the Group", on_delete=models.CASCADE,  null=True,)

    UNITS_CHOICE= [
    ("kg", ("Kilogram [kg]")),
    ("m", ("Meter [m]")),
    ("m2", ("Square metre [m2]")),
    ("m3", ("Cubic metre [m3]")),
    ("MJ", ("Megajoule [MJ]")),
    ("tkm", ("Tonne-kilometre [tkm]")),
    ("m3km", ("Cubic kilometre [m3km]")),
    ("s", ("??????? [s]")),
    ("p", ("piece [p]")),
    ]


    unit = models.CharField(choices=UNITS_CHOICE, max_length=50) #input unit




    ec_total = models.FloatField(editable=True, verbose_name= "Total Eco costs [euro]", blank=True,null=True, default = 0)

    ec_of_human_health = models.FloatField(editable=True, verbose_name= "Eco costs of human health [euro]", blank=True,null=True, default = 0)

    ec_exo_toxicity=models.FloatField(editable=True, verbose_name= "Eco costs of exo-toxicity [euro]", blank=True,null=True,default = 0)

    ec_resource=models.FloatField(editable=True, verbose_name= "Eco costs of carbon footprint [euro]", blank=True,null=True, default = 0)

    ec_carbon=models.FloatField(editable=True, verbose_name= "Eco costs of carbon footprint [euro]", blank=True,null=True, default = 0)

    carbon_footprint=models.FloatField(editable=True, verbose_name= "Carbon Footprint [kg CO2 equiv.]", blank=True,null=True, default = 0)

    ced_total=models.FloatField(editable=True, verbose_name= "CED Total [MJ]", blank=True,null=True, default = 0)

    recipe2016_endpoint=models.FloatField(editable=True, verbose_name= "ReCiPe2016 endpoint (pt) [World(2010) H/A]", blank=True,null=True, default = 0)

    recipe_human_health=models.FloatField(editable=True, verbose_name= "ReCiPe human health [H            DALY]", blank=True,null=True, default = 0)

    recipe_eco_toxicity=models.FloatField(editable=True, verbose_name= "ReCiPe ectoxicity [H            DALY]", blank=True,null=True, default = 0)

    recipe_resources=models.FloatField(editable=True, verbose_name= "ReCiPe resources [H     USD2013]", blank=True,null=True, default = 0)

    environmental_footprint=models.FloatField(editable=True, verbose_name= "Environm Footprint [Total          Pt]", blank=True,null=True, default=0)

    source=models.CharField(max_length=1000,  default= 'Note', editable=True, blank=True, )



    class Meta:
        app_label = 'EcoMan'
    def __str__(self):
        return str(self.name)

    #def save(self, *args, **kwargs):
    #    '''if not imported from idemat idemat_id will be None and has to be generated with following function
    #    '''
    def save(self, *args, **kwargs):
            import re
            if  self.process_id is None or re.search('nan', str(self.process_id), re.IGNORECASE):
                if self.category_model and self.group_model and self.subgroup_model:
                    self.idemat_id = str(self.category_model.identifier) + "." + str(self.group_model.identifier) + "." + str(self.subgroup_model.identifier) + "." + str(self.id)
                    self.process_id = self.idemat_id
            super(Lca_Database_Process, self).save(*args, **kwargs)



def on_create_default_process():
    process = Lca_Database_Process.objects.create(accessibility = "HIDDEN")
    return process.id

@receiver(post_save, sender=Lca_Database_Process)
def create_projectuser_conceptman_ref(sender, instance, created, **kwargs):
    '''this function is tracking if new processes bring new categories with it'''
    if created:
        target_database = instance.database_model
        category = instance.category_model
        if category:
            target_database.categories.add(category)
            target_database.save()