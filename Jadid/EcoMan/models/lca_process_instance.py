from django.db import models
from django.forms.models import model_to_dict
from django.urls import reverse
from website.generate_pk import generate_pk
from django.conf import settings
from django.core.validators import RegexValidator
from EcoMan.models import Lca_Database_Process
from EcoMan.scripts import get_random_color
from EcoMan.models.lca_database_process import on_create_default_process
class Instance_Idemat_Database_Process(models.Model):   #should be LCA_Process_Instance
    id = models.CharField(default=generate_pk, primary_key=True, max_length=255, unique=True)
    name = models.CharField(max_length=100,  default= 'Not defined', editable=True, blank=True)
    owner = models.ForeignKey("EcoMan.ProjectUser_EcoMan_Ref", models.SET_NULL, blank=True,null=True,)
    color = models.CharField(max_length=7,  default= get_random_color, editable=True, blank=False)

    STATUS_CHOICES= [
    ("GREEN", ("Green")),
    ("ORANGE", ("Orange")),
    ("RED", ("Red")),
    ]
    status = models.CharField(choices=STATUS_CHOICES, max_length=32, default="GREEN")

    PROCESS_TYPE_CHOICES= [
    ("PTYPE0_OTHER", ("Other Processes")),
    ("PTYPE1_MATERIAL", ("Material Process")),
    ("PTYPE2_MANUFACTURING_PROCESS", ("Manufacturing Process")),
    ("PTYPE3_TRANSPORT", ("Transport Process")),
    ]
    process_type = models.CharField(choices=PROCESS_TYPE_CHOICES, max_length=32, default="ES2")


    
    LCA_STEP_CHOICES= [
    ("LCASTEP1", ("Upstream")),
    ("LCASTEP2", ("Core")),
    ("LCASTEP3", ("Downstream")),
    ("LCASTEP4", ("Circularity")),
    ]
    lca_step = models.CharField(choices=LCA_STEP_CHOICES, max_length=32, default="ES2")

    is_active = models.BooleanField(default =True,)

    CB_CHOICES= [
    ("CB1", ("Mass Based")),
    ("CB2", ("Material removed Based")),
    ("CB3", ("Surface Based")),
    ]
    calculation_basis = models.CharField(choices=CB_CHOICES, max_length=32, default="ES2")

    process_model = models.ForeignKey("EcoMan.Lca_Database_Process", models.CASCADE, blank=True, null=True,)
    calculation_model = models.OneToOneField("EcoMan.Lca_Database_Process", on_delete=models.CASCADE, default=on_create_default_process, related_name='%(class)s_calculation')
    results_model = models.OneToOneField("EcoMan.Lca_Database_Process", on_delete=models.CASCADE, default=on_create_default_process, related_name='%(class)s_results')

    PROCESS_FLAG= [
        ("MANUAL_INPUT", ("Manual Input (not referenced to LCA Database)")),
        ("MANUAL_MODIFICATION", ("Manual Modification (referenced to LCA Database)")),
        ("ORPH_DELETED", ("Orphan Process (Probably Deleted from LCA Database)")),
        ("ORPH_UNIDENTIFIED", ("Orphan Process (Reference Process not identified during Import)")),
        ("REF_CORRECT", ("Correctly referenced to LCA Database")),
        ("PROCESS_CHANGED", ("Process changed in LCA Database")),
    ]
    process_flag = models.CharField(choices=PROCESS_FLAG, max_length=32, default="REF_CORRECT")
    CALC_FLAG= [
        ("PROCESS_QUANTITY_NOTDEF", ("Manual Input (not referenced to LCA Database)")),
        ("TRANSPORT_DISTANCE_NOTDEF", ("Manual Modification (referenced to LCA Database)")),
        ("PROPERTY_VALUE_NOTDEF", ("Orphan Process (Probably Deleted from LCA Database)")),
        ("INPUT_CORRECT", ("Orphan Process (Probably Deleted from LCA Database)")),
        ("PROCESS_DEACTIVATED", ("Process was deactivated.")),
    ]
    calculation_flag = models.CharField(choices=CALC_FLAG, max_length=32, default="INPUT_CORRECT")

    process_quantity = models.FloatField(editable=True, verbose_name= "Process quantity [-]", default=0)
    process_auxiliary_quantity = models.FloatField(editable=True, verbose_name= "Process quantity [-]", default=0)

    def _get_total_quantity(self):   #process_total_quantity
        total_quantity = float(self.process_quantity) + float(self.process_auxiliary_quantity)
        return total_quantity
    process_total_quantity = property(_get_total_quantity)

    def _get_process_meq(self):   #Materialeinsatzquote
        if float(self.process_quantity) == 0:
            meq = 100
        else:
            meq = float(100 + self.process_auxiliary_quantity / self.process_quantity*100)
        return meq
    process_meq = property(_get_process_meq)

    #only for transport process for tkm calculation
    transport_distance = models.FloatField(editable=True, verbose_name= "Transport Distance for Transporting", default=0)

    notes = models.CharField(max_length=2000, blank=True, null=True, verbose_name= "Notes", help_text="Put your notes and assumptions here")

    lca_fields =['ec_total',                #this fields are currently used in lca analysis calculations
                 'ec_of_human_health',
                 'ec_exo_toxicity',
                 'ec_resource',
                 'ec_carbon',
                 'carbon_footprint',
                 'ced_total',
                 'recipe2016_endpoint',
                 'recipe_human_health',
                 'recipe_eco_toxicity',
                 'recipe_resources',
                 'environmental_footprint']

    def get_computed(self):
        if self.calculation_model:

            if self.process_quantity == None or self.process_quantity == 0:
                self.calculation_flag = 'PROCESS_QUANTITY_NOTDEF'
            if self.transport_distance == None or self.transport_distance == 0:
                self.calculation_flag = 'TRANSPORT_DISTANCE_NOTDEF'

            for field in self.lca_fields:
                setattr(self.results_model, field, (getattr(self.calculation_model, field) * float(self.process_total_quantity)))

    def save(self, *args, **kwargs):
        #this will repair instance if it is not correct
        if self.results_model is None:
            self.results_model = Lca_Database_Process.objects.filter(id = on_create_default_process()).get()
        if self.calculation_model is None:
            self.calculation_model = Lca_Database_Process.objects.filter(id = on_create_default_process()).get()

        self.set_gui_category()
        self.set_transport()
        self.get_computed()
        if self.name == Lca_Database_Process._meta.get_field('name').get_default():
            self.name = self.calculation_model.name
        self.results_model.save()
        super(Instance_Idemat_Database_Process, self).save(*args, **kwargs)

    def set_transport(self):
         if self.process_type == "PTYPE3_TRANSPORT":
             from EcoMan.models import Lca_Part
             lca_part_query = Lca_Part.objects.filter(lca_process_model__id = self.id)
             if lca_part_query:
                 lca_part = lca_part_query.get()
                 self.process_quantity = lca_part.part_model.weight /1000 * self.transport_distance
    

    def set_gui_category(self):
        try:
            if self.process_model.category_model.name == "materials":
                self.process_type = "PTYPE1_MATERIAL"
            elif self.process_model.category_model.name == "Processing":
                self.process_type = "PTYPE2_MANUFACTURING_PROCESS"
            elif self.process_model.category_model.name == "Transport":
                self.process_type = "PTYPE3_TRANSPORT"
            else:
                self.process_type = "PTYPE0_OTHER"
        except:
            self.process_type = "PTYPE0_OTHER"

    def clone_it(self):
        '''This function creates a duplicate of a Instance_LCA_Process object
            Almost all fields are simple so we will translate to dictionary and exclude process_model snd result_model
            Result_model will be created automatically during save procsess of new_instance
        '''
        from django.forms import model_to_dict
        kwargs = model_to_dict(self, exclude=['id', 'process_model', 'results_model' ])
        kwargs.update({'name': self.name +'_clone'})
        calc_model = Lca_Database_Process.objects.get(pk=self.process_model.pk)
        calc_model.pk = None
        calc_model.accessibility = 'HIDDEN'
        calc_model.save()

        kwargs.pop('calculation_model') # calculation model ist one to one field so it has to be duplicated with a new pk
        new_instance = Instance_Idemat_Database_Process.objects.create(process_model = self.process_model, calculation_model = calc_model, **kwargs)

        #post creation
        new_instance.color = get_random_color()
        new_instance.save()
        return new_instance

    def as_dict(self) ->dict:
        '''this function will create custom instance process dictionary
        '''
        entry = {}

        #sum all the processes for a single part
        entry.update({self.__str__() : {}})
        entry_self = entry[self.__str__()]
        entry_self.update(model_to_dict(self, exclude=[ 'process_model', 'results_model' ]))
        entry_self.update({'owner': str(entry_self['owner'])})
        entry_self.update({'lca_input': model_to_dict(self.process_model)})

        entry_self.update({'lca_result': {}})
        for lca_field in self.lca_fields:
            entry_self['lca_result'].update({ lca_field : getattr(self.results_model, lca_field)} )
        return entry

    class Meta:
        app_label = 'EcoMan'
    def __str__(self):
        return str('ID:' + self.id + ' Name:' + self.name)
    
    @staticmethod
    def create_from_dict(**obj_data):

        create_dict = obj_data.copy()
        create_dict.pop("lca_result")
        create_dict.pop("lca_input")
        create_dict.pop("id")

        lca_input=Lca_Database_Process.objects.all()
        lca_input = lca_input.filter(name = obj_data['lca_input']['name']).get()
        create_dict.update({"process_model": lca_input})
        return Instance_Idemat_Database_Process.objects.create(**create_dict)


