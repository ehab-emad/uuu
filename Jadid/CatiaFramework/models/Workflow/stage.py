from django.db import models
from math import *
from django.db.models import Q
import uuid
from CatiaFramework.models.help_functions import *
from CatiaFramework.scripts import *
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction


class Workflow_Stage(models.Model):   #should be LCA_Process

    #standard fields
    UUID = models.UUIDField(primary_key=True, verbose_name="UUID",   default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=1000,   editable=True, blank=True,null=True,)
    description = models.CharField(max_length=1000,   editable=True, blank=True,null=True,)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey("CatiaFramework.ProjectUser_CatiaFramework_Ref", models.SET_NULL, blank=True,null=True,)
    thumbnail = models.ImageField(upload_to ='uploads/', null=True, blank=True, verbose_name = "Thumbnail")
    gif = models.ImageField(upload_to ='uploads/', null=True, blank=True, verbose_name = "Animated Thumbnail")
    project_model=models.ForeignKey("CatiaFramework.Project_CatiaFramework_Ref", verbose_name="Project", on_delete=models.CASCADE, help_text ="Select a a project for Shared Component", default=None, blank=True,null = True )
    instruction=models.OneToOneField("CatiaFramework.Workflow_Instruction", verbose_name="Instruction", on_delete=models.CASCADE)  
    
    parent_stage = models.ForeignKey("CatiaFramework.Workflow_Stage", verbose_name="Parent Stage", related_name='stages_children_stages', on_delete=models.CASCADE, help_text ="Parent Dependent Session", default=None, blank=True, null = True)
    parent_workflow = models.ForeignKey("CatiaFramework.Workflow", verbose_name="Parent Workflow", related_name='workflows_children_stages', on_delete=models.CASCADE, help_text ="Parent Worf", default=None, blank=True, null = True)

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

    #options
    is_active = models.BooleanField(default =False, verbose_name="Is Active For User Interaction")    
                                                                    
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
        for field in Workflow_Stage._meta.get_fields():
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
                if field.name == 'parent_stage':          
                    if getattr(self, field.attname):                              
                        entry[field.name] = str(Workflow_Stage.objects.filter(UUID = str(self.parent_stage.UUID)).get().UUID)
                    else:
                        entry[field.name] = None
                if field.name == 'parent_workflow':          
                    if getattr(self, field.attname):   
                        from CatiaFramework.models import Workflow                           
                        entry[field.name] = str(Workflow.objects.filter(UUID = str(self.parent_workflow.UUID)).get().UUID)
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
        if self.parent_stage:
            return str(f'Stage: {str(self.name)} Of: {str(self.parent_stage.name)} UUID: {str(self.UUID)}')
        else:
            return str(f'Stage: {str(self.name)} Of: ?Root? UUID: {str(self.UUID)}')       


    def __init__(self, *args, **kwargs):
        super(Workflow_Stage, self).__init__(*args, **kwargs)
        from .instruction import Workflow_Instruction
        try:
            self.instruction
        except:
            self.instruction = Workflow_Instruction.objects.create()

    def get_structure_dict_TEST(self, session_UUID=None, preview=False):
        from CatiaFramework.models import Workflow_Action
        stage_dict = self.as_dict()
        stage_dict['objects'] = []
        stage_dict['actions'] = []

        if not preview:
            root_objects = self.get_root_objects().prefetch_related(
                'instances__workflow_session'
            )
            
            for root_object in root_objects:
                root_object_dict = root_object.as_dict()
                root_object_dict['instances'] = [
                    instance.as_dict() 
                    for instance in root_object.instances.all() 
                    if instance.workflow_session and str(instance.workflow_session.UUID) == session_UUID
                ]
                root_object_dict['actions'] = []
                
                actions = Workflow_Action.objects.filter(
                    parent_object=root_object
                ).select_related('parent_action').prefetch_related('actions_children_actions')
                
                root_actions = [action for action in actions if action.parent_action is None]
                
                for root_action in root_actions:
                    action_dict = root_action.as_dict()
                    action_dict['actions'] = []
                    current_action = root_action
                    
                    while current_action.actions_children_actions.first():
                        next_action = current_action.actions_children_actions.first()
                        next_action_dict = next_action.as_dict()
                        action_dict['actions'].append(next_action_dict)
                        current_action = next_action
                    
                    root_object_dict['actions'].append(action_dict)
                    
                stage_dict['objects'].append(root_object_dict)
            
            root_actions = self.get_root_actions().select_related('parent_action').prefetch_related('actions_children_actions')
            
            for root_action in root_actions:
                action_dict = root_action.as_dict()
                action_dict['actions'] = []
                current_action = root_action
                
                while current_action.actions_children_actions.first():
                    next_action = current_action.actions_children_actions.first()
                    next_action_dict = next_action.as_dict()
                    action_dict['actions'].append(next_action_dict)
                    current_action = next_action
                
                stage_dict['actions'].append(action_dict)
        
        return stage_dict

    

    def get_structure_dict(self, session_UUID = None, preview = False, instances = True):
        from CatiaFramework.models import Workflow_Action
        stage_dict=dict()
        stage_dict =self.as_dict()                
        stage_dict['objects'] = list()
        stage_dict['actions'] = list()

        if not preview:
            for root_object in self.get_root_objects():
                while root_object is not None:                                   
                    stage_dict['objects'].append(dict())  
                    stage_dict['objects'][-1] =root_object.as_dict()                      
                    stage_dict['objects'][-1]['instances'] = list()
                    stage_dict['objects'][-1]['actions'] = list()  
                    if instances:
                        for instance in root_object.instances.select_related('workflow_session').filter(workflow_session__UUID = session_UUID ):
                            #we are only interested in instances to session_UUID otherwise list will remain empty
                            #if instance.workflow_session:
                                #if str(instance.workflow_session.UUID) == session_UUID:
                            stage_dict['objects'][-1]['instances'].append(dict())
                            stage_dict['objects'][-1]['instances'][-1] = instance.as_dict()    


                    #find root action
                    actions = Workflow_Action.objects.filter(parent_object = root_object)
                    root_actions = actions.filter(parent_action__isnull=True)                     
                    #root_actions = Workflow_Action.objects.filter(Q(parent_object = root_object) & Q(parent_action__isnull=True))   
                    for root_action in root_actions:
                        stage_dict['objects'][-1]['actions'].append(dict()) 
                        stage_dict['objects'][-1]['actions'][-1] = root_action.as_dict()               
                        stage_dict['objects'][-1]['actions'][-1]['actions'] = list()  
                        while root_action.actions_children_actions.first() is not None:
                            root_action = root_action.actions_children_actions.first()
                            stage_dict['objects'][-1]['actions'].append(dict())                     
                            stage_dict['objects'][-1]['actions'][-1] = root_action.as_dict() 
                    root_object = root_object.objects_children_objects.first() 

    
                
            for root_action in self.get_root_actions():
                stage_dict['actions'].append(dict()) 
                stage_dict['actions'][-1]= root_action.as_dict()                  
                while root_action.actions_children_actions.first() is not None:
                    root_action = root_action.actions_children_actions.first()
                    stage_dict['actions'].append(dict())                     
                    stage_dict['actions'][-1] = root_action.as_dict() 
 
        return stage_dict

    def duplicate(self):
            # Create a new instance with the same field values
            duplicated_object = Workflow_Stage(**{field.name: getattr(self, field.name) for field in self._meta.fields})
            # Set primary key to None to create a new object
            duplicated_object.UUID = uuid.uuid4()
            from CatiaFramework.models import  Workflow_Instruction            
            from CatiaFramework.models import  Workflow_Instruction  
            if duplicated_object.instruction is not None:
                new_instruction = duplicated_object.instruction.duplicate()         
            else:
                new_instruction = Workflow_Instruction.objects.create() 
            duplicated_object.instruction = new_instruction
            # Save the new object to the database
            duplicated_object.save()
            return duplicated_object    
    
    def duplicate_recursively(self, parent_workflow = None, parent_stage= None):
        #create master object
        new_stage = self.duplicate()
        new_stage.parent_workflow = parent_workflow
        new_stage.parent_stage = parent_stage        
        new_stage.type = "SESSION"

        children = self.stages_children_stages.first()
        if children:
            children.duplicate_recursively(parent_workflow = parent_workflow, parent_stage = new_stage)

        #find root actions
        root_actions = self.get_root_actions().all()
        for action in root_actions:
            action.duplicate_recursively(parent_stage = new_stage, parent_object = None,  parent_action = None)

        #find root objects
        root_objects = self.get_root_objects().all()
        for object in root_objects:
            object.duplicate_recursively(parent_stage = new_stage, parent_object = None)
        new_stage.save()

    def get_root_stage(self):
        '''Find root stage object iteratively'''
        current_stage = self

        while current_stage.parent_stage is not None:
            current_stage = current_stage.parent_stage

        return current_stage
    
    def get_last_stage(self):
        '''Find the last stage object iteratively'''
        current_stage = self
        while current_stage.stages_children_stages.first() is not None:
            current_stage = current_stage.stages_children_stages.first()
        return current_stage 
         
    
    def get_root_objects(self):
        ''' find root stage object
        '''
        from CatiaFramework.models import Workflow_Object
        objects = Workflow_Object.objects.filter(parent_stage = self)
        return objects.filter(parent_object__isnull=True) 
    
    def get_root_actions(self):
        ''' find root actions
        '''
        from CatiaFramework.models import Workflow_Action
        actions= Workflow_Action.objects.filter(parent_stage = self)
        return actions.filter(parent_action__isnull=True) 
    
    def get_status_icon(self):
        """
        function will call static function and retrieve correct icon for self status
        """
        from CatiaFramework.models.Workflow.status_functions import get_status_icon
        return get_status_icon(self)


    def set_status(self, status:str=None):
        '''override method to set the status
        '''
        if status:
            self.status = status
        else:
            self.status = "UNKNOWN"

    def get_parent_stages(self):
        '''
        '''      
        stages = []
        last_stage = self
        while last_stage.parent_stage is not None:
            last_stage = last_stage.parent_stage
            stages.append(last_stage)
        return stages

    def get_all_templates(self):
        from CatiaFramework.models import Workflow_Object
        return Workflow_Object.objects.filter(parent_stage = self)




@receiver(post_save, sender=Workflow_Stage)
def Workflow_Stage_post_save(sender, instance, created = None, **kwargs):
    #find reference workflow model and save it to update static dicitonary
    root_stage = instance.get_root_stage()
    if root_stage.parent_workflow:
        root_stage.parent_workflow.modified = True
        root_stage.parent_workflow.save()