from django.db import models
from math import *
import uuid
from CatiaFramework.models.help_functions import *
from CatiaFramework.scripts import *
from website.settings import MEDIA_ROOT
def SessionCustomUploadPath(instance, filename):
    '''Dynamic Upload To
    '''
    filename, file_extension = os.path.splitext(filename)
    match file_extension:

        case ".wrl":
            # Generate unique filename
            filename = instance.name + "_" + str(instance.UUID) + ".wrl"
        case ".CATPart":
            # Generate unique filename
            filename = instance.name + "_" + str(instance.UUID) + ".CATPart"    

    # Construct the final path and check for existance
    final_path = os.path.join("workflow_sessions" , f"User_{str(instance.owner.UUID)}" , "instances")
    sessions_dir = os.path.join(MEDIA_ROOT, "workflow_sessions")
    user_dir = os.path.join(sessions_dir, f"User_{str(instance.owner.UUID)}")
    instances_dir = os.path.join(user_dir, "instances")
    None if os.path.exists(sessions_dir) else os.mkdir(sessions_dir)
    None if os.path.exists(user_dir) else os.mkdir(user_dir)
    None if os.path.exists(instances_dir) else os.mkdir(instances_dir)

    return os.path.join(final_path,filename )



class Workflow_Session(models.Model):

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
      
    workflow_model = models.ForeignKey("CatiaFramework.Workflow", verbose_name="Workflow Template of this Sesion", related_name='workflowss_reference_sessions', on_delete=models.CASCADE,  default=None)
    session_metadata = models.JSONField(verbose_name="Session Metadata", editable=True, default=dict)


    PROTECTIONCLASS_CHOICES= [
    ("PUBLIC", ("Public")),
    ("INTERNAL", ("Internal")),
    ("CONFIDENTIAL", ("Confidential")),
    ("STRICTLY_CONFIDENTIAL", ("Strictly Confidential")),
    ]
    protection_class = models.CharField(choices=PROTECTIONCLASS_CHOICES, verbose_name="Analysis protection class",max_length=100, default="CONFIDENTIAL",)





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
        for field in Workflow_Session._meta.get_fields():
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
    
    def get_all_instances(self):
        all_stages = self.workflow_model.get_all_stages()
        instances_list = []

        for stage in all_stages:

            templates = stage.get_all_templates()
            for template in templates:
                instances = template.instances.all()
                for instance in instances:
                    instances_list.append(instance)
        return instances_list
