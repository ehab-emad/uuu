
from django.forms import ModelForm
from django import forms
from django.forms import ValidationError
#from .models import *
from EcoMan.models import Analysis_Comparison
from EcoMan.models import Lca_Database_Process
from EcoMan.models import Instance_Idemat_Database_Process
from EcoMan.models import Lca_Part
from EcoMan.models import Utilisation_Process
from EcoMan.models import Circularity_Process
from website.models import Energy_Source
from website.models import Project
from ConceptMan.models import Part
from django.db.models import Q
from website.models import Vehicle

#Vehicle EnergySource
class EnergySourceForm(forms.ModelForm):
    vehicle_name = forms.CharField(label='Vehicle Name', required = False)
    vehicle_owner = forms.CharField(label='Vehicle Owner', required = False)
    def __init__(self, *args, **kwargs): 

        super(EnergySourceForm, self).__init__(*args, **kwargs)                       
        self.fields['vehicle_name'].disabled = True 
        self.fields['vehicle_owner'].disabled = True 
        vehicle = Vehicle.objects.filter(energy_source_model__id = self.instance.id).get()
        self.fields['vehicle_name'].initial = vehicle.name
        self.fields['vehicle_owner'].initial = vehicle.owner
    class Meta:
        model = Energy_Source
        fields = '__all__'        
        exclude ='id', 'name', 'owner',
        widgets = {
          'notes': forms.Textarea(attrs={'rows':4, }),
        }

    def clean_battery_capacity_source_1(self):
        capacity = self.cleaned_data['battery_capacity_source_1']
        if self.cleaned_data['energysource_1'] != "ES1": #we dont care when source is not "ES1" Electrical 
            return 0
        if not capacity :
            raise ValidationError("Battery capacity cannot be 0 or none [kWh]")
        elif capacity<=0: 
            raise ValidationError("Battery capacity must be greater than 0 [kWh]")
        return capacity

    def clean_battery_weight_source_1(self):
        weight = self.cleaned_data['battery_weight_source_1']
        if self.cleaned_data['energysource_1'] != "ES1": #we dont care when source is not "ES1" Electrical 
            return 0
        if not weight :
            raise ValidationError("Battery weight cannot be 0 or none [kg]")
        elif weight<=0: 
            raise ValidationError("Battery weight must be greater than 0 [kg]")
        return weight

    def clean_battery_capacity_source_2(self):
        capacity = self.cleaned_data['battery_capacity_source_2']
        if self.cleaned_data['energysource_2'] != "ES1": #we dont care when source is not "ES1" Electrical 
            return 0
        if not capacity :
           raise ValidationError("Battery capacity cannot be 0 or none [kWh]")
        elif capacity<=0: 
            raise ValidationError("Battery capacity must be greater than 0 [kWh]")
        return capacity

    def clean_battery_weight_source_2(self):
        weight = self.cleaned_data['battery_weight_source_2']
        if self.cleaned_data['energysource_2'] != "ES1": #we dont care when source is not "ES1" Electrical 
            return 0
        if not weight :
            raise ValidationError("Battery weight cannot be 0 or none [kg]")
        elif weight<=0: 
            raise ValidationError("Battery weight must be greater than 0 [kg]")
        return weight

    def clean_estimated_fuel_consumption_source_1(self):
        consumption = self.cleaned_data['estimated_fuel_consumption_source_1']
        if self.cleaned_data['energysource_1'] == "ES1": #we dont care when source is "ES1" Electrical 
            return 0
        if not consumption :
            raise ValidationError("Consumption cannot be 0 or none [l/100km]")
        elif consumption<=0: 
            raise ValidationError("Consumption must be greater than 0 [kWh]")
        return consumption

    def clean_estimated_fuel_consumption_source_2(self):
        consumption = self.cleaned_data['estimated_fuel_consumption_source_2']
        if self.cleaned_data['energysource_2'] == "ES1" or self.cleaned_data['energysource_2'] == "ES10": #we dont care when source is "ES1" Electrical or "ES10" None 
            return 0
        if not consumption :
            raise ValidationError("Consumption cannot be 0 or none [l/100km]")
        elif consumption<=0: 
            raise ValidationError("Consumption must be greater than 0 [kWh]")
        return consumption

    def clean_capacity_source_1(self):
        capacity = self.cleaned_data['capacity_source_1']
        if self.cleaned_data['energysource_1'] == "ES1": #we dont care when source is "ES1" Electrical 
            return 0
        if not capacity :
            raise ValidationError("Consumption cannot be 0 or none [l/100km]")
        elif capacity<=0: 
            raise ValidationError("Consumption must be greater than 0 [kWh]")
        return capacity

    def clean_capacity_source_2(self):
        capacity = self.cleaned_data['capacity_source_2']
        if self.cleaned_data['energysource_2'] == "ES1" or self.cleaned_data['energysource_2'] == "ES10": #we dont care when source is "ES1" Electrical or "ES10" None 
            return 0
        if not capacity :
            raise ValidationError("Capacity cannot be 0 or none [l/100km]")
        elif capacity<=0: 
            raise ValidationError("Capacity must be greater than 0 [kWh]")
        return capacity

