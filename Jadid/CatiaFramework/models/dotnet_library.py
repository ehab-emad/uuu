import os, json, uuid
from django.conf import settings
from django.db import models
from math import *
from NormMan.models.help_functions import *
from NormMan.models.Component_Group_Level import *
from NormMan.scripts import render_allowed


# Helper function to rename files based on UUID and file type
def rename_file(instance, filename, file_type):
    # Get file extension
    extension = os.path.splitext(filename)[1]
    # Generate file name based on the UUID and file type
    new_filename = f"{instance.uuid}_{file_type}{extension}"
    # Define the folder path
    folder_name = os.path.join('libraries', str(instance.uuid))
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


class Dotnet_Library(models.Model):   #should be LCA_Process
    UUID = models.UUIDField(primary_key=True, verbose_name="UUID",   default=uuid.uuid4, editable=True)
    data_path = models.CharField(editable=True, blank=True,null=True, max_length=50000)
    name = models.CharField(max_length=1000,   editable=True, blank=True,null=True,)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey("NormMan.ProjectUser_NormMan_Ref", models.SET_NULL, blank=True,null=True,)
    project_model=models.ForeignKey("NormMan.Project_NormMan_Ref", verbose_name="Project", on_delete=models.CASCADE, help_text ="Select a project for Shared Component", default=None, blank=True, )

    library_file = models.FileField(upload_to=library_file_path, null=True, blank=True)  # For library files (.dll)
    meta = models.FileField(upload_to=meta_file_path, blank=True, null=True)  # For meta files
    thumbnail = models.FileField(upload_to=thumbnail_file_path, blank=True, null=True)  # For logo files (e.g., .png, .jpg)

    source=models.CharField(max_length=1000,   editable=True, blank=True, )
    is_token_required = models.BooleanField(default =True )


    class Meta:
        app_label = 'CatiaFramework'
    def __str__(self):
        return str(self.name)





