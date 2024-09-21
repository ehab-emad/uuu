import os, json
from .views import *
from django.shortcuts import render
from django.contrib import messages
from django.db.models import ProtectedError
from django.http import HttpResponse, JsonResponse 
from django.shortcuts import  get_object_or_404, redirect
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.urls import reverse
from NormMan.models import NormParts_Shared_Component
from NormMan.Views.shared_component_workflow_session_dashboard import load_workflow_details
from NormMan.scripts.meta_replication import valid
from CatiaFramework.models import Workflow_Object, Workflow_Stage, Workflow_Session
from website.models import ProjectUser
from website.settings import MEDIA_ROOT, BASE_DIR
from django import forms
from django_keycloak.keycloak_manager import keycloak_manager


def Get_Dotnet_Library(request, library_UUID):
    '''
    This funvz
    '''    
    try:     
        if request.method == 'GET': 
            static_path = "norm_parts/static_files/framework"
            path = f'{MEDIA_ROOT}/{static_path}/meta.json'.replace("\\","/")
            with open(path, "r") as meta:
                meta_data = json.loads(meta.read())
            # archive_to_export = open(os.path.join(meta_data["file_path"], meta_data["file"]), "rb") if meta else None
            # batch_to_export = open(os.path.join(meta_data["file_path"], meta_data["batch"]), "rb") if meta else None
            # archive_to_export = os.path.join(meta_data["file_path"], meta_data["file"])if meta else None
            # batch_to_export = os.path.join(meta_data["file_path"], meta_data["batch"]) if meta else None                            

            # with zipfile.ZipFile(os.path.join(meta_data["file_path"],'framework.zip'), 'w', zipfile.ZIP_STORED) as zipf:
            #     # Here we write into folder
            #     zipf.write(archive_to_export, meta_data["file"])
            #     zipf.write(batch_to_export, meta_data["batch"])
            #     zipf.close        
            
            # Here we check for user that is to be downloading a framework.
            # We open file containing users and update it accordingly.
        
            meta_data["users"].update({request.user.username: request.user.username}) if request.user.username not in meta_data["users"] else None
            with open(path, "w") as meta:
                meta.write(json.dumps(meta_data, indent = 4))

            new_file_path = os.path.join(meta_data["file_path"],'framework.zip')
            if new_file_path:
                response = None
                with open(new_file_path, "rb") as new_zip:
                    response = HttpResponse(new_zip)
                    response['Content-Disposition'] = 'attachement; filename=framework.zip'                                    
                # os.remove(new_file_path)
                return response
            else:
                messages.add_message(request,messages.ERROR, "File not found")
                return redirect(request.META.get('HTTP_REFERER'))


    except ProtectedError:
        messages.add_message(request,messages.ERROR, "No permision")

    except Exception as e:
        messages.add_message(request,messages.ERROR, e)
    return redirect(request.META.get('HTTP_REFERER'))