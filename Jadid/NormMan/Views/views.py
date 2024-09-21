# Create your views here.
import os, json, logging, zipfile
from .views import *
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib import messages
from django.db.models import ProtectedError
from django.http import HttpResponse, JsonResponse 
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.urls import reverse
from NormMan.models import NormParts_Shared_Component
from NormMan.Views.shared_component_workflow_session_dashboard import load_workflow_details
from NormMan.scripts.meta_replication import valid
from website.models import ProjectUser
from website.settings import MEDIA_ROOT
from django import forms
from django.shortcuts import  get_object_or_404
from django_keycloak.keycloak_manager import keycloak_manager

class Framework(forms.Form):
    shared_component_type = forms.CharField()
    shared_component_UUID = forms.CharField()
    configuration_select = forms.ChoiceField()
    norm_parts_collector = None
    check = forms.BooleanField()

    def __init__(self, *args, **kwargs):
        # instance = kwargs['instance']
        # del kwargs['instance']
        super(Framework, self).__init__(*args, **kwargs)    
        self.fields['shared_component_type'].initial = "something"
        self.fields['shared_component_UUID'].initial = "something"

        @property
        def shared_component_type_property(self):
            return self.fields['shared_component_type'].initial
        
        @property
        def shared_component_UUID_property(self):
            return self.fields['shared_component_UUID'].initial    

    class Meta:
        pass


def framework_download_modal(request):
    form = Framework()        

    data = dict()
    if request.method == 'POST':
        data['form_is_valid'] = True
    else:
        pass
    context = {'form': form}
    data['html_form'] = render_to_string('modal/normpart/framework_download_modal.html', context, request=request),
    return JsonResponse(data)


def FrameworkDownload(request):
    '''
    RIGHT NOW HARDCODED, MIGRATE TO DATABASE SOLUTION (maybe not necessary)
    Function will download requested specific part after GUID
    -> So this function should be able to serve a framework data 
    -> Moreover, we need a framework versioning, so as to inform user,
        whether there is a new version available.
    -> Firstly, we consider just static data, nothing more.
    '''    
    try:     
        if request.method == 'GET': 
            static_path = "norm_parts/static_files/framework"
            path = f'{MEDIA_ROOT}/{static_path}/meta.json'.replace("\\","/")
            with open(path, "r") as meta:
                meta_data = json.loads(meta.read())
            meta_data["users"].update({request.user.username: request.user.username}) if request.user.username not in meta_data["users"] else None
            with open(path, "w") as meta:
                meta.write(json.dumps(meta_data, indent = 4))
            new_file_path = os.path.join(meta_data["file_path"],'framework.zip')
            if new_file_path:
                response = None
                with open(new_file_path, "rb") as new_zip:
                    response = HttpResponse(new_zip)
                    response['Content-Disposition'] = 'attachement; filename=framework.zip'                                    
                return response
            else:
                messages.add_message(request,messages.ERROR, "File not found")
                return redirect(request.META.get('HTTP_REFERER'))
    except ProtectedError:
        messages.add_message(request,messages.ERROR, "No permision")

    except Exception as e:
        messages.add_message(request,messages.ERROR, e)
    return redirect(request.META.get('HTTP_REFERER'))


