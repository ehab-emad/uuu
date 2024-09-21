import uuid
from django.db import models
from math import *
from CatiaFramework.models.help_functions import *
from CatiaFramework.scripts import *

class Workflow(models.Model):   #should be LCA_Process
    UUID = models.UUIDField(primary_key=True, verbose_name="UUID",   default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=1000,   editable=True, blank=True,null=True,)
    description = models.CharField(max_length=1000,   editable=True, blank=True,null=True,)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey("CatiaFramework.ProjectUser_CatiaFramework_Ref", models.SET_NULL, blank=True,null=True,)
    is_public = models.BooleanField(default =False, verbose_name="Workflow will be visible for other colleagues within the same project" )
    thumbnail = models.ImageField(upload_to ='uploads/', null=True, blank=True, verbose_name = "Thumbnail")
    project_model=models.ForeignKey("CatiaFramework.Project_CatiaFramework_Ref", verbose_name="Project", on_delete=models.CASCADE, help_text ="Select a a project for Shared Component", default=None, blank=True, null=True)
    version =  models.IntegerField(editable=False, blank=True,null=True, default = 0)    
    instruction=models.OneToOneField("CatiaFramework.Workflow_Instruction", verbose_name="Instruction", on_delete=models.CASCADE)      
    static_structure = models.JSONField(verbose_name="Workflow Structure", editable=True, null= True, blank=True)
    modified = models.BooleanField(default =False, verbose_name="Status flag indicating the need to update the static structure." )
    TYPE_CHOICE= [
    ("USER_SESSION", ("User Session")),  
    ("DATABASE_TEMPLATE", ("Database Template")),  
    ("FRAMEWORK_INTERNAL", ("Framework Internal")),  
    ]

    type = models.CharField(choices=TYPE_CHOICE, default="DATABASE_TEMPLATE",  max_length=50)
    reference_workflow = models.ForeignKey("CatiaFramework.Workflow", verbose_name="Reference Workflow", on_delete=models.CASCADE, help_text ="Reference Definition Workflow", default=None, blank=True, null=True )
    reference_workflow_version =  models.IntegerField(editable=False, blank=True,null=True, default = 0)    

    ACCESSIBILITY_CHOICE= [
    ("PRIVATE", ("Private")),
    ("DATABASE_USERS", ("Database Users")),
    ("PROJECT_USERS", ("Project Users")),    
    ]
    accessibility = models.CharField(choices=ACCESSIBILITY_CHOICE, default="private",  max_length=50)

    #status
    STATUS_CHOICE= [
    ("COMPLETED", ("Completed")),    
    ("CANCELLED", ("Cancellec")),
    ("INPROGRESS", ("In Progress")),             
    ("PENDING", ("Pending")),  
    ("UNKNOWN", ("Unknown")),
    ("WAITING", ("Waiting")), 
    ("FAILED", ("Failed")),        
    ]
    status = models.CharField(choices=STATUS_CHOICE, default="UNDEFINED",  max_length=50)
   
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
        for field in Workflow._meta.get_fields():
            if type(field).__qualname__ == "ManyToManyField":
                entry[field.attname] =[str(object.UUID) for object in entry[field.attname]]

            if type(field).__qualname__ == "ImageField":
                if entry[field.attname]:
                    entry[field.attname] = entry[field.attname].path
                else:
                    entry[field.attname] = None
        # Iterate through the dictionary
        for key, value in entry.items():
            # Check if the value is of type UUID
            if isinstance(value, uuid.UUID):
                # Convert the UUID to a string
                entry[key] = str(value)                         
        return entry
    
    def __str__(self):
        return str(f'Workflow: {str(self.name)} UUID: {str(self.UUID)} TYPE: {str(self.type)} ') 
    

    def __init__(self, *args, **kwargs):
        super(Workflow, self).__init__(*args, **kwargs)
        from .instruction import Workflow_Instruction
        try:
            self.instruction
        except:
            self.instruction = Workflow_Instruction.objects.create()

    def get_structure_dict(self, session_UUID = None, stage_UUID = None, complete = False, instances = True):
        ''' 
        '''
        from CatiaFramework.models import Workflow_Stage
        workflow_object = self
        #organise dictionary of all stage elements
        workflow_dict = list()

        stages_ordered_list =list()

        if self.get_root_stages().first():
            stages_ordered_list.append(self.get_root_stages().first())
        
        child = Workflow_Stage.objects.filter(parent_stage = self.get_root_stages().first()).first()
        while child is not None and (child.parent_workflow_id == self.UUID or child.parent_workflow is None):
            stages_ordered_list.append(child)
            child = Workflow_Stage.objects.filter(parent_stage = child).first()

        #propagate recursively through all branches of the workflow
        
        for stage in stages_ordered_list:
            if complete == False:
                if stage.UUID == stage_UUID:
                    new_list = stage.get_structure_dict(session_UUID = session_UUID, preview = False )
                if stage.UUID != stage_UUID:
                    new_list = stage.get_structure_dict(session_UUID = session_UUID, preview = True)
                if stage_UUID == None:
                    new_list = stage.get_structure_dict(session_UUID = session_UUID, preview = False, instances = False)                    
            else:
                new_list = stage.get_structure_dict(session_UUID = session_UUID, preview = False, instances = instances)                                               
            if new_list:
                workflow_dict.append(new_list)
        return workflow_dict




    def duplicate(self):
            # Create a new instance with the same field values
            duplicated_object = Workflow(**{field.name: getattr(self, field.name) for field in self._meta.fields})
            # Set primary key to None to create a new object
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
        
    def duplicate_recursively(self):
        #create master object
        new_workflow = self.duplicate()      
        new_workflow.type = "USER_SESSION"
        new_workflow.save()
       
        #find root stages
        root_stages = self.get_root_stages().all()
        for stage in root_stages:
            stage.duplicate_recursively(parent_stage = None,  parent_workflow = new_workflow)
        return new_workflow

    def get_root_stages(self):
        '''1 find root stage object
        '''
        from CatiaFramework.models import Workflow_Stage
        stages = Workflow_Stage.objects.filter(parent_workflow_id = str(self.UUID))
        return stages.filter(parent_stage__isnull=True)
    
    def get_all_stages(self):
        from CatiaFramework.models import Workflow_Object
        return self.workflows_children_stages.all()

    def get_status_icon(self):
        from django.templatetags.static import static
        """
        Returns a static icon based on the status choice field.
        Adjust the icon URLs or classes based on your needs.
        """
        if self.status == 'COMPLETED':
            return static('CatiaFramework/Status_Icons/Status_Completed_icon.png') 
        elif self.status == 'CANCELLED':
            return static('CatiaFramework/Status_Icons/Status_Cancelled_icon.png') 
        elif self.status == 'INPROGRESS':
            return static('CatiaFramework/Status_Icons/Status_In_Progress_icon.png') 
        elif self.status == 'PENDING':
            return static('CatiaFramework/Status_Icons/Status_Pending_icon.png') 
        elif self.status == 'UNKNOWN':
            return static('CatiaFramework/Status_Icons/Status_Unknown_icon.png') 
        elif self.status == 'WAITING':
            return static('CatiaFramework/Status_Icons/Status_Waiting_icon.png') 
        elif self.status == 'FAILED':
            return static('CatiaFramework/Status_Icons/Status_Failed_icon.png')
        else:
            return static('CatiaFramework/Status_Icons/Status_Completed_icon.png')
        

    def get_active_object_instances(self) -> list:
        # -> This here is to be then used probably for checking all active instances of a workflow
        from CatiaFramework.models import Workflow_Object, Workflow_Stage
        object_instances = list()
        for stage in Workflow_Stage.objects.filter(parent_workflow_id = str(self.UUID)).all():
            [object_instances.append(inst) for inst in Workflow_Object.objects.filter(models.Q(parent_stage = stage) & models.Q(instances__is_active = True)).all()]
        return object_instances


    def save(self, *args, **kwargs):
        # Update static JSON for the structure
        #self.static_structure = self.get_structure_dict(session_UUID = None, stage_UUID = None, complete = True, instances = False)

        # Call the superclass's save method to actually save the instance
        super(Workflow, self).save(*args, **kwargs)

