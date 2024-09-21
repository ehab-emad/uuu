from django.db import models
from website.generate_pk import generate_pk
from EcoMan.scripts import get_random_color
from django.core.validators import MinValueValidator
from django.dispatch import receiver
from django.db.models.signals import post_save

NONNEGATIVE_VALIDATOR = [MinValueValidator(0),]
class Lca_Part(models.Model):   #should be renamed to Lca_Part
    id = models.CharField(default=generate_pk, primary_key=True, max_length=255, unique=True)
    name = models.CharField(max_length=100,  default= 'Not defined', editable=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey("EcoMan.ProjectUser_EcoMan_Ref", models.SET_NULL, blank=True,null=True,)
    part_model =  models.ForeignKey("ConceptMan.Part", on_delete=models.CASCADE, blank=True, null=True)
    multiplier = models.FloatField(editable=True, verbose_name= "Number of part instances", default = 1.0, validators=[MinValueValidator(0.0),])

    color = models.CharField(max_length=7,  default= get_random_color, editable=True, blank=False)
    notes = models.CharField(max_length=600,  default= "Not defined", editable=True, blank=True)
    istemplate = models.BooleanField(default =False, verbose_name="Visible As Template")
    project_model=models.ForeignKey("EcoMan.Project_EcoMan_Ref", verbose_name="Project", on_delete=models.CASCADE, help_text ="Select a project for part", default=None, blank=True, null=True, )
    #LCA Processes
    lca_process_model =  models.ManyToManyField("EcoMan.Instance_Idemat_Database_Process", verbose_name="LCA processes",  blank=True, related_name='%(class)s_instance')

    #Circularity
    circularity_process_model =models.OneToOneField("EcoMan.Circularity_Process", verbose_name= "Model for Circularity (ReUse)", on_delete=models.CASCADE, default=None, blank=True, null=True,)


    #result  = part.weight / vehicle_weight * engwpperkm * quantity  [Energie]
    ES_CHOICES= [
    ("INCLUDED", ("Part Weight ""included"" in Target Vehicle Weight")),
    ("ADDED", ("Part Weight ""added"" to Target Vehicle Weight")),
    ]

    vehicle_weight_participation = models.CharField(choices=ES_CHOICES, verbose_name= "Vehicle Weight Participation", max_length=32, default="INCLUDED")

    def get_weight_conceptman(self, units="KILOGRAMS"):
        if units =="KILOGRAMS":
            try:
                return self.part_model.weight
            except:
                return 0
        elif units =="GRAMS":
            try:
                return self.part_model.weight * 1000
            except:
                return 0           

    def clone_it(self, ipart_model=None, exclude_processes = []):
        '''This function creates a duplicate of a lca_part
        '''
        from django.forms import model_to_dict
        instance = self

        kwargs = {'name': self.name + '_clone', 'owner': self.owner,} #simple fields

        if ipart_model == None:    #Part_Model if not provided create one else carry over
                ipart_model = self.part_model.clone_it()

        kwargs.update({'name': self.name + '_clone', 'owner': self.owner,})
        new_instance = Lca_Part.objects.create(part_model = ipart_model, **kwargs)


        #post creation
        from EcoMan.models import Circularity_Process
        from django.forms import model_to_dict

        kwargs = model_to_dict(self.circularity_process_model, exclude=['id'])
        Circularity_Process.objects.filter(pk=new_instance.circularity_process_model.pk).update(**kwargs)
        Circularity_Process.objects.filter(pk=new_instance.circularity_process_model.pk).get().save()
        new_instance.color = get_random_color()
        new_instance.save()

        #now lets clone all lca processes

        #create duplicates of the processes
        processes_in_use = self.lca_process_model.all()
        for process in processes_in_use:
            if not process.id in exclude_processes:
                new_process = process.clone_it()
                new_instance.lca_process_model.add(new_process)

        new_instance.save()

        return new_instance
    #this probably doesnt work right now
    def validate_materials_instance(self):
        material_instances = self.lca_process_model.filter(process_type = "PTYPE1_MATERIAL")
        total_weight=0
        for material in material_instances:
            total_weight=total_weight + material.process_quantity
        for material in material_instances:

            if material.process_quantity > 0:
                material.status = "GREEN"
                material.save()

            if total_weight > 1.01 * float(self.part_model.weight):
                material.status = "RED"
                material.save()
            if total_weight < 0.99 * float(self.part_model.weight):
                material.status = "ORANGE"
                material.save()
            if total_weight >= 0.99 * float(self.part_model.weight) and  total_weight <= 1.01 * float(self.part_model.weight):
                material.status = "GREEN"
                material.save()

            if material.process_quantity == 0:
                material.status = "RED"
                material.save()

    def validate_processes_instance(self):
        process_instances = self.lca_process_model.filter(process_type = "PTYPE2_MANUFACTURING_PROCESS")

        for process in process_instances:

            if process.process_quantity > 0:
                process.status = "GREEN"
                process.save()

            if process.process_quantity == 0:
                process.status = "RED"
                process.save()


    def validate_transports_instance(self):
        process_instances = self.lca_process_model.filter(process_type = "PTYPE2_TRANSPORT")

        for process in process_instances:

            if process.process_quantity > 0:
                process.status = "GREEN"
                process.save()

            if process.process_quantity == 0:
                process.status = "RED"
                process.save()


    class Meta:
        app_label = 'EcoMan'
    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        if self.pk:
            self.validate_materials_instance()
            self.validate_processes_instance()
            self.validate_transports_instance()
        super(Lca_Part, self).save(*args, **kwargs)





    def as_dict(self) ->dict:
        '''this function will collects all the processes and generate dictionary
        '''
        step_dict = {} #create an empty structore sorted by GUI steps and GUI process types
        step_dict.update({'multiplier': self.multiplier})
        step_dict.update({'lca_part': {}})
        from EcoMan.models import Instance_Idemat_Database_Process
        LCA_STEP_CHOICES = {} #this array will store Possible lca steps
        LCA_STEP_CHOICES = dict(Instance_Idemat_Database_Process.LCA_STEP_CHOICES)
        PROCESS_TYPE_CHOICES = {} #this array will store Possible lca steps
        PROCESS_TYPE_CHOICES = dict(Instance_Idemat_Database_Process.PROCESS_TYPE_CHOICES)

        query_processes = self.lca_process_model.all()

        #generate separate result dictionary
        lca_result_dict = {}
        for item in Instance_Idemat_Database_Process.lca_fields:
            lca_result_dict.update({item: 0})

        #add steps
        for step in LCA_STEP_CHOICES:
            step_dict['lca_part'][LCA_STEP_CHOICES[step]] = {}

        step_dict.update({'lca_part_id': self.id})
        step_dict.update({'lca_result': lca_result_dict.copy()})
        step_dict.update({'lca_result_circularity': lca_result_dict.copy()})
        step_dict['lca_part'].update({'lca_result': lca_result_dict.copy()})

        #add GUI Process types to the steps
        for step in step_dict['lca_part']:
            if step != 'lca_result':
                for process in PROCESS_TYPE_CHOICES:
                    step_dict['lca_part'][step].update({PROCESS_TYPE_CHOICES[process]: {}})
                    if step != 'lca_result' and process != 'lca_result':
                        step_dict['lca_part'][step][PROCESS_TYPE_CHOICES[process]].update({'lca_result': lca_result_dict.copy()})
                if step != 'lca_result':
                    step_dict['lca_part'][step].update({'lca_result': lca_result_dict.copy()})

        #new
        for process in query_processes:
            if process.is_active:   #only active processes will be included in calculation
                process_dict = process.as_dict()
                for object in process_dict.values():
                   if object['owner'] is not None:
                        object['owner'] = str(object['owner'])
                   if object['lca_input']['owner'] is not None:
                        object['lca_input']['owner'] = str(object['lca_input']['owner'])                     
                step_dict['lca_part'][LCA_STEP_CHOICES[process.lca_step]][PROCESS_TYPE_CHOICES[process.process_type]].update( process_dict )

        lca_result_sum = lca_result_dict

        #summing all processes
        lca_result_step_sum = lca_result_dict.copy()
        lca_result_step_circularity_sum = lca_result_dict.copy()
        for step in step_dict['lca_part'].items():
            if step[0] != 'lca_result':
                lca_result_process_type_sum = lca_result_dict.copy()
                for process_type in step[1].items():
                    if process_type[0] != 'lca_result':
                        lca_result_process_sum = lca_result_dict.copy()
                        for process in process_type[1].items():
                            if process[0] != 'lca_result':
                                for item in lca_result_process_sum:
                                    lca_result_process_sum[item] += process[1]['lca_result'][item]
                                process_type[1].update({'lca_result': lca_result_process_sum.copy()})
                        for item in lca_result_process_type_sum:
                            lca_result_process_type_sum[item] += process_type[1]['lca_result'][item]
                        step[1].update({'lca_result': lca_result_process_type_sum.copy()})
                for item in lca_result_step_sum:
                    if step[0] != 'Circularity': #Circularity is calculated separately and does not belong to manufacturing
                       lca_result_step_sum[item] += step[1]['lca_result'][item]
                    if step[0] == 'Circularity': #Circularity
                       lca_result_step_circularity_sum[item] += step[1]['lca_result'][item]
                step_dict['lca_part'].update({'lca_result': lca_result_step_sum.copy()})
                step_dict['lca_result_circularity'].update({'lca_result_circularity': lca_result_step_circularity_sum.copy()})


        # step 1 to 3 including multiplication
        lca_result_step_sum = lca_result_dict.copy()

        for item in lca_result_step_sum:
            lca_result_step_sum[item] += self.multiplier * step_dict['lca_part']['lca_result'][item]
        step_dict.update({'lca_result': lca_result_step_sum.copy()})

        lca_result_step_sum = lca_result_dict.copy()
        #step 3 circularity including multiplication
        for item in lca_result_step_sum:
            lca_result_step_sum[item] += self.multiplier * step_dict['lca_part']['Circularity']['lca_result'][item]
        step_dict.update({'lca_result_circularity': lca_result_step_sum.copy()})

        return step_dict

    from ConceptMan.models import Part
    @receiver(post_save, sender=Part)
    def save_lca_part(sender, instance, **kwargs):
        '''this function will be triggered everytime lca_part will be saved
           all processes in reffered lca_parts will be resaved in order to recalculate them
        '''
        from ConceptMan.models import Part
        query_part = Part.objects.filter(id = instance.id)
        query_lca_part = Lca_Part.objects.filter(part_model__in = query_part)

        for object in query_lca_part:
            process_instances = object.lca_process_model.all()
            for process in process_instances:
                process.save()


    @staticmethod
    def create_from_dict(part_model, **obj_data):

        new_lca_part = Lca_Part()
        new_lca_part.multiplier = obj_data['multiplier']
        new_lca_part.part_model = part_model
        from EcoMan.models import Instance_Idemat_Database_Process

        def get_recursively(search_dict, field):
            fields_found = []

            for key, value in search_dict.items():

                if field in key:
                    fields_found.append(value)

                elif isinstance(value, dict):
                    results = get_recursively(value, field)
                    for result in results:
                        fields_found.append(result)

                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            more_results = get_recursively(item, field)
                            for another_result in more_results:
                                fields_found.append(another_result)
            return fields_found

        processes = get_recursively(obj_data, 'ID:')

        for process in processes:
            new_process_instance = Instance_Idemat_Database_Process.create_from_dict(**process)
            new_process_instance.save()
            new_lca_part.save()
            new_lca_part.lca_process_model.add(new_process_instance)

        return new_lca_part
    
from website.models import ProjectUser
from website.models import Project
@receiver(post_save, sender=ProjectUser)
def changed_projectuser(sender, instance, created, **kwargs):
    if created:
        return
    else:
        '''
        Find objects which are belonging to user and projects for which user is not authorised   
        '''
        projects = instance.authorised_projects.all()
        project_uuids = []
        for project in projects:
            project_uuids.append(project.UUID)
        from django.db.models import Q
        query_lca_part = Lca_Part.objects.filter(Q(owner__UUID = instance.UUID))
        query_lca_part =  query_lca_part.filter( ~Q(project_model__UUID__in = project_uuids))
        for lca_part in query_lca_part:
            print ("Orphan Object:" + lca_part.name + "UUID:" + str(lca_part.id) + "owner:" + str(lca_part.owner))
            if lca_part.project_model:
                project = lca_part.project_model.reference_project
                from EcoMan.models import ProjectUser_EcoMan_Ref
                lca_part.owner = ProjectUser_EcoMan_Ref.objects.filter(UUID = project.get_anonymous_projectuser(project.UUID).UUID).first()
                print ("Anonymous Object:" + lca_part.name + "UUID:" + str(lca_part.id)+ "owner:" + str(lca_part.owner)) 
                #lca_part.save()