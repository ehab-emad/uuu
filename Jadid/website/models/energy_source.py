from django.db import models
from decimal import *
from website.generate_pk import generate_pk
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import  pre_save
from website.models import Vehicle
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from EcoMan.QLCA_Idemat_Calculation import import_lca_constant
PERCENTAGE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(100)]
NONNEGATIVE_VALIDATOR = [MinValueValidator(0),]

def validate_greater_than_zero(value):
    if value <= 0:
        raise ValidationError(
            ("%(value)s is not greater than zero."),
            params={"value": value},
        )

class Energy_Source(models.Model):
    id = models.CharField(default=generate_pk, primary_key=True, max_length=255, unique=True)    
    name = models.CharField(max_length=100,  default= 'Not defined', editable=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, models.SET_NULL, blank=True, null=True,)

    notes = models.CharField(max_length=100,  default= 'Put your comment here...', editable=True, blank=True)

    ES_CHOICES= [
    ("ES1", ("Electricity")),
    ("ES2", ("Petrol")),
    ("ES3", ("Diesel")),
    ("ES4", ("Gray Hydrogen")),
    ("ES5", ("Blue Hydrogen")),
    ("ES6", ("Green Hydrogen")),
    ("ES7", ("CNG")),
    ("ES8", ("LNG")),
    ("ES10", ("None")),
    ]

    energysource_1 = models.CharField(choices=ES_CHOICES, max_length=32, default="ES2")
    energysource_2 = models.CharField(choices=ES_CHOICES, max_length=32, default="ES2")
  
    utilisation_ratio_source_1 = models.DecimalField(max_digits=3, decimal_places=0, verbose_name= "Energy source use ratio '%'", default=Decimal(100), validators=PERCENTAGE_VALIDATOR)
    utilisation_ratio_source_2 = models.DecimalField(max_digits=3, decimal_places=0, verbose_name= "Energy source use ratio '%'", default=Decimal(100), validators=PERCENTAGE_VALIDATOR)
    estimated_fuel_consumption_source_1 =models.FloatField(editable=True, verbose_name= "Estimated Fuel Consumption [l/100km]", default=0, blank=True,null=True,)
    estimated_fuel_consumption_source_2 =models.FloatField(editable=True, verbose_name= "Estimated Fuel Consumption [l/100km]", default=0, blank=True,null=True,)
    estimated_energy_consumption_source_1 =models.FloatField(editable=True, verbose_name= "Estimated Energy Consumption [kWh/100km]", default=0, blank=True,null=True,)
    estimated_energy_consumption_source_2 =models.FloatField(editable=True, verbose_name= "Estimated Energy Consumption [kWh/100km]", default=0, blank=True,null=True,)
 
    BATTERY_CHOICES= [
    ("BAT1", ("NMC")),
    ("BAT2", ("NiMH")),
    ("BAT3", ("LiFePo4")),
    ("BAT4", ("LiCoO2")),
    ]

    battery_type_source_1 = models.CharField(choices=BATTERY_CHOICES, max_length=32, default="BAT1", blank=True,null=True,)
    battery_capacity_source_1 = models.FloatField(editable=True, verbose_name= "Battery Capacity [kWh]", blank=True,null=True,)
    battery_weight_source_1 = models.FloatField(editable=True, verbose_name= "Battery Weight [kg]", blank=True,null=True,)
  
    battery_type_source_2 = models.CharField(choices=BATTERY_CHOICES, max_length=32, default="BAT1", blank=True,null=True,)
    battery_capacity_source_2 = models.FloatField(editable=True, verbose_name= "Battery Capacity [kWh]", blank=True,null=True,)
    battery_weight_source_2 = models.FloatField(editable=True, verbose_name= "Battery Weight [kg]", blank=True,null=True,)


    capacity_source_1 = models.FloatField(editable=True, verbose_name= "Source capacity [l]", default=0, validators=NONNEGATIVE_VALIDATOR, blank=True,null=True,)
    #efficiency_source_1 =models.FloatField(editable=True, verbose_name= "Efficiency [-]", default=Decimal(100), validators=PERCENTAGE_VALIDATOR, blank=True,null=True,)

    capacity_source_2 = models.FloatField(editable=True, verbose_name= "Source capacity [l]", default=0, validators=NONNEGATIVE_VALIDATOR, blank=True,null=True,)
    #efficiency_source_2 =models.FloatField(editable=True, verbose_name= "Efficiency [-]", default=Decimal(100), validators=PERCENTAGE_VALIDATOR, blank=True,null=True,)

    engwp_source_1 = models.FloatField(editable=True, verbose_name= "Global Warming Potential Primary Source [kg] (Co2 equivalent)", default=0, validators=NONNEGATIVE_VALIDATOR, blank=True,null=True,)
    engwp_source_2 = models.FloatField(editable=True, verbose_name= "Global Warming Potential Secondary Source [kg] (Co2 equivalent)", default=0, validators=NONNEGATIVE_VALIDATOR, blank=True,null=True,)

    engwpperkm = models.FloatField(editable=True, verbose_name= "Global Warming Potential [kg/km] (Co2 equivalent)", default=0, validators=NONNEGATIVE_VALIDATOR, blank=True,null=True,)



    class Meta:
        app_label = 'website'
    def __str__(self):
        return str("ID:" + self.id)
    def save(self, *args, **kwargs):
        #for every energy source calculate separately
        self.engwpperkm = self.calculation_engwp(added_weight = 0)
        super(Energy_Source, self).save(*args, **kwargs)



    def calculation_engwp(self, added_weight):
        """
        This function estimates energy gwp for selected energy sources 
        """
        energy_source_1 = self.get_energysource_1_display().upper()
        energy_source_2 = self.get_energysource_2_display().upper()

        self.engwp_source_1 = import_lca_constant(energy_source_1)[energy_source_1]["ENGWP"] #get with script from JSON constant
        self.engwp_source_2 = import_lca_constant(energy_source_2)[energy_source_2]["ENGWP"] #get with script from JSON constant
        kwhperl_source_1 = import_lca_constant(energy_source_1)[energy_source_1]["KWHPERL"] #get with script from JSON constant
        kwhperl_source_2 = import_lca_constant(energy_source_2)[energy_source_2]["KWHPERL"] #get with script from JSON constant

        eff_adj_source_1 = import_lca_constant(energy_source_1)[energy_source_1]["EFF_ADJ_100KG"][self.vehicle.vehicle_classification] * added_weight /100  #get with script from JSON constant 
        eff_adj_source_2 = import_lca_constant(energy_source_2)[energy_source_2]["EFF_ADJ_100KG"][self.vehicle.vehicle_classification] * added_weight /100  #get with script from JSON constant

        #calculate estimated energy consuption in kWh per 100km for database with added weight 0kg (baseline), for electric user input was requested
        if not self.energysource_1 =="ES1":  #if not electric  #[kWh/100km]
            self.estimated_energy_consumption_source_1 =  kwhperl_source_1 * self.estimated_fuel_consumption_source_1
        
        if not self.energysource_2 =="ES1":  #if not electric  #[kWh/100km]
            self.estimated_energy_consumption_source_2 =  kwhperl_source_2 * self.estimated_fuel_consumption_source_2

        #calculate estimated energy consuption in kWh per 100km for added weight in kg 

        if not self.energysource_1 =="ES1":  #if not electric
            weight_corrected_estimated_energy_consumption_source_1 =  kwhperl_source_1 * (self.estimated_fuel_consumption_source_1 + eff_adj_source_1)
        else:                               #if electric
            weight_corrected_estimated_energy_consumption_source_1 =  self.estimated_energy_consumption_source_1 + eff_adj_source_1

        if not self.energysource_2 =="ES1":  #if not electric
            weight_corrected_estimated_energy_consumption_source_2 =  kwhperl_source_2 * (self.estimated_fuel_consumption_source_2 + eff_adj_source_2)
        else:                               #if electric
            weight_corrected_estimated_energy_consumption_source_2 =  self.estimated_energy_consumption_source_2 + eff_adj_source_2

        engwpperkm1 = float(self.utilisation_ratio_source_1) * 0.01 * weight_corrected_estimated_energy_consumption_source_1 * self.engwp_source_1 # hybrid fraction drive 1 * energy usage per 100km drive 1 * gwp energy type drive 1
        engwpperkm2 = float(self.utilisation_ratio_source_2) * 0.01 * weight_corrected_estimated_energy_consumption_source_2 * self.engwp_source_2 # vehicle energy consumption in MJ per km
        return engwpperkm1 + engwpperkm2 # adding energy use of drive 1 and drive 2 together

    @receiver(pre_save, sender=Vehicle)
    def create_energy_source(sender, instance, **kwargs):
        if instance._state.adding:
            Energy_Source.objects.get_or_create(vehicle=instance)
        else:
            if hasattr(instance, 'energy_source_model') and instance.energy_source_model is None:
                Energy_Source.objects.get_or_create(vehicle=instance)
