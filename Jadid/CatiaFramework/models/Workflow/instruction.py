from django.db import models
from math import *
import uuid
from CatiaFramework.models.help_functions import *
from CatiaFramework.scripts import *
from CatiaFramework.models import DotNet_ProjectFolder

class Workflow_Instruction(models.Model):   #should be LCA_Process
    UUID = models.UUIDField(primary_key=True, verbose_name="UUID",   default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=1000,   editable=True, blank=True,null=True,)
    description = models.CharField(max_length=1000,   editable=True, blank=True,null=True,)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    thumbnail = models.ImageField(upload_to ='uploads/', null=True, blank=True, verbose_name = "Instruction Image/Animation")

    class Meta:
        app_label = 'CatiaFramework'        

    def as_dict(self) ->dict:
        '''convert instance to dictionary
        '''
        from django.forms import model_to_dict
        entry = {}

        entry.update({"UUID": str(self.UUID)})
        entry.update(model_to_dict(self))
        entry.update({"CLASS_name": self.__class__.__name__})
        for field in Workflow_Instruction._meta.get_fields():
            if type(field).__qualname__ == "ManyToManyField":
                entry[field.attname] =[str(object.UUID) for object in entry[field.attname]]
        return entry
    
    def __str__(self):
        return str(f'Action: {str(self.name)} UUID: {str(self.UUID)}')
    
    def duplicate(self):
            # Create a new instance with the same field values
            duplicated_object = Workflow_Instruction(**{field.name: getattr(self, field.name) for field in self._meta.fields})
            # Set primary key to None to create a new object
            duplicated_object.pk = None
            # Save the new object to the database
            duplicated_object.save()
            return duplicated_object    