# Create your views here.
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

def instance_download_file_internal(request, uuid_instance):  
    try:  
        if request.method == 'GET' and uuid_instance:
            instance = Workflow_Object.objects.filter(UUID = uuid_instance).get()
            if instance.catia_representation:
                # with open(os.path.join(BASE_DIR, instance.catia_representation.url), "rb") as file:
                with open(f"{BASE_DIR}/{instance.catia_representation.url}", "rb") as file:                    
                    response = HttpResponse(file)
                    response['Content-Disposition'] = 'attachement; filename='+ instance.catia_representation.url
                    response.status_code = 200
                    return response
            else:
                messages.add_message(request,messages.ERROR, "Specified instance has no file")
                return redirect(request.META.get('HTTP_REFERER'))
    except ProtectedError:
        messages.add_message(request,messages.ERROR, "No permision")
    except Exception as e:
        messages.add_message(request,messages.ERROR, e)
    return redirect(request.META.get('HTTP_REFERER'))   


def get_main_object(request = None, uuid_instance = None):
    object = get_object_or_404(Workflow_Object, UUID = str(uuid_instance))
    reference_instance = object.reference_instance
    workflow_session = reference_instance.workflow_session
    stage = Workflow_Stage.objects.filter(parent_workflow = workflow_session.workflow_model, name = "CATPart").get()
    parent_reference_object = Workflow_Object.objects.filter(parent_stage = stage).get()
    parent_object_instance = parent_reference_object.instances.filter(workflow_session = workflow_session, is_active = True).get()
    # -> We have finally parent object active instance, we can check for catia_representation
    return parent_object_instance

def instance_download_file(request, uuid_instance):
    inspection = {'active': False} if 'Authorization' not in request.headers else keycloak_manager.introspect(request.headers['Authorization'].replace("Bearer ", ""))
    data = dict()
    if inspection['active']:        
        if request.method == 'GET' and uuid_instance:
            instance = Workflow_Object.objects.filter(UUID = uuid_instance).get()
            target_instance = instance if instance.type != 'REFERENCE' else get_main_object(None, str(instance.UUID))
            if target_instance.catia_representation:
                # with open(os.path.join(BASE_DIR, instance.catia_representation.url), "rb") as file:
                with open(f"{BASE_DIR}/{target_instance.catia_representation.url}", "rb") as file:                    
                    response = HttpResponse(file)
                    response['Content-Disposition'] = 'attachement; filename='+ target_instance.catia_representation.url
                    response['Instance_UUID'] = None if instance.reference_instance is None else str(instance.reference_instance.UUID)
                    response.status_code = 200                    
                    return response
    else:
        data["status"] = 403
        data["error"] = 'You do not have permission to access this resource.'
    return JsonResponse(data)


def instance_upload_file(request):
    inspection = {'active': False} if 'Authorization' not in request.headers else keycloak_manager.introspect(request.headers['Authorization'].replace("Bearer ", ""))
    data = dict()
    if inspection['active']:        
        if request.method == 'POST' and request.FILES.get('object_instance_catia_representation'):
            myfile = request.FILES['object_instance_catia_representation']
            if request.POST.get('object_instance_uuid'):
                target_instance = Workflow_Object.objects.filter(UUID = request.POST.get('object_instance_uuid'))
                if target_instance:
                        target_instance = target_instance.get()
                        # Assignment of a custom field in ordeer to save file on a correct position - has to be deleted!!
                        target_instance.username = request.POST.get('user', 'unknown_user')
                        target_instance.catia_representation = myfile
                        target_instance.save()
            data["message"] = 'File uploaded successfully!'
            data["status"] = 200
            data["uploaded_file_url"] = target_instance.catia_representation.url
    else:
        data["status"] = 403
        data["error"] = 'You do not have permission to access this resource.'
    return JsonResponse(data)
 
def custom_file_upload(request):
    inspection = {'active': False} if 'Authorization' not in request.headers else keycloak_manager.introspect(request.headers['Authorization'].replace("Bearer ", ""))
    data = dict()
    if inspection['active']:
        if request.POST.get('session_uuid'):
            if request.method == 'POST' and len(request.FILES) > 0:
                # Here we run through all the files
                if request.POST.get('instance_uuid'):
                    try:
                        instance = Workflow_Object.objects.filter(UUID = request.POST.get('instance_uuid')).get()                        
                        for received_file in request.FILES.values():
                            instance.thumbnail = received_file
                            instance.save()
                        # here custom stuff
                        data["message"] = 'Files uploaded successfully!'
                        data["status"] = 200
                    except:
                        data["status"] = 404
                        data["error"] = 'Error occured in upload procedure. Check you rights!'
                else:
                    try:
                        counter = 0
                        for received_file in request.FILES.values():
                            counter += 1
                            static_save(received_file, f'Picture_Page_{counter}.png', request.POST.get('session_uuid'))
                        data["message"] = 'Files uploaded successfully!'
                        data["status"] = 200
                    except:
                        data["status"] = 404
                        data["error"] = 'Error occured in upload procedure. Check you rights!'
        else:
            data["status"] = 403
            data["error"] = 'Prohibited because of missing information (UUID session)!'
    else:
        data["status"] = 403
        data["error"] = 'You do not have permission to access this resource.'
    return JsonResponse(data)


