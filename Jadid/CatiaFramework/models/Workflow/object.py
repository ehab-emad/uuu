from django.db import models
from math import *
import uuid
from CatiaFramework.models.help_functions import *
from CatiaFramework.scripts import *
from django.utils.deconstruct import deconstructible
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .session import SessionCustomUploadPath
from NormMan.scripts import render_allowed



class Workflow_Object(models.Model):   #should be LCA_Process
    UUID = models.UUIDField(primary_key=True, verbose_name="UUID",  editable=False)
    name = models.CharField(max_length=1000,   editable=True, blank=True,null=True,)
    description = models.CharField(max_length=1000,   editable=True, blank=True,null=True,)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey("CatiaFramework.ProjectUser_CatiaFramework_Ref", models.SET_NULL, blank=True,null=True,)
    is_public = models.BooleanField(default =False, verbose_name="Job will be visible for other colleagues within the same project" )
    thumbnail = models.ImageField(upload_to ='uploads/', null=True, blank=True, verbose_name = "Thumbnail")
    instruction=models.OneToOneField("CatiaFramework.Workflow_Instruction", verbose_name="Instruction", on_delete=models.CASCADE)  
    instances = models.ManyToManyField("CatiaFramework.Workflow_Object", verbose_name="Instances", blank=True, related_name='instances_object')
    is_active = models.BooleanField(default =False, verbose_name="Object is activated")  
    is_interactive = models.BooleanField(default =False, verbose_name="Object is activated")  
    parent_object = models.ForeignKey("CatiaFramework.Workflow_Object", verbose_name="Parent Object", on_delete=models.CASCADE, related_name='objects_children_objects', default=None, blank=True, null = True)  
    parent_stage = models.ForeignKey("CatiaFramework.Workflow_Stage", verbose_name="Parent Stage", on_delete=models.CASCADE, related_name='stages_children_objects', help_text ="Parent Dependent Session", default=None, blank=True, null = True)     
    reference_instance = models.ForeignKey("CatiaFramework.Workflow_Object", verbose_name="Reference to instance in other session", on_delete=models.CASCADE, related_name='objects_referenced_instances', default=None, blank=True, null = True)  
    required_objects = models.ManyToManyField("CatiaFramework.Workflow_Object", verbose_name="Required Objects", blank=True,  default=None)
    required_actions = models.ManyToManyField("CatiaFramework.Workflow_Action", verbose_name="Required Actions", blank=True,  default=None)
    instance_parameters = models.JSONField(verbose_name="Instance Parameters", editable=True, null= True, blank=True)
    instance_framework_metadata = models.JSONField(verbose_name="Instance Framework Metadata", editable=True, null= True, blank=True)
    workflow_session = models.ForeignKey("CatiaFramework.Workflow_Session", verbose_name="Workflow Session", on_delete=models.CASCADE, related_name='sessions_object_instances', default=None, blank=True, null = True)  
    catia_representation = models.FileField( upload_to=SessionCustomUploadPath, verbose_name="3D Catia representation", blank=True, null=True,)
    wrl_representation = models.FileField( upload_to=SessionCustomUploadPath, verbose_name="3D VRML representation", blank=True, null=True,)
    norman_reference = models.UUIDField(verbose_name="UUID NorMan",  editable=False, blank=True, null=True,) #as UUID to keep database structure simple as possible
    ACCESSIBILITY_CHOICE= [
    ("PRIVATE", ("Private")),
    ("DATABASE_USERS", ("Database Users")),
    ("PROJECT_USERS", ("Project Users")),    
    ]

    accessibility = models.CharField(choices=ACCESSIBILITY_CHOICE, default="private",  max_length=50)

    #status
    STATUS_CHOICE= [
    ("COMPLETED", ("Completed")),    
    ("CANCELLED", ("Cancelled")),
    ("INPROGRESS", ("In Progress")),             
    ("PENDING", ("Pending")),  
    ("UNKNOWN", ("Unknown")),
    ("WAITING", ("Waiting")), 
    ("FAILED", ("Failed")), 
    ("CAUTION", ("Caution")),            
    ]
    status = models.CharField(choices=STATUS_CHOICE, default="UNDEFINED",  max_length=50)
     
    TYPE_CHOICE= [
    ("INSTANCE", ("Instance")),  
    ("REFERENCE", ("Reference")),  
    ("TEMPLATE", ("Template")),  
    ("FRAMEWORK_INTERNAL", ("Framework Internal")),  
    ]

    type = models.CharField(choices=TYPE_CHOICE, default="STAGE",  max_length=50)


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
        for field in Workflow_Object._meta.get_fields():
            if type(field).__qualname__ == "ManyToManyField":
                entry[field.attname] =[str(object.UUID) for object in entry[field.attname]]

            if type(field).__qualname__ == "ImageField":
                if getattr(self, field.attname):
                    entry[field.attname] = getattr(self, field.attname).url
                else:
                    entry[field.attname] = None

            if type(field).__qualname__ == "FileField":
                if getattr(self, field.attname):                
                    entry[field.attname] = getattr(self, field.attname).url
                else:
                    entry[field.attname] = None

            #reference_instance
            if type(field).__qualname__ == "ForeignKey":
                if field.name == 'reference_instance':          
                    if getattr(self, field.attname):                              
                        entry[field.name] = str(Workflow_Object.objects.filter(UUID = str(self.reference_instance.UUID)).get().UUID)
                    else:
                        entry[field.name] = None

        # Iterate through the dictionary
        for key, value in entry.items():
            # Check if the value is of type UUID
            if isinstance(value, uuid.UUID):
                # Convert the UUID to a string
                entry[key] = str(value)                
        return entry
    
    def __str__(self):
        return str(f'Object: {str(self.name)} UUID: {str(self.UUID)}')


    @render_allowed
    def __init__(self, *args, **kwargs):
        uuid_value = kwargs.pop('uuid_value', None)
        super(Workflow_Object, self).__init__(*args, **kwargs)
        from .instruction import Workflow_Instruction
        try:
            self.instruction
        except:
            self.instruction = Workflow_Instruction.objects.create()

        if uuid_value:
            self.UUID = uuid_value
        else:
            if self.UUID:
                self.UUID = self.UUID
            else:
                self.UUID = uuid.uuid4()

    def get_root_actions(self):
        ''' find root actions
        '''
        from CatiaFramework.models import Workflow_Action
        actions= Workflow_Action.objects.filter(parent_object = self)
        return actions.filter(parent_action__isnull=True)
    
    def get_root_object(self):
        '''Find root object iteratively'''
        current_object = self

        while current_object.parent_object is not None:
            current_object = current_object.parent_object

        return current_object
    


    def get_last_object(self):
        '''Find the last object object iteratively'''
        current_object = self
        while current_object.objects_children_objects.first() is not None:
            current_object = current_object.objects_children_objects.first()
        return current_object 


    def duplicate(self):
        # Create a new instance with the same field values
        duplicated_object = Workflow_Object(**{field.name: getattr(self, field.name) for field in self._meta.fields})
        # Set primary key to None to create a new object
        duplicated_object.pk = None
        duplicated_object.UUID = uuid.uuid4()        
        from CatiaFramework.models import  Workflow_Instruction            
        if duplicated_object.instruction is not None:
            new_instruction = duplicated_object.instruction.duplicate()         
        else:
            new_instruction = Workflow_Instruction.objects.create() 
        duplicated_object.instruction = new_instruction
        # Save the new object to the database
        duplicated_object.save()
        return duplicated_object       
     
    def duplicate_recursively(self, parent_stage = None, parent_object = None):
        #create self duplicate
        new_object = self.duplicate()   
        #deal with reffered objects
        new_object.parent_object = parent_object
        new_object.parent_stage = parent_stage
        new_object.required_actions
        new_object.required_objects
        new_object.save()   

        #search for cildren actions
        children = self.objects_children_objects.all()
        for child in children:
            child.duplicate_recursively(parent_stage = parent_stage, parent_object = new_object)

        #find root actions
        root_actions = self.get_root_actions().all()
        for action in root_actions:
            action.duplicate_recursively(parent_stage = None, parent_object = new_object,  parent_action = None)

    def get_status_icon(self):
        """
        function will call static function and retrieve correct icon for self status
        """
        from CatiaFramework.models.Workflow.status_functions import get_status_icon
        return get_status_icon(self)
        



    def set_status(self, status:str=None):
        """override method to set the status. Django cannot decide about the status of the action it can be only made with help of a workflow or addon
        """
        if status:
            self.status = status
        else:
            self.status = "UNKNOWN"        
    
    def get_status(self):
        """
        Live query of the status 
        """        
        if self.type == "INSTANCE":
            #Status of the instance depends from status of actions corresponding to Object Template
            pass


        if self.type == "TEMPLATE":            
            #Status of the template depends from status of instances corresponding to Object Template
            pass

    def get_parent_templates(self):
        '''
        Get only parent template objects given input object
        for specified stage
        '''      
        templates = list()
        last_object = self
        while last_object.parent_stage is None and (last_object := last_object.parent_object) is not None and templates.append(last_object): pass
        return templates



    def get_all_templates(self):
        '''
        Get all the templates last object given input object for
        specified stage.
        '''      
        templates = list()
        last_object = self.get_last_object()
        templates.append(last_object)
        while last_object.parent_stage is None and (last_object := last_object.parent_object) is not None and templates.append(last_object): pass
        return templates
    

    
    
@receiver(pre_delete, sender=Workflow_Object)
@receiver(post_save, sender=Workflow_Object)
def Workflow_Object_post_save(sender, instance = None, created = None, **kwargs):
    #find reference workflow model and save it to update static dicitonary
    if instance.type == "TEMPLATE":
        root_object= instance.get_root_object()
        if root_object.parent_stage:
            root_stage = root_object.parent_stage.get_root_stage()
            if root_stage.parent_workflow:
                root_stage.parent_workflow.modified = True
                root_stage.parent_workflow.save()
