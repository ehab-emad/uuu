from django.db import models
from datetime import datetime
from django.urls import reverse
from django.forms.models import model_to_dict
from website.generate_pk import generate_pk
from django.conf import settings
from EcoMan.models.lca_property import Lca_Property
from EcoMan.models.analysis_settings import on_create_default_settings
from decouple import config
import os
class Analysis(models.Model):
    id = models.CharField(default=generate_pk, primary_key=True, max_length=255, unique=True)    
    name = models.CharField(max_length=100,  default= 'No Name', editable=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey("EcoMan.ProjectUser_EcoMan_Ref", models.SET_NULL, blank=True,null=True,)
    project_model=models.ForeignKey("EcoMan.Project_EcoMan_Ref", verbose_name="Project", on_delete=models.CASCADE, help_text ="Select a a project for analysis", default=None, blank=True,null=True, )
    concept_model=models.ForeignKey("ConceptMan.Concept", verbose_name="Analysed Concept", on_delete=models.CASCADE, help_text ="Select a concept for analysis", blank=True, null=True,)   
    logo = models.ImageField(upload_to ='uploads/', null=True, blank=True, verbose_name = "Part Image")
    lca_part_models=models.ManyToManyField("EcoMan.Lca_Part", verbose_name="LCA Parts", blank=True, related_name='%(class)s_Upstream'  )  
    analysis_settings=models.OneToOneField("EcoMan.Analysis_Settings", verbose_name="Settings", on_delete=models.CASCADE, help_text ="Create Analysis Comparison settings", default=on_create_default_settings)
    goal_definition = models.CharField(max_length=600,  default= "Not defined", editable=True, blank=True)
    scope_definition  = models.CharField(max_length=600,  default= "Not defined", editable=True, blank=True)
    primary_property = models.ForeignKey("EcoMan.Lca_Property", verbose_name="Primary Property Of Interest",  on_delete = models.SET_DEFAULT,  default=Lca_Property.get_default_pk, related_name='%(class)s_primary')
    secondary_properties = models.ManyToManyField("EcoMan.Lca_Property", verbose_name="Secondary Properties of Interst", blank=True, related_name='%(class)s_secondary')
    utilisation_instance_model =  models.ManyToManyField("EcoMan.Utilisation_Process", verbose_name="Utilisations processes",  blank=True,)
    weight = models.FloatField(editable=False, verbose_name= "Concept Weight [kg]", blank=True,  default = 0)

    def save(self, *args, **kwargs):
        self.calculate_analysis_weight() 

        super(Analysis, self).save(*args, **kwargs)

    # def get_object(self, *args, **kwargs) -> None:
    #     super().__init__(*args, **kwargs)
    #     self.primary_property = Lca_Property.get_default_pk  

    def calculate_analysis_weight(self):
        """
        This function estimates the weight of the analysis
        """
        self.weight = 0
        parts_in_use = self.lca_part_models.all()
        for x in parts_in_use: 
            self.weight += x.part_model.weight  * x.multiplier    

    def getDefaultProperty(self) -> Lca_Property:
        return Lca_Property.objects.filter(id = Lca_Property.get_default_pk()).get()
    
    def as_comparison_dict(self) ->dict:
        '''this function will sum up all the steps and its processes
        '''


        #get information
        vehicle = self.concept_model.vehicles.all()[:1].get()
        energy = vehicle.reference_vehicle.energy_source_model
        production = vehicle.reference_vehicle.production_rate_model
        now_timestamp = str(datetime.now().isoformat(sep=" ", timespec="minutes"))

        #JSON Header some information about the exported
        entry = {}
        entry.update({'application': "EDAG QLCA Tool"})
        entry.update({'version': os.environ.get('DJANGO_APPLICATION_QLCA_VERSION', config('DJANGO_APPLICATION_QLCA_VERSION', default='Not Defined'))})
        entry.update({'analysis_id': str(self.id)})
        entry.update({'analysis_name': f"Analysis comparison for {str(self.name)}"})
        #entry.update({'entry_creator ': "ah!! i need request to get user info"})
        entry.update({'owner': str(self.owner)})
        entry.update({'created_at': now_timestamp}) #sliced for better legibility
        entry.update({'updated_at': now_timestamp}) #sliced for better legibility
        entry.update({'exported_at': now_timestamp})
        entry.update({'analysis_settings': model_to_dict(self.analysis_settings)})
        entry.update({'utilisation_instance_model': []})
        entry.update({'primary_property': ""})
        entry.update({'secondary_properties': []})
        entry.update({'goal_definition': ""})
        entry.update({'scope_definition': ""})
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
        entry.update({'analysis': [self.as_dict()]})

        return entry

    def as_dict(self) ->dict:
        '''this function will sum up all the steps and its processes 
        '''

        #JSON Header some information about the exported 
        entry = {}
        entry.update(model_to_dict(self,fields = ['id','name', 'owner', 'created_at', 'updated_at']))
        entry.update({'owner': str(entry['owner'])})
        entry.update({'parts': {}})
        entry.update({'weight': str(self.weight)})
        entry.update({'scope_definition': str(self.scope_definition)})
        entry.update({'goal_definition': str(self.goal_definition)})
        entry.update({'primary_property': str(self.primary_property)})
        entry.update({'secondary_properties': [p.id for p in self.secondary_properties.all()]})
        entry.update({'utilisation_instance_model': [p.id for p in self.utilisation_instance_model.all()]})
        entry.update({'analysis_settings': model_to_dict(self.analysis_settings)})
        lca_result_dict = {}
        from EcoMan.models import Instance_Idemat_Database_Process
        for item in Instance_Idemat_Database_Process.lca_fields:
            lca_result_dict.update({item: 0})
        entry.update({'lca_result': lca_result_dict.copy()})
        lca_parts = self.lca_part_models.all()
        
        #calculate lca_ parts and its header data
        for lca_part in self.lca_part_models.all():            
            entry['parts'].update({lca_part.part_model.__str__(): lca_part.part_model.as_dict().copy() })
            entry['parts'][lca_part.part_model.__str__()]['process_model'] ={}
            entry['parts'][lca_part.part_model.__str__()].update(lca_part.as_dict().copy())
        #calculate sum for all parts in analysis
        lca_result_sum = lca_result_dict.copy()
        for partid in entry['parts']:
            for item in lca_result_sum:
                if item != 'lca_result':
                    lca_result_sum[item] += entry['parts'][partid]['lca_result'][item] 
        entry.update({'lca_result': lca_result_sum.copy()})                    

        #calculate sum for all circularity 
        lca_result_sum = lca_result_dict.copy()
        for partid in entry['parts']:
            for item in lca_result_sum:
                if item != 'lca_result':
                    lca_result_sum[item] += entry['parts'][partid]['lca_result_circularity'][item] 
        entry.update({'lca_result_circularity': lca_result_sum.copy()})   
        return entry

    def get_weight_in_units(self, units=None):
        """Return the weight in the specified units or use the default from settings if not provided."""
        
        # Use provided units or fallback to self.settings
        units = units or self.analysis_settings.weight_units
        
        # Define conversion factors
        conversion_factors = {
            'KILOGRAMS': 1,
            'GRAMS': 1000,
        }
        
        # Return the weight converted to the desired units
        return self.weight * conversion_factors.get(units, 1)

    def import_json(self, json_data):
        import json
        from EcoMan.models import Lca_Part
        from ConceptMan.models import Part
        for _, part_data in json_data['parts'].items():
            basic_part = Part(
                name=part_data['name'],
                weight=part_data['weight'],
                weight_calculation=part_data['weight_calculation'],
            )
            basic_part.save()
            lca_part = Lca_Part(
                name=part_data['name'],
                multiplier=part_data['multiplier'],
                part_model=basic_part
            )
            lca_part.save()
            self.process_choices(part_data, lca_part)


            self.lca_part_models.add(lca_part)
        self.name = json_data['name']
        self.concept_model.name = json_data['name']
        self.concept_model.save()
        self.save()


    def process_choices(self, part_data, lca_part):

        from EcoMan.models import Instance_Idemat_Database_Process, Lca_Database_Process
        PROCESS_TYPE_CHOICES = dict(Instance_Idemat_Database_Process.PROCESS_TYPE_CHOICES)
        LCA_STEP_CHOICES = dict(Instance_Idemat_Database_Process.LCA_STEP_CHOICES)

        for step_name, step_data in part_data['lca_part'].items():

                try:
                    step_choice = list(filter(lambda x: LCA_STEP_CHOICES[x] == step_name, LCA_STEP_CHOICES))[0]
                except:
                    continue # no data apart from summary

                for process_name, process_data in step_data.items():
                    try:
                        # No data apart from summary
                        process_type_choice = list(filter(lambda x: PROCESS_TYPE_CHOICES[x] == process_name, PROCESS_TYPE_CHOICES))[0]
                    except:
                        continue
                    if len(process_data) <= 1:
                        continue

                    self.parse_idemat_process(process_data, step_choice, process_type_choice, lca_part)


    def parse_idemat_process(self,process_data, step_choice, process_type_choice, lca_part):
        from EcoMan.models import Instance_Idemat_Database_Process, Lca_Database_Process
        for item_name, item_data in process_data.items():
            if(item_name == 'lca_result'):
                continue

            instance_process_model=Instance_Idemat_Database_Process()

            calculation_model = Lca_Database_Process.objects.create()

            calculation_model.name = item_data['lca_input']['name']
            # Set all the values for calculation
            for field in instance_process_model.lca_fields:
                setattr(calculation_model, field, item_data['lca_input'][field])

            calculation_model.save()

            instance_process_model.calculation_model = calculation_model

            try:
                idemat_process = Lca_Database_Process.objects.get(pk=item_data['lca_input']['id'])
                instance_process_model.process_model=idemat_process
                if self.compare_process_details(instance_process_model, idemat_process, calculation_model) == True:
                    instance_process_model.process_flag = "REF_CORRECT"
                else:
                    instance_process_model.process_flag = "PROCESS_CHANGED"


            except Lca_Database_Process.DoesNotExist:
                instance_process_model.process_model=calculation_model
                instance_process_model.process_flag = "ORPH_UNIDENTIFIED"


            instance_process_model.lca_step = step_choice
            instance_process_model.process_type = process_type_choice
            instance_process_model.process_quantity=item_data['process_quantity']
            instance_process_model.process_auxiliary_quantity=item_data['process_auxiliary_quantity']
            instance_process_model.name=item_data['name']
            instance_process_model.save()
            lca_part.lca_process_model.add(instance_process_model)

    def compare_process_details(self, instance, model, calc_model):

        is_equal = True

        # Check all the calculation fields
        for field in instance.lca_fields:
            is_equal &= (getattr(calc_model, field) == getattr(model, field))

        return is_equal

        

    class Meta:
        app_label = 'EcoMan'
    def __str__(self):
        return str(self.name) 