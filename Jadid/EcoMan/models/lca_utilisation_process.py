from django.db import models
#from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from website.generate_pk import generate_pk
from django.conf import settings
from django.core.validators import RegexValidator
from EcoMan.models import Lca_Database_Process
from EcoMan.models import Analysis_Comparison

from EcoMan.QLCA_Idemat_Calculation import import_lca_constant
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from decimal import *
from django.dispatch import receiver
from django.db.models.signals import post_save , pre_save
PERCENTAGE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(100)]
NONNEGATIVE_VALIDATOR = [MinValueValidator(0),]
class Utilisation_Process(models.Model):
    id = models.CharField(default=generate_pk, primary_key=True, max_length=255, unique=True) 
    name = models.CharField(max_length=100,  default= 'Not defined', editable=True, blank=True)
    owner = models.ForeignKey("EcoMan.ProjectUser_EcoMan_Ref", models.SET_NULL, blank=True,null=True,)
   
    custom_name = models.CharField(  max_length=100, blank=True, null=True, verbose_name= "Custom Process Name", help_text="Your internal designation of process name") 
    notes = models.CharField(max_length=2000, unique=True, blank=True, null=True, verbose_name= "Notes", help_text="Put your notes and assumptions here") 
    vehicle=models.ForeignKey("EcoMan.Vehicle_EcoMan_Ref", models.SET_NULL, verbose_name="Vehicle", help_text ="Select vehicle", default=None, blank=True, null=True, )   


    start_time = models.IntegerField(editable=True, verbose_name= "Utilisation Start Time [-] (years after SOP)", blank=True, null=True,)    
    end_time  = models.IntegerField(editable=True, verbose_name= "Utilisation End Time [-] (years after SOP)", blank=True, null=True,)    
    manufactured_units  = models.IntegerField(editable=True, verbose_name= "Manufactured units [-] (units)", blank=True, null=True,)    

    
    concept_weight_left = models.FloatField(editable=True, verbose_name= "Concept Weight [kg]", default = 0)         
    concept_weight_right = models.FloatField(editable=True, verbose_name= "Concept Weight [kg]", default = 0)        

    vehicle_weight_left = models.FloatField(editable=True, verbose_name= "Adjusted Vehicle Weight [kg]", default = 0)         
    vehicle_weight_right = models.FloatField(editable=True, verbose_name= "Adjusted Vehicle Weight [kg]", default = 0)  

    vehicle_weight_delta_left = models.FloatField(editable=True, verbose_name= "Adjusted Vehicle Weight [kg]", default = 0 )         
    vehicle_weight_delta_right = models.FloatField(editable=True, verbose_name= "Adjusted Vehicle Weight [kg]", default = 0)  

    goods_weight = models.FloatField(editable=True, verbose_name= "Goods weight [kg]", default = 0) 
    goods_weight_utilisation = models.DecimalField(max_digits=3, decimal_places=0, verbose_name= "Goods Weight Utilisation [-]", default=Decimal(100), validators=PERCENTAGE_VALIDATOR)

    engwpperkm_vehicle = models.FloatField(editable=True, verbose_name= "Energy GWP per Km [GWP/km]", blank=True, null=True,)      
    engwpperkm_vehicle_for_analysis_left = models.FloatField(editable=True, verbose_name= "Energy GWP per Km [GWP/km]", blank=True, null=True,)         
    engwpperkm_vehicle_for_analysis_right = models.FloatField(editable=True, verbose_name= "Energy GWP per Km [GWP/km]", blank=True, null=True,)    
    
    engwpperkm_vehicle_source_1 = models.FloatField(editable=True, verbose_name= "Global Warming Potential Primary Source [GWP/l]", default=0, validators=NONNEGATIVE_VALIDATOR, blank=True,null=True,)
    engwpperkm_vehicle_source_2 = models.FloatField(editable=True, verbose_name= "Global Warming Potential Secondary Source [GWP/l]", default=0, validators=NONNEGATIVE_VALIDATOR, blank=True,null=True,)
    engwpperkm_concept_source_1 = models.FloatField(editable=True, verbose_name= "Global Warming Potential Primary Source [GWP/l]", default=0, validators=NONNEGATIVE_VALIDATOR, blank=True,null=True,)
    engwpperkm_concept_source_2 = models.FloatField(editable=True, verbose_name= "Global Warming Potential Secondary Source [GWP/l]", default=0, validators=NONNEGATIVE_VALIDATOR, blank=True,null=True,)

    estimated_fuel_consumption_source_1_adj =models.FloatField(editable=True, verbose_name= "Estimated Fuel Consumption [l/100km]", default=0, blank=True,null=True,)
    estimated_fuel_consumption_source_2_adj =models.FloatField(editable=True, verbose_name= "Estimated Fuel Consumption [l/100km]", default=0, blank=True,null=True,)
    estimated_energy_consumption_source_1_adj =models.FloatField(editable=True, verbose_name= "Estimated Energy Consumption [kWh/100km]", default=0, blank=True,null=True,)
    estimated_energy_consumption_source_2_adj =models.FloatField(editable=True, verbose_name= "Estimated Energy Consumption [kWh/100km]", default=0, blank=True,null=True,)





    STATUS_CHOICES= [
    ("GREEN", ("Green")),
    ("ORANGE", ("Orange")),
    ("RED", ("Red")),
    ]
    status = models.CharField(choices=STATUS_CHOICES, max_length=32, default="GREEN")
    weight = models.FloatField(editable=True, verbose_name= "Energy GWP per Km [GWP/km]", blank=True, null=True,)          

    quantity = models.FloatField(editable=True, verbose_name= "Utilisation Lifetime [km] (only for current usage process)", default=0)

    def save(self, *args, **kwargs):
        self.calculate() 

        if self.quantity == 0:
            self.status ='RED'
        if self.quantity >0:
            self.status ='GREEN'
        super(Utilisation_Process, self).save(*args, **kwargs)

    def calculate(self):
        #for left concept
        analysis_comparison = Analysis_Comparison.objects.filter(utilisation_instance_model=self.id)

        if not analysis_comparison:
            return None #dont try to calculate if concept is not defined
        else:
            analysis = analysis_comparison.get().analysis_left
            self.concept_weight_left = self.calculate_concept_weight(analysis)
            self.vehicle_weight_left = self.calculate_vehicle_weight(analysis)
            self.vehicle_weight_delta_left = self.vehicle_weight_left - self.vehicle.reference_vehicle.target_weight
            self.engwpperkm_vehicle_for_analysis_left =self.calculation_engwpperkm(self.vehicle_weight_delta_left)
        #for right concept
        if not analysis_comparison:
            return None #dont try to calculate if concept is not defined
        else:
            analysis = analysis_comparison.get().analysis_right
            self.concept_weight_right = self.calculate_concept_weight(analysis)
            self.vehicle_weight_right = self.calculate_vehicle_weight(analysis)
            self.vehicle_weight_delta_right = self.vehicle_weight_right - self.vehicle.reference_vehicle.target_weight
            self.calculation_engwpperkm(self.vehicle_weight_delta_left)
            self.engwpperkm_vehicle_for_analysis_right =self.calculation_engwpperkm(self.vehicle_weight_delta_right)
    def calculate_concept_weight(self, analysis):
        """
        This function estimates the final weight of the concept used for calculation
        Should be implemented inside Concept model
        """

        vehicle_weight_delta = 0 #this value will represent weight which will be added to a total vehicle weight
        concept_weight = 0 #this value will represent weight of the concept
        lca_parts_in_use = analysis.lca_part_models.all()
        for x in lca_parts_in_use: 
            concept_weight = concept_weight + x.part_model.weight      #we are catching error when part weight is 0
        return concept_weight

    def calculate_vehicle_weight(self, analysis):
        """
        This function estimates the final weight of the vehicle
        """
        vehicle_weight_delta = 0 #this value will represent weight which will be added to a total vehicle weight
        concept_weight = 0 #this value will represent weight of the concept
        lca_parts_in_use = analysis.lca_part_models.all()
        for x in lca_parts_in_use: 
            if x.vehicle_weight_participation == "ADDED":
                vehicle_weight_delta =vehicle_weight_delta + x.part_model.weight 
        return self.vehicle.reference_vehicle.target_weight + vehicle_weight_delta + self.goods_weight * int(self.goods_weight_utilisation)/100



    def calculation_engwpperkm(self, vehicle_weight_delta):
        """
        This function estimates energy gwp of the vehicle per km 
        """
        energy_source_1 = self.vehicle.reference_vehicle.energy_source_model.get_energysource_1_display().upper()
        energy_source_2 = self.vehicle.reference_vehicle.energy_source_model.get_energysource_2_display().upper()

        self.engwp_source_1 = import_lca_constant(energy_source_1)[energy_source_1]["ENGWP"] #get with script from JSON constant
        self.engwp_source_2 = import_lca_constant(energy_source_2)[energy_source_2]["ENGWP"] #get with script from JSON constant
        kwhperl_source_1 = import_lca_constant(energy_source_1)[energy_source_1]["KWHPERL"] #get with script from JSON constant
        kwhperl_source_2 = import_lca_constant(energy_source_2)[energy_source_2]["KWHPERL"] #get with script from JSON constant

        #calculate adjusted fuel consumtion for the energy sources
        if not self.vehicle.reference_vehicle.energy_source_model.energysource_1 =="ES1":     #if not electric
            eff_adj_source_1 = self.vehicle.reference_vehicle.energy_source_model.estimated_fuel_consumption_source_1 + import_lca_constant(energy_source_1)[energy_source_1]["EFF_ADJ_100KG"][self.vehicle.reference_vehicle.vehicle_classification] * vehicle_weight_delta / 100  #get with script from JSON constant 
        if not self.vehicle.reference_vehicle.energy_source_model.energysource_2 =="ES1":     #if not electric
            eff_adj_source_2 = self.vehicle.reference_vehicle.energy_source_model.estimated_fuel_consumption_source_2 + import_lca_constant(energy_source_2)[energy_source_2]["EFF_ADJ_100KG"][self.vehicle.reference_vehicle.vehicle_classification] * vehicle_weight_delta / 100  #get with script from JSON constant

        #calculate adjusted energy consuption in kWh per 100km for database with added weight, for electric user input was requested
        if not self.vehicle.reference_vehicle.energy_source_model.energysource_1 =="ES1":     #if not electric
            estimated_energy_consumption_source_1_adj =  kwhperl_source_1 * eff_adj_source_1
        else:                                   #if electric
            estimated_energy_consumption_source_1_adj =  self.vehicle.reference_vehicle.energy_source_model.estimated_energy_consumption_source_1 + import_lca_constant(energy_source_1)[energy_source_1]["EFF_ADJ_100KG"][self.vehicle.reference_vehicle.vehicle_classification] * vehicle_weight_delta / 100  #get with script from JSON constant 

        #calculate adjusted energy consuption in kWh per 100km for database with added weight, for electric user input was requested
        if not self.vehicle.reference_vehicle.energy_source_model.energysource_2 =="ES1":     #if not electric
            estimated_energy_consumption_source_2_adj =  kwhperl_source_2 * eff_adj_source_2
        else:                                   #if electric
            estimated_energy_consumption_source_2_adj =  self.vehicle.reference_vehicle.energy_source_model.estimated_energy_consumption_source_2 + import_lca_constant(energy_source_2)[energy_source_2]["EFF_ADJ_100KG"][self.vehicle.reference_vehicle.vehicle_classification] * vehicle_weight_delta / 100  #get with script from JSON constant 

        engwpperkm1 = float(self.vehicle.reference_vehicle.energy_source_model.utilisation_ratio_source_1) * 0.01 * estimated_energy_consumption_source_1_adj * self.engwp_source_1 # hybrid fraction drive 1 * energy usage per 100km drive 1 * gwp energy type drive 1
        engwpperkm2 = float(self.vehicle.reference_vehicle.energy_source_model.utilisation_ratio_source_2) * 0.01 * estimated_energy_consumption_source_2_adj * self.engwp_source_2 # vehicle energy consumption in MJ per km

        return engwpperkm1 + engwpperkm2 # adding energy use of drive 1 and drive 2 together

    class Meta:
        app_label = 'EcoMan'
    def __str__(self):
        return str(self.name) 