def static_save(uploaded_file, file_name, session_uuid):
    session = Workflow_Session.objects.filter(UUID = session_uuid).first()
    # -> Static Upload To

    sessions_dir = os.path.join(MEDIA_ROOT, "workflow_sessions")
    user_dir = os.path.join(sessions_dir, f"User_{str(session.owner.UUID)}")
    user_session_dir = os.path.join(user_dir, f"Session_{str(session.UUID)}")
    reports_dir = os.path.join(user_session_dir, "reports")
    None if os.path.exists(sessions_dir) else os.mkdir(sessions_dir)
    None if os.path.exists(user_dir) else os.mkdir(user_dir)
    None if os.path.exists(user_session_dir) else os.mkdir(user_session_dir)
    None if os.path.exists(reports_dir) else os.mkdir(reports_dir)
    file_path = os.path.join(reports_dir, file_name)
    with open(file_path, 'wb') as file:
        for chunk in uploaded_file.chunks():
            file.write(chunk)
    return file_path


def framework_download_modal(request):
    form = Framework()        

    data = dict()
    if request.method == 'POST':
        # here probably ajax request??
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


def NormPartDownloadView(request, uuid):
    '''Function will donload requested part after GUID'''
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


def get_csrf_token(request):
   context = {}
   return TemplateResponse(request, "NormMan//get_csrf_token.html", context)

def NormPartDownloadSpecificMeta(request, uuid):
    '''Function will download requested specific part after GUID'''
    try:     
        if request.method == 'GET': 
            queries = [NormParts_Shared_Component.objects.filter(UUID = uuid)]     
            requsted_object = [ query for query in queries if query][0].first()
            file_name = "workflow" if "workflow" in request.META["PATH_INFO"] else "meta" if "meta" in request.META["PATH_INFO"] else None
            path = f'{MEDIA_ROOT}/{requsted_object.data_path}/{file_name}.json'.replace("\\","/")
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


def NormPartDownloadSpecificView(request, uuid):
    '''Function will download requested specific part after GUID'''
    try:     
        if request.method == 'GET': 
            path = f'{MEDIA_ROOT}/norm_parts/static_files/meta.json'.replace("\\","/")
            if valid(uuid):       
                # We will go through database, but for now i do it the simple way, 
                # just by downloading a file directly                
                with open(path, "r") as meta:
                    resources = json.load(meta)
                    pass
                path = [value for key, value in zip(resources.keys(), resources.values()) if key == uuid][0]                
            else:
                # We give only one oportunity and that is download procedure of a 
                # meta.json file (at least for now)
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


def flatten_json(o):
    o_list = []
    for key in o:
        o_list.append(o[key])
    return o_list


def AssignObject(request) -> None:
    """
    This function assigns an id of selected and clicked object from
    database represented in a modal window.
    :request: ASGI Request
    :return: NoneType
    """
    object_uuid = None if not 'object_uid' in request.POST else request.POST['object_uid'] 
    user = request.user.username if type(request) is not dict else request["user"]
    user = user if not (not len(user) and 'user' in request.POST) else request.POST["user"]

    projectuser = ProjectUser.objects.filter(user__username = user).get()
    session_object = projectuser.current_workflow_session    

    # question: where to store objects for future? Some collector?
    # because it does not make sense to overwrite meta all the time...

    if session_object:
        if session_object.workflow_status:
            reduced_objects = dict()
            # if it exist, then use it, otherwise, use meta file
            for obj in session_object.workflow_status.values():
                if "objects" in obj:
                    for sub_obj in obj["objects"].values():
                        if sub_obj["uid"] != object_uuid:
                            # remove it by adding the one different from that one sought
                            pass
        session_object.save()
    return JsonResponse(request)


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

    # question: where to store objects for future? Some collector?
    # because it does not make sense to overwrite meta all the time...    
    session_object.created_objects[object_uuid]["properties"]["Active"]["value"] = False
    session_object.update_status(session_object.created_objects[object_uuid])
    # if session_object:
    #     if session_object.workflow_status:
    #         reduced_objects = dict()
    #         # if it exist, then use it, otherwise, use meta file
    #         for obj in session_object.workflow_status.values():
    #             if "objects" in obj:
    #                 reduced_objects = dict()
    #                 for sub_obj in obj["objects"].values():
    #                     if sub_obj["uid"] != object_uuid:
    #                         # remove it by adding the one different from that one sought
    #                         reduced_objects.update({str(len(reduced_objects) + 1):sub_obj})
    #                 obj.update({"objects":reduced_objects})
    #     session_object.save()    
    return load_workflow_details(request)



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


            path = reverse('CatiaFramework:load_content')
            li_elem ='<li class="breadcrumb-item"><a class="category_group" + id="current_category"'  + 'value=' + str(parent_category_group_object.UUID) + ' data-url =' + path + ' style="cursor:pointer; color:blue;"' + '>' 
            li_elem+= str(parent_category_group_object.name) + '</a></li>'
            li_array.append(li_elem)
            parent_category_group_object = parent_category_group_object.parent_folder
            if parent_category_group_object == None:
                break
        for elem in reversed(li_array):
            dynamic_breadcrumb+= elem
        

        dynamic_breadcrumb+= '</ol>'
        dynamic_breadcrumb+= '</nav>'
        return dynamic_breadcrumb