def NormPartDownloadView(request, uuid):
    '''Function will donload requested part after GUID'''
    inspection = {'active': False} if 'Authorization' not in request.headers else keycloak_manager.introspect(request.headers['Authorization'].replace("Bearer ", ""))
    if inspection['active']:
        try:   
            if request.method == 'GET':
                queries = [NormParts_Shared_Component.objects.filter(UUID = uuid)]     
                    
                requsted_object = [ query for query in queries if query][0].first()
                
                if requsted_object:
                    new_path = os.path.join(MEDIA_ROOT, requsted_object.file_catia_part.name.replace("\\", "/").strip("/"))
                    requsted_object.file_catia_part.name = new_path
                    # requsted_object.save()
                    file_to_export = requsted_object.file_catia_part                    
                if file_to_export:
                    response = HttpResponse(file_to_export.file)
                    response['Content-Disposition'] = 'attachement; filename=catia_part.CATPart' #os.path.basename(new_file.name.replace("\\", "/"))
                    return response
                else:
                    messages.add_message(request,messages.ERROR, "File not found")
                    return redirect(request.META.get('HTTP_REFERER'))
        except ProtectedError:
            messages.add_message(request,messages.ERROR, "No permision")

        except Exception as e:
            messages.add_message(request,messages.ERROR, e)

        return redirect(request.META.get('HTTP_REFERER'))   
    else:
        return redirect("home")
      



def get_csrf_token(request):
    inspection = {'active': False} if 'Authorization' not in request.headers else keycloak_manager.introspect(request.headers['Authorization'].replace("Bearer ", ""))
    if inspection['active']:
        context = {}
        return TemplateResponse(request, "NormMan//get_csrf_token.html", context)
    else:
        return redirect("home")


def NormPartDownloadSpecificMeta(request, uuid):
    '''Function will download requested specific part after GUID'''
    inspection = {'active': False} if 'Authorization' not in request.headers else keycloak_manager.introspect(request.headers['Authorization'].replace("Bearer ", ""))
    if inspection['active']:
        try:     
            if request.method == 'GET': 
                queries = [NormParts_Shared_Component.objects.filter(UUID = uuid)]     
                requsted_object = [ query for query in queries if query][0].first()
                file_name = "workflow" if "workflow" in request.META["PATH_INFO"] else "meta" if "meta" in request.META["PATH_INFO"] else None
                # path = f'{MEDIA_ROOT}/{requsted_object.data_path}/{file_name}.json'.replace("\\","/")
                path = requsted_object.file_workflow_json.path
                file_to_export = open(path, "rb") if path is not None and (valid(uuid) and file_name) else None
                if file_to_export:        
                    response = HttpResponse(file_to_export)
                    response['Content-Disposition'] = 'attachement; filename='+ path.split("/")[-1]
                    return response
                else:
                    messages.add_message(request,messages.ERROR, "File not found")
                    return redirect(request.META.get('HTTP_REFERER'))
        except ProtectedError:
            messages.add_message(request,messages.ERROR, "No permision")

        except Exception as e:
            messages.add_message(request,messages.ERROR, e)
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect("home")    


def NormPartDownloadSpecificView(request, uuid):
    '''Function will download requested specific part after GUID'''
    inspection = {'active': False} if 'Authorization' not in request.headers else keycloak_manager.introspect(request.headers['Authorization'].replace("Bearer ", ""))
    if inspection['active']:    
        try:     
            if request.method == 'GET': 
                path = f'{MEDIA_ROOT}/norm_parts/static_files/meta.json'.replace("\\","/")
                if valid(uuid):                      
                    with open(path, "r") as meta:
                        resources = json.load(meta)
                    path = [value for key, value in zip(resources.keys(), resources.values()) if key == uuid][0]                
                else:
                    pass
                file_to_export = open(path, "rb") if path is not None else None
                if file_to_export:        
                    response = HttpResponse(file_to_export)
                    response['Content-Disposition'] = 'attachement; filename='+ path.split("/")[-1]
                    return response
                else:
                    messages.add_message(request,messages.ERROR, "File not found")
                    return redirect(request.META.get('HTTP_REFERER'))
        except ProtectedError:
            messages.add_message(request,messages.ERROR, "No permision")

        except Exception as e:
            messages.add_message(request,messages.ERROR, e)
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect("home")   

def flatten_json(o):
    o_list = []
    for key in o:
        o_list.append(o[key])
    return o_list


