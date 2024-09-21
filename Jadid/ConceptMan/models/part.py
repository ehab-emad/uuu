from django.forms.models import model_to_dict
from django.db import models
from django.urls import reverse
from website.models import Vehicle
from website.generate_pk import generate_pk
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from EcoMan.scripts import get_random_color        
NONNEGATIVE_VALIDATOR = [MinValueValidator(0),]

class Part(models.Model):
    id = models.CharField(default=generate_pk, primary_key=True, max_length=255, unique=True)    
    name = models.CharField(max_length=100,  default= 'Not defined', editable=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey("ConceptMan.ProjectUser_ConceptMan_Ref", models.SET_NULL, blank=True,null=True,)
    diagram_color = models.CharField(max_length=7,  default= get_random_color, editable=True, blank=False)

    WE_CHOICES= [
    ("WE1", ("Area and thickness: Weight = Area * thickness * Material_density")),
    ("WE2", ("Volume: Weight = Volume * Material_density")),
    ("WE3", ("Weight: Weight = Input_weight")),
    ]
    weight_calculation = models.CharField(choices=WE_CHOICES, max_length=32, default="WE3")

    thickness = models.FloatField(editable=True, verbose_name= "Thickness (m)", blank=True,null=True,)    
    engineering_material = models.ForeignKey("MatMan.Engineering_Material", help_text="Select material", on_delete=models.CASCADE, default=None, blank=True, null=True,)
    volume = models.FloatField(editable=True, verbose_name= "Volume (m3)", blank=True,null=True,)
    weight = models.FloatField(editable=True, verbose_name= "Weight (kg)", default=0, validators=NONNEGATIVE_VALIDATOR,)
    area = models.FloatField(editable=True, verbose_name= "Area (m2)", blank=True,null=True,)
    logo = models.ImageField(upload_to ='uploads/', null=True, blank=True, verbose_name = "Part Image")
    process_model=models.ManyToManyField("ConceptMan.Manufacturing_Process", verbose_name="Process", help_text ="Select one or more processes", default=None, blank=True,)  





    def clone_it(self):
        '''This function creates a duplicate of a Part object
            Almost all fields are simple so we will translate to dictionary and exclude process_model
        '''

        from django.forms import model_to_dict
        kwargs = model_to_dict(self, exclude=['id', 'process_model', 'owner'])
        kwargs.update({'name': self.name +'_clone'})
        new_instance = Part.objects.create(**kwargs)
        new_instance.owner = self.owner
        #post creation
        new_instance.diagram_color = get_random_color()
        new_instance.save()
        return new_instance

    def as_dict(self) ->dict:
        '''this function will create custom dictionary for a part object
        '''
        entry = {}
        entry.update(model_to_dict(self, exclude =['process_model', 'logo'] ))
        entry.update({'owner' : str(entry['owner'])} )
        return entry

    def get_weight_in_units(self, units):
        if units == 'kg' or units == 'KILOGRAMS':
            return self.weight
        if units == 'g' or units == 'GRAMS':       
            return self.weight * 1000

    class Meta:
        app_label = 'ConceptMan'
    def __str__(self):
        return str('ID:' + self.id + ' Name:' + self.name) 
    

