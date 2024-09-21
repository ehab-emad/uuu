from django.db import models
from math import *
import uuid
from CatiaFramework.models.help_functions import *
from CatiaFramework.scripts import *
from django.db.models.signals import pre_delete, post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
class Workflow_Action(models.Model): 
    UUID = models.UUIDField(primary_key=True, verbose_name="UUID",   default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=1000,   editable=True, blank=True,null=True,)
    description = models.CharField(max_length=1000,   editable=True, blank=True,null=True,)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey("CatiaFramework.ProjectUser_CatiaFramework_Ref", models.SET_NULL, blank=True,null=True,)
    is_public = models.BooleanField(default =False, verbose_name="Job will be visible for other colleagues within the same project" )
    thumbnail = models.ImageField(upload_to ='uploads/', null=True, blank=True, verbose_name = "Thumbnail")
    project_model=models.ForeignKey("CatiaFramework.Project_CatiaFramework_Ref", verbose_name="Project", on_delete=models.CASCADE, help_text ="Select a a project for Shared Component", default=None, blank=True, )
    instruction=models.OneToOneField("CatiaFramework.Workflow_Instruction", verbose_name="Instruction", on_delete=models.CASCADE)  
    framework_request = models.UUIDField( verbose_name="Framework Request UUID",   blank=True,null=True,)
    parent_action = models.ForeignKey("CatiaFramework.Workflow_Action", verbose_name="Parent Action", on_delete=models.SET_NULL, related_name='actions_children_actions', default=None, blank=True, null = True)  
    parent_object = models.ForeignKey("CatiaFramework.Workflow_Object", verbose_name="Parent Object", on_delete=models.CASCADE,  related_name='objects_children_actions', help_text ="Parent Dependent Object", default=None, blank=True, null = True)    
    parent_stage = models.ForeignKey("CatiaFramework.Workflow_Stage", verbose_name="Parent Stage", on_delete=models.CASCADE,  related_name='stages_children_actions', help_text ="Parent Dependent Session", default=None, blank=True, null = True)
    required_actions = models.ManyToManyField("CatiaFramework.Workflow_Action", verbose_name="Required Actions", blank=True,  default=None)
    required_objects = models.ManyToManyField("CatiaFramework.Workflow_Object", verbose_name="Required Objects", blank=True,  default=None)
    target_object = models.ForeignKey("CatiaFramework.Workflow_Object", verbose_name="Target Object", on_delete=models.CASCADE,  related_name='objects_trigger_actions', help_text ="Parent Dependent Object", default=None, blank=True, null = True)    
    #url = models.URLField(max_length=200, null=None, blank=True)
    url_route = models.CharField(max_length=1000,   editable=True, blank=True,null=True,)
    #options
    is_active = models.BooleanField(default =False, verbose_name="Object is activated")   
    is_automatic = models.BooleanField(default =False, verbose_name="Action will be called automatically")  
    is_for_all_instances = models.BooleanField(default =False, verbose_name="Execute on all required instances")     
    auverride_parameters = models.BooleanField(default =False, verbose_name="User Custom Parameters on Execution")  
    
    TYPE_CHOICE= [
    ("SESSION", ("Session")),  
    ("TEMPLATE", ("Template")),  
    ("FRAMEWORK_INTERNAL", ("Framework Internal")),  
    ] 

    type = models.CharField(choices=TYPE_CHOICE, default="SESSION",  max_length=50)

    ACCESSIBILITY_CHOICE= [
    ("PRIVATE", ("Private")),
    ("DATABASE_USERS", ("Database Users")),
    ("PROJECT_USERS", ("Project Users")),    
    ]

    accessibility = models.CharField(choices=ACCESSIBILITY_CHOICE, default="PRIVATE",  max_length=50)

    #status this value will be updated based on session metadata or in template with usage of a js
    status = 'WAITING'
                      
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
        # Iterate through the dictionary
        for key, value in entry.items():
            # Check if the value is of type UUID
            if isinstance(value, uuid.UUID):
                # Convert the UUID to a string
                entry[key] = str(value)
        for field in Workflow_Action._meta.get_fields():
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

        entry['status'] = self.status


                
        return entry
    
    def __str__(self):

        if  self.parent_object or self.parent_stage:   
            return str(f'Action: {str(self.name)} UUID: {str(self.UUID)}')
        else:
            return str(f'Action: {str(self.name)} UUID: {str(self.UUID)}    NOT UTILISED! ') 

    def duplicate(self):
            # Create a new instance with the same field values
            duplicated_object = Workflow_Action(**{field.name: getattr(self, field.name) for field in self._meta.fields})
            # Set primary key to None to create a new object
            duplicated_object.pk = None
            from CatiaFramework.models import  Workflow_Instruction            
            if duplicated_object.instruction is not None:
                new_instruction = duplicated_object.instruction.duplicate()         
            else:
                new_instruction = Workflow_Instruction.objects.create() 
            duplicated_object.instruction = new_instruction
            # Save the new object to the database
            duplicated_object.save()
            return duplicated_object       
     
    def duplicate_recursively(self, parent_stage = None, parent_object = None,  parent_action = None):
        #create self duplicate
        new_action = self.duplicate()
        new_action.type = "SESSION"     
        #deal with reffered objects
        new_action.parent_action = parent_action
        new_action.parent_object = parent_object
        new_action.parent_stage = parent_stage
        new_action.required_actions 
        new_action.required_objects 
        new_action.save()   
        #search for cildren actions
        children = self.actions_children_actions.all()
        for child in children:
            child.duplicate_recursively(parent_stage = parent_stage, parent_object = parent_object,  parent_action = parent_action)

    def get_last_action(self):
        '''Find the last stage object iteratively'''
        current_action = self
        while current_action.actions_children_actions.first() is not None:
            current_action = current_action.actions_children_actions.first()
        return current_action 

    def __init__(self, *args, **kwargs):
        super(Workflow_Action, self).__init__(*args, **kwargs)
        from .instruction import Workflow_Instruction
        try:
            self.instruction
        except:
            self.instruction = Workflow_Instruction.objects.create()

    def get_status_icon(self):
        """
        function will call static function and retrieve correct icon for self status
        """
        from CatiaFramework.models.Workflow.status_functions import get_status_icon
        return get_status_icon(self)
        
    def set_status(self, status:str=None):
        '''override method to set the status. Django cannot decide about the status of the action it can be only made with help of a workflow or addon
        '''
        if status:
            self.status = status
        else:
            self.status = "UNKNOWN"

    def get_root_action(self):
        '''Find root action object iteratively'''
        current_action = self

        while current_action.parent_action is not None:
            current_action = current_action.parent_action

        return current_action



# Signal handler for pre_delete
@receiver(pre_delete, sender=Workflow_Action)
def pre_delete_book(sender, instance, **kwargs):
    # If the book has children, reassign them to the book's parent
    for child in instance.actions_children_actions.all():
        child.parent_action = instance.parent_action
        child.save()

    # If the action has a parent, remove it from the required_actions of the parent
    if instance.parent_action:
        instance.parent_action.required_actions.remove(instance)
@receiver(pre_delete, sender=Workflow_Action)
@receiver(post_save, sender=Workflow_Action)
def Workflow_Action_post_save(sender, instance, created = None, **kwargs):
    root_action = instance.get_root_action ()
    #find reference workflow model and save it to update static dicitonary
    if root_action.parent_stage:
        root_stage = root_action.parent_stage.get_root_stage()
        if root_stage.parent_workflow:
            root_stage.parent_workflow.modified = True
            root_stage.parent_workflow.save()           
    if root_action.parent_object:
        if instance.type == "TEMPLATE":
            root_object = root_action.parent_object.get_root_object()
            if root_object.parent_stage:
                root_stage = root_object.parent_stage.get_root_stage()
                if root_stage.parent_workflow:
                    root_stage.parent_workflow.modified = True
                    root_stage.parent_workflow.save()