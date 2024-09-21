from NormMan.models import NormParts_Shared_Component, Workflow_Session, ProjectUser_NormMan_Ref
from .views import *
from django.views.generic import  TemplateView
import json, os
from django.shortcuts import  get_object_or_404
from django.views.generic import TemplateView
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, JsonResponse   
from website.models import ProjectUser
from channels.layers import get_channel_layer
from NormMan.models import Component_Group_Level
from NormMan.scripts.meta_replication import valid
from website import settings
from website.settings import MEDIA_ROOT

def flatten_json(o):
    o_list = []
    for key in o:
        o_list.append(o[key])
    return o_list


class shared_component_workflow_session(TemplateView):

    template_name = 'NormMan/normparts/shared_component_workflow_dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/user/login')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        target_object_uuid = kwargs.get('uuid', None)
        owner = ProjectUser_NormMan_Ref.objects.filter(nickname = self.request.user.username).get()

        session_object = Workflow_Session.objects.filter(UUID = target_object_uuid).first()
        workflow_object = session_object.workflow_object 

        # -> Here ight be a general change in terms of Workflow session to be Workflow instance, 
        #   as this is a new workflow session object

        self.request.user.projectuser.current_workflow_session = session_object
        self.request.user.projectuser.save()
        #send request to framework and check if continuation is possible
        channel_layer = get_channel_layer()
        message =                 {
            'type': 'framework_command',
            'message': json.dumps({
                'user': self.request.user.username,
                'command': 'get_or_create_session',
                'session_uuid': str(session_object.UUID),               
                'parameters': None
            })
        }
        # -> we do not send a message for now, rethink an approach
        # async_to_sync(channel_layer.group_send)('chat_'+ self.request.user.username, message)

        # Temporary debugging 
        category_group_object = Component_Group_Level.objects.filter(group_depth_level = 0).first()
        p = os.path.join(category_group_object.data_path.path, "meta_threejs.json" ).replace("\\", "/")
        try:
            with open(p,"r") as f:
                content = json.load(f)
        except:
            pass        

        context = super(shared_component_workflow_session, self).get_context_data(**kwargs)
        context['stl_file_list'] = json.dumps(content)
        context['target_object_uuid'] = str(target_object_uuid)
        context['current_session_id'] = str(session_object.UUID)
        context['master_id'] = str(workflow_object.UUID)
        context['current_session'] = session_object
        context['current_workflow'] = str(workflow_object)

        # -> this operation is to be replaced by information from json field
        # but based on a given information from the field, it is either to be
        # created or replaced
        if session_object.workflow_status:
            # if it exist, then use it, otherwise, use meta file
            pass
        else:
            # if does not exist, we use meta json but save it directly to status as well
            p = os.path.join(settings.BASE_DIR, workflow_object.file_workflow_json.url.strip("/")).replace("\\", "/")      
            try:
                with open(p,"r") as f:
                    session_object.workflow_status = json.load(f)
            except:
                session_object.workflow_status = None
            session_object.save()
        
        o_array = flatten_json(session_object.workflow_status)
        for object in o_array:
            if 'methods' in object: 
                if object['methods']:
                    for method in object['methods'].items():
                        search_object = [ele for ele in o_array if ele['id'] == method[1]][0]
                        search_object['parent'] = object['id']

        for object in o_array:
            object['text'] =object['gui']['text']
        res = [ele for ele in o_array if 'text' in ele and not (ele["gui"]["type"] == "object" or ele["gui"]["type"] == "method")] #remove items not to be displayed for user

        o_array = res
        for obj in o_array:
            obj.update({"workflow_uuid":str(workflow_object.UUID) })  

            if obj['gui']['type']== "step":
                obj['icon']= '/media/norm_parts/icons/step.png'

            if obj['gui']['type']== "process":
                obj['icon']= '/media/norm_parts/icons/process.png'

            if obj['gui']['type']== "workflow":
                obj['icon']= '/media/norm_parts/icons/workflow.png'

            if obj['gui']['type']== "method":
                obj['icon']= '/media/norm_parts/icons/method.png'

            if obj['icon']== None:
                # totally obsolete
                obj['icon']= None
        
        context['json_tree'] = json.dumps(o_array)         
        return context     


def load_workflow_details(request):
    '''View used to reload dropdown list during addition of idemat material process
    '''
    trigger_id = request.POST['trigger_id']
    command = request.POST['command']
    context, data = dict(), dict()
    worklfow_uuid = request.POST['master_id']
    session_uuid = request.POST['session_id']    
    user = request.user.username
    user = user if not (not len(user) and 'user' in request.POST) else request.POST["user"]
    context['step_id'] = trigger_id
    if user is None or not len(user):
        return

    projectuser = ProjectUser_NormMan_Ref.objects.filter(nickname = user).get()
    session_object = projectuser.reference_projectuser.current_workflow_session
    worklfow_object = get_object_or_404(NormParts_Shared_Component, UUID=worklfow_uuid) 

    # function was called directly
    if command == 'workflow_dashboard_status_update_request':
        # question: where to store objects for future? Some collector?
        # because it does not make sense to overwrite meta all the time...

        if session_object:
            if session_object.workflow_status:
                # if it exist, then use it, otherwise, use meta file
                pass
            else:
                # if does not exist, we use meta json but save it directly to status as well
                p = os.path.join(settings.BASE_DIR, worklfow_object.file_workflow_json.url.strip("/"))        
                try:
                    with open(p,"r") as f:
                        session_object.workflow_status = json.load(f)
                except:
                    session_object.workflow_status = None
                session_object.save()

            o_array = flatten_json(session_object.workflow_status)    
            object_dict = next((item for item in o_array if item["id"] == trigger_id), None)
            expanded_object_dict = object_dict.copy()                     
            
        else:
            data['workflow_json'] = None
    # fnction was called directly
    if command == 'workflow_dashboard_action':
        pass



    #jstree object was clicked
    if command == 'jstree_select' or 'modify_process_action':
        if worklfow_object:
            # p = os.path.join(settings.BASE_DIR, worklfow_object.file_workflow_json.url.strip("/"))
            # f = open(p, "r")    
            # content = json.load(f)
            # o_array = flatten_json(content)
            # #add workflow uuid to every object 
            # object_dict = next((item for item in o_array if item["id"] == trigger_id), None)
            # expanded_object_dict = object_dict.copy()  
            if session_object.workflow_status:
                # if it exist, then use it, otherwise, use meta file
                pass
            else:
                # if does not exist, we use meta json but save it directly to status as well
                p = os.path.join(settings.BASE_DIR, worklfow_object.file_workflow_json.url.strip("/"))        
                try:
                    with open(p,"r") as f:
                        session_object.workflow_status = json.load(f)
                except:
                    session_object.workflow_status = None
                session_object.save()

            o_array = flatten_json(session_object.workflow_status)    
            object_dict = next((item for item in o_array if item["id"] == trigger_id), None)
            expanded_object_dict = object_dict.copy()         
        else:
            data['workflow_json'] = None

    # load static meta
    meta = json.load(open(f'{MEDIA_ROOT}/norm_parts/static_files/meta.json'.replace("\\", "/"), "r"))
    if "objects" in object_dict:
        for key, value in object_dict['objects'].items():
            if type(expanded_object_dict['objects'][key]) is not dict:
                expanded_object_dict['objects'][key] =  next((item for item in o_array if item["id"] == value), None)
            cur_item = expanded_object_dict['objects'][key]

            if cur_item["object"]:
                if "uuid" in cur_item["object"]:
                    queries = [NormParts_Shared_Component.objects.filter(UUID = cur_item["object"]["uuid"])]     
                    requsted_object = [ query for query in queries if query][0].first()
                    new_path = requsted_object.thumbnail.path
                elif "config" in cur_item["object"]:
                    cur_item["object"]["config"] = json.dumps(cur_item["object"]["config"])
                    new_path = cur_item["gui"]["icon"] if not valid(cur_item["gui"]["icon"]) else meta[cur_item["gui"]["icon"]]    
            else:
                new_path = cur_item["gui"]["icon"] if not valid(cur_item["gui"]["icon"]) else meta[cur_item["gui"]["icon"]]
                        
            new_path = os.path.relpath(new_path).replace("\\", "/") if new_path else None
            cur_item["gui"]["icon"] = None if new_path is None else f'/{new_path}'
            for key2, value2 in cur_item['methods'].items():
                cur_item['methods'][key2]= next((item for item in o_array if item["id"] == value2), None)
                cur_item2 = cur_item['methods'][key2]
                new_path = cur_item2["gui"]["icon"] if not valid(cur_item2["gui"]["icon"]) else meta[cur_item2["gui"]["icon"]]
                new_path = os.path.relpath(new_path).replace("\\", "/") if new_path else None
                cur_item2["gui"]["icon"] = None if new_path is None else f'/{new_path}'
    if "methods" in object_dict:
        for key, value in object_dict['methods'].items():                        
            expanded_object_dict['methods'][key]  =  next((item for item in o_array if item["id"] == value), None)   
            cur_item = expanded_object_dict['methods'][key]
            new_path = cur_item["gui"]["icon"] if not valid(cur_item["gui"]["icon"]) else meta[cur_item["gui"]["icon"]]
            new_path = os.path.relpath(new_path).replace("\\", "/") if new_path else None
            cur_item["gui"]["icon"] = None if new_path is None else f'/{new_path}'            
    new_path = object_dict["gui"]["gif"] if not valid(object_dict["gui"]["gif"]) else meta[object_dict["gui"]["gif"]]
    new_path = os.path.relpath(new_path).replace("\\", "/") if new_path else None
    object_dict["gui"]["gif"] = None if new_path is None else f'/{new_path}'


    reference = request.META['HTTP_REFERER'].replace(request.META['HTTP_ORIGIN'], "")
    if reference == '/shared_components/database/dashboard/':
        return JsonResponse(dict(data))

    # Temporary debugging 
    category_group_object = Component_Group_Level.objects.filter(group_depth_level = 0).first()
    p = os.path.join(category_group_object.data_path.path, "meta_threejs.json" ).replace("\\", "/")
    try:
        with open(p,"r") as f:
            content = json.load(f)
    except:
        pass
    context['stl_file_list'] = json.dumps(content)

    # Render information    
    data['workflow_json'] = expanded_object_dict
    context['object_details'] = expanded_object_dict
    context['object_details_ser'] = JsonResponse(expanded_object_dict)    
    context['master_id'] = worklfow_uuid
    data['html_workflow_details'] = render_to_string('NormMan/normparts/workflow_details.html', context, request=request)
    data['html_object_actions'] = render_to_string('NormMan/normparts/workflow_object_actions.html', context, request=request)
    data['html_object_details'] = render_to_string('NormMan/normparts/workflow_object_details.html', context, request=request)


    category_id = "96540593-2cc7-460b-b453-6438078313a4"
    current_category_group = Component_Group_Level.objects.filter(UUID = category_id).get()
    context['parts'] = current_category_group.normparts_shared_components.filter(type="Part")
    data['html_list_norm_parts'] =render_to_string('NormMan/normparts/list_shared_components/shared_component_parts.html', context, request=request)
    data['norm_parts_hits'] = len(context['parts'] )
    return JsonResponse(data)
