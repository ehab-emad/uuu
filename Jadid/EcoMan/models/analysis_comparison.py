from django.db import models
from datetime import datetime
from website.generate_pk import generate_pk
from django.conf import settings
from EcoMan.models.lca_property import Lca_Property
from EcoMan.models.analysis_settings import on_create_default_settings
from .lca_part import Lca_Part
from ConceptMan.models import Part
from django.shortcuts import get_object_or_404
from django.forms import model_to_dict
from decouple import config
import json
import os

class Analysis_Comparison(models.Model):
    id = models.CharField(default=generate_pk, primary_key=True, max_length=255, unique=True)
    name = models.CharField(max_length=100,  default= 'No Name', editable=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey("EcoMan.ProjectUser_EcoMan_Ref", models.SET_NULL, blank=True,null=True,)
    project_model=models.ForeignKey("EcoMan.Project_EcoMan_Ref", verbose_name="Project", on_delete=models.CASCADE, help_text ="Select a a project for analysis", default=None, blank=True, null=True,)

    analysis_settings=models.OneToOneField("EcoMan.Analysis_Settings", verbose_name="Settings", on_delete=models.CASCADE, help_text ="Create Analysis Comparison settings", default=on_create_default_settings)

    logo = models.ImageField(upload_to ='uploads/', null=True, blank=True, verbose_name = "Part Image")
    analysis_left=models.ForeignKey("EcoMan.Analysis", verbose_name="Compared Left Analysis", on_delete=models.CASCADE, help_text ="Select an analysis for comparsion", related_name='%(class)s_Left',  blank=True, null=True,)
    analysis_right=models.ForeignKey("EcoMan.Analysis", verbose_name="Compared Right Analysis", on_delete=models.CASCADE, help_text ="Select an analysis for comparsion", related_name='%(class)s_Right',  blank=True,null=True,)

    utilisation_instance_model =  models.ManyToManyField("EcoMan.Utilisation_Process", verbose_name="Utilisations processes",  blank=True,)

    goal_definition = models.CharField(max_length=600,  default= "Not defined", editable=True, blank=True)
    scope_definition  = models.CharField(max_length=600,  default= "Not defined", editable=True, blank=True)

    last_import_document = models.FileField(upload_to='documents/', verbose_name="Import analysis comparison from JSON file", blank=True, null=True,)

    primary_property = models.ForeignKey("EcoMan.Lca_Property", verbose_name="Primary Property Of Interest",  on_delete = models.SET_DEFAULT,  default=Lca_Property.get_default_pk, related_name='%(class)s_primary')

    secondary_properties = models.ManyToManyField("EcoMan.Lca_Property", verbose_name="Secondary Properties of Interst", blank=True, related_name='%(class)s_secondary')


    def save(self, *args, **kwargs):
        super(Analysis_Comparison, self).save(*args, **kwargs)
        #save all utilisation_instance_models in order
        for model in self.utilisation_instance_model.all():
            model.save()

    def import_json(self):

        json_file_path = self.last_import_document.path
        with open(json_file_path, 'r') as f:
            json_data = json.load(f)

        # load analysis objects from current project
        self.analysis_left.import_json(json_data['analysis'][0])
        self.analysis_right.import_json(json_data['analysis'][1])
        self.save()

    class Meta:
        app_label = 'EcoMan'
    def __str__(self):
        return str(self.name)

    def get_commodity_parts(self): #-> QuerySet[Lca_Part]:
        lca_parts_left_all = self.analysis_left.lca_part_models.all()
        lca_parts_right_all = self.analysis_right.lca_part_models.all()
        lca_parts_commodity= set(lca_parts_left_all) & set(lca_parts_right_all)
        lca_parts_commodity = sorted(lca_parts_commodity, key=lambda x: x.id, reverse=True)


        lca_parts_left=lca_parts_left_all.exclude(id__in=[o.id for o in lca_parts_commodity])
        lca_parts_right=lca_parts_right_all.exclude(id__in=[o.id for o in lca_parts_commodity])

    def as_dict(self) ->dict:
        '''this function will sum up all the steps and its processes
        '''


        #get vehicle information
        vehicle = self.analysis_left.concept_model.vehicles.all()[:1].get()
        energy = vehicle.reference_vehicle.energy_source_model
        production = vehicle.reference_vehicle.production_rate_model

        #or like this?
        #from website.models import Vehicle
        #vehicle =Vehicle.objects.filter(concept__analysis__analysis_comparison_id = self.id)

        #JSON Header some information about the exported
        entry = {}
        entry.update({'application': "EDAG QLCA Tool"})
        entry.update({'version': os.environ.get('DJANGO_APPLICATION_QLCA_VERSION', config('DJANGO_APPLICATION_QLCA_VERSION', default='Not Defined'))})
        entry.update({'analysis_id': str(self.id)})
        entry.update({'analysis_name': str(self.name)})
        #entry.update({'entry_creator ': "ah!! i need request to get user info"})
        entry.update({'owner': str(self.owner)})
        entry.update({'created_at': str(self.created_at)[0:16]}) #sliced for better legibility
        entry.update({'updated_at': str(self.updated_at)[0:16]}) #sliced for better legibility
        entry.update({'exported_at': str(datetime.now().isoformat(sep=" ", timespec="minutes"))})
        entry.update({'analysis_settings': model_to_dict(self.analysis_settings)})
        entry.update({'utilisation_instance_model': [p.id for p in self.utilisation_instance_model.all()]})
        entry.update({'primary_property': str(self.primary_property)})
        entry.update({'secondary_properties': [p.id for p in self.secondary_properties.all()]})
        entry.update({'goal_definition': str(self.goal_definition)})
        entry.update({'scope_definition': str(self.scope_definition)})
        #vehicle information
        vehicle_dict = {}
        vehicle_dict.update({'id': str(str(vehicle.UUID))})
        vehicle_dict.update({'name': str(vehicle.reference_vehicle.name)})
        vehicle_dict.update({'class': str(vehicle.reference_vehicle.get_vehicle_classification_display()).split("(")[0]}) #examples removed from string
        vehicle_dict.update({'target_weight': str(vehicle.reference_vehicle.target_weight)})
        vehicle_dict.update({'estimated_weight': str(vehicle.reference_vehicle.estimated_weight)})
        vehicle_dict.update({'life_km': str(vehicle.reference_vehicle.life_distance_in_km)})
        vehicle_dict.update({'life_years': str(vehicle.reference_vehicle.life_time_in_years)})
        entry.update({'vehicle': vehicle_dict})
        #energy source information
        entry.update({'primary_energy': str(energy.get_energysource_1_display())})
        entry.update({'secondary_energy':str(energy.get_energysource_2_display())})
        #production information
        entry.update({'produced_units': str(production.produced_units)})
        #lca results
        entry.update({'analysis': [self.analysis_left.as_dict(), self.analysis_right.as_dict()]})

        oDict = entry

        return oDict