def RemoveObject(request) -> JsonResponse:
    """
    This function does remove object in given request from workflow session.
    After removement is next consequent action executed and thus, the request
    is communicated further and send over to a framework, that will remove it 
    from its session as well.
    :request: ASGI Request
    :return: JsonResponse
    """
    object_uuid = None if not 'object_uid' in request.POST else request.POST['object_uid'] 
    user = request.user.username if type(request) is not dict else request["user"]
    user = user if not (not len(user) and 'user' in request.POST) else request.POST["user"]
    projectuser = ProjectUser.objects.filter(user__username = user).get()
    session_object = projectuser.current_workflow_session    
    session_object.created_objects[object_uuid]["properties"]["Active"]["value"] = False
    session_object.update_status(session_object.created_objects[object_uuid])
    return load_workflow_details(request)


def MethodSendToFramework(request):
    '''
    View used to reload dropdown list during addition of idemat material process
    '''
    command  = request.POST['command']
    trigger_id = None if not 'trigger_id' in request.POST else request.POST['trigger_id'] 
    session_uuid = None if not 'session_id' in request.POST else request.POST['session_id'] 
    master_uuid = None if not 'master_id' in request.POST else request.POST['master_id'] 
    session_type = None if not 'session_type' in request.POST else request.POST['session_type'] 
    method_uuid = None if not 'method_id' in request.POST else request.POST['method_id'] 
    object_uuid = None if not 'object_uid' in request.POST else request.POST['object_uid']
    shared_component_uuid = None if not 'shared_component_uuid' in request.POST else request.POST['shared_component_uuid'] 
    shared_component_type = None if not 'shared_component_type' in request.POST else request.POST['shared_component_type'] 
    parameters = None if not 'parameters' in request.POST else request.POST['parameters'] 
    config = None if not 'config' in request.POST else request.POST['config'] 
    channel_layer = get_channel_layer()
    channel_name = 'chat_' + request.user.username
    async_obj = async_to_sync(channel_layer.group_send)(channel_name,{
        'type': 'framework_command',
        'message': json.dumps({
            'user': request.user.username, 
            'command': command,
            'trigger_uuid': trigger_id,
            'method_uuid': method_uuid,
            'session_uuid': session_uuid,
            'workflow_uuid': master_uuid,
            'session_type': session_type,
            'object_uuid': object_uuid,            
            'shared_component_uuid' : shared_component_uuid,
            'shared_component_type' : shared_component_type,
            'parameters': parameters,
            'config': config
        })
    })    
    return JsonResponse(dict())


def load_framework_status(request):
    '''
    View used to reload dropdown list during addition of idemat material process
    '''
    trigger_id = request.POST['trigger_id']
    context, data = dict(), dict()
    #jstree object was clicked
    if trigger_id == 'framework_status_update_available':
        active_user = request.user
        context ={}
        context['user'] = active_user

        data['html_framework_details'] = render_to_string('website/current_framework_session.html', context, request=request)
    return JsonResponse(data)

def dynamic_breadcrumb(category_group_object) ->str:
        dynamic_breadcrumb ='<nav aria-label="breadcrumb">'
        dynamic_breadcrumb+= '<ol class="breadcrumb">'

        li_array = []
        parent_category_group_object = category_group_object
        i = 1
        while i>0:


            path = reverse('NormMan:load_content')
            li_elem ='<li class="breadcrumb-item"><a class="category_group" + id="current_category"'  + 'value=' + str(parent_category_group_object.UUID) + ' data-url =' + path + ' style="cursor:pointer; color:blue;"' + '>' 
            li_elem+= str(parent_category_group_object.name) + '</a></li>'
            li_array.append(li_elem)
            parent_category_group_object = parent_category_group_object.parent_group
            if parent_category_group_object == None:
                break
        for elem in reversed(li_array):
            dynamic_breadcrumb+= elem
        

        dynamic_breadcrumb+= '</ol>'
        dynamic_breadcrumb+= '</nav>'
        return dynamic_breadcrumb
