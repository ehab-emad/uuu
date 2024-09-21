from django.db import models
from math import *
import uuid
from CatiaFramework.models.help_functions import *
from CatiaFramework.scripts import *
from CatiaFramework.models import DotNet_ProjectFolder

# Helper function to rename files based on UUID and file type
def rename_file(instance, filename, file_type):
    # Get file extension
    extension = os.path.splitext(filename)[1]
    # Generate file name based on the UUID and file type
    new_filename = f"{instance.UUID}_{file_type}{extension}"
    # Define the folder path
    folder_name = os.path.join('libraries', str(instance.UUID))
    return os.path.join(folder_name, new_filename)

# Function to rename library files (DLLs)
def library_file_path(instance, filename):
    return rename_file(instance, filename, 'library')

# Function to rename meta files
def meta_file_path(instance, filename):
    return rename_file(instance, filename, 'meta')

# Function to rename logo files (PNGs, JPGs, etc.)
def thumbnail_file_path(instance, filename):
    return rename_file(instance, filename, 'thumbnail')


class DotNet_Component(models.Model):   #should be LCA_Process
    UUID = models.UUIDField(primary_key=True, verbose_name="UUID",   default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=1000,   editable=True, blank=True,null=True,)
    description = models.CharField(max_length=1000,   editable=True, blank=True,null=True,)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey("CatiaFramework.ProjectUser_CatiaFramework_Ref", models.SET_NULL, blank=True,null=True,)
    is_public = models.BooleanField(default =False, verbose_name="Job will be visible for other colleagues within the same project" )
    thumbnail = models.FileField(upload_to=thumbnail_file_path, blank=True, null=True)
    project_model=models.ForeignKey("CatiaFramework.Project_CatiaFramework_Ref", verbose_name="Project", on_delete=models.CASCADE, help_text ="Select a a project for Shared Component", default=None, blank=True, )
    library_file = models.FileField(upload_to=library_file_path, null=True, blank=True)  # For library files (.dll)
    meta = models.FileField(upload_to=meta_file_path, blank=True, null=True)  # For meta files

    comment_section = models.CharField(max_length=100000,   editable=True, blank=True,null=True,)
    content_section = models.CharField(max_length=3000000,   editable=True, blank=True,null=True,)
    summary_section = models.CharField(max_length=10000,   editable=True, blank=True,null=True,)    
    
    MODIFIER_CHOICE= [
    ("PUBLIC", ("vb.net Public")),
    ("PRIVATE", ("vb.net Private")),
    ("PROTECTED", ("vb.net sub Protected")),    
    ("FRIEND", ("vb.net Friend")), 
    ("PROTECTED", ("vb.net Protected")), 
    ("NONE", ("None")),     
    ]

    access_modifier = models.CharField(choices=MODIFIER_CHOICE, default="private",  max_length=50)    

    TYPE_CHOICE= [
    ("VBDOTNET_CLASS", ("vb.net class")),
    ("VBDOTNET_LIBRARY", ("vb.net library")),
    ("VBDOTNET_MODULE", ("vb.net module")),
    ("VBDOTNET_SUB", ("vb.net sub procedure")),    
    ("VBDOTNET_FUNCTION", ("vb.net function")), 
    ("VBDOTNET_PROPERTY", ("vb.net property")), 
    ("DJANGO_VIEW", ("Django view")), 
    ("UNDEFINED", ("Undefined")),     
    ]

    type = models.CharField(choices=TYPE_CHOICE, default="UNDEFINED",  max_length=50)



    ACCESSIBILITY_CHOICE= [
    ("PRIVATE", ("Private")),
    ("DATABASE_USERS", ("Database Users")),
    ("PROJECT_USERS", ("Project Users")),    
    ]

    accessibility = models.CharField(choices=ACCESSIBILITY_CHOICE, default="private",  max_length=50)


    #static properties (used and saved only from framework)
    status ={"status": {
                    "result_object": None,
                    "is_done": False,
                    "in_progress": False,
                    "log": {},
                    "is_automatic": None,
                    "is_active": False,
                    "show": False,
                    "dependancy": None
                    }
            }
                      
    class Meta:
        app_label = 'CatiaFramework'        

    def as_dict(self) ->dict:
        '''convert instance to dictionary
        '''
        from django.forms import model_to_dict
        entry = {}

        entry.update({"UUID": str(self.UUID)})
        entry.update(model_to_dict(self))

        for field in DotNet_ProjectFolder._meta.get_fields():
            if type(field).__qualname__ == "ManyToManyField":
                entry[field.attname] =[str(object.UUID) for object in entry[field.attname]]
        return entry
    
    def __str__(self):
        return str(f'DotNet_Component: {str(self.UUID)}')


