import json, os
import pandas as pd
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django  import apps
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.html import format_html
from NormMan.models import NormParts_Shared_Component, ProjectUser_NormMan_Ref
from NormMan.models import Component_Group_Level
from website.settings import BASE_DIR, MEDIA_ROOT
from website.models import ProjectUser



def norm_part_quick_position(request):
    ''' Powercopy model positioning is called from here. '''

    context = dict()
    trigger_id = None if not 'trigger_id' in request.POST else request.POST['trigger_id'] 
    session_uuid = None if not 'session_id' in request.POST else request.POST['session_id'] 
    master_uuid = None if not 'master_id' in request.POST else request.POST['master_id'] 
    session_type = None if not 'session_type' in request.POST else request.POST['session_type'] 
    method_uuid = None if not 'method_id' in request.POST else request.POST['method_id'] 
    shared_component_uuid = None if not 'shared_component_uuid' in request.POST else request.POST['shared_component_uuid'] 
    shared_component_type = None if not 'shared_component_type' in request.POST else request.POST['shared_component_type'] 
    parameters = None if not 'parameters' in request.POST else request.POST['parameters'] 
    config = None if not 'config' in request.POST else request.POST['config'] 
    user = request.user.username
    user = user if not (not len(user) and 'user' in request.POST) else request.POST["user"]
    context['step_id'] = trigger_id
    if user is None or not len(user):
        return

    projectuser = ProjectUser_NormMan_Ref.objects.filter(nickname = user).get()
    session_object = projectuser.reference_projectuser.current_workflow_session
    if len(session_object.created_objects) > 1 and "last_object" in session_object.created_objects: 
        obj = session_object.created_objects["last_object"]
        if "Active" in obj["properties"]:
            obj["properties"]["Active"]["value"] = False
            channel_layer = get_channel_layer()
            channel_name = 'chat_' + request.user.username
            async_obj = async_to_sync(channel_layer.group_send)(channel_name,{
                'type': 'framework_command',
                'message': json.dumps({
                    'user': request.user.username, 
                    'command': "object_utilisation",
                    'trigger_uuid': trigger_id,
                    'method_uuid': method_uuid,
                    'session_uuid': session_uuid,
                    'workflow_uuid': master_uuid,
                    'session_type': session_type,
                    'object_uuid': obj["uid"],            
                    'shared_component_uuid' : shared_component_uuid,
                    'shared_component_type' : shared_component_type,
                    'parameters': parameters,
                    'config': config
                })
            })                        
        obj["properties"].update({"Active":{"value":False}})
        session_object.update_status(obj)
    session_object.save()
    return JsonResponse(dict())



def norm_part_select_modal_config(request):
    '''Part will be checked for configuration file if not exists send only UUID
    '''
    uuid = request.POST["object_uid"]                   
    query_component = NormParts_Shared_Component.objects.filter(UUID = uuid)
    if query_component:
        normpart = get_object_or_404(NormParts_Shared_Component, pk=uuid )
    from NormMan.forms import NormPartSelectConfigurationForm
    form = NormPartSelectConfigurationForm(instance = normpart)    
    return lca_part_from_template_save_form(request, form, 'modal/normpart/norm_part_select_configuration_modal.html')


def norm_part_select_modal(request, id, uid, wid):
    '''Part will be checked for configuration file if not exists send only UUID
    '''        
    # category_id = "96540593-2cc7-460b-b453-6438078313a4"
    norm_part_obj = NormParts_Shared_Component.objects.filter(UUID = wid).first()
    group_level = Component_Group_Level.objects.filter(UUID = norm_part_obj.data_path.split("/")[-3][-36:])

    norm_parts = group_level.get().normparts_shared_components.all()
    ids = {"id": id, "uid": uid, "wid": wid}
    from NormMan.forms import NormPartSelectConfigurationCollector
    form = NormPartSelectConfigurationCollector(request.user.projectuser.current_project_id, norm_parts = norm_parts, ids = ids)
    return norm_part_from_template_save_form(request, form, 'modal/normpart/norm_part_modal.html')


def norm_part_send_to_cad(request, uuid):
    '''Part will be checked for configuration file if not exists send only UUID
    '''                  
    query_component = NormParts_Shared_Component.objects.filter(UUID = uuid)
    if query_component:
        normpart = get_object_or_404(NormParts_Shared_Component, pk=uuid )
    from NormMan.forms import NormPartSelectConfigurationForm
    form = NormPartSelectConfigurationForm(instance=normpart)        
    return lca_part_from_template_save_form(request, form, 'modal/normpart/norm_part_select_configuration_modal.html')


def norm_part_from_template_save_form(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        data['form_is_valid'] = True
    context = {'form': form}

    from NormMan.forms import Configuration
    # category_id = "96540593-2cc7-460b-b453-6438078313a4"
    # norm_parts = Component_Group_Level.objects.filter(UUID = category_id).get().normparts_shared_components.filter(type="PART")
    context['norm_parts_collector'] = form.norm_parts_collector #[Configuration(meta = obj) for obj in norm_parts]
    norm_part_obj = NormParts_Shared_Component.objects.filter(UUID = form.worklfow_uuid_property).first()
    category_group_object = Component_Group_Level.objects.filter(UUID = norm_part_obj.data_path.split("/")[-3][-36:]).first() # "96540593-2cc7-460b-b453-6438078313a4").first()
    context['category_group'] = category_group_object   
    query = Component_Group_Level.objects.filter(parent_group__UUID = category_group_object.UUID)
    context['category_groups'] = query
    from . import dynamic_breadcrumb_normparts_modal
    context['html_dynamic_breadcrumb'] = format_html(dynamic_breadcrumb_normparts_modal(category_group_object))
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)

#lcastep_save_form-----------------------------------------------------------------------------------
def lca_part_from_template_save_form(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        data['form_is_valid'] = True
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request),
    return JsonResponse(data)

def load_configurations(request):
    '''View used to reload dropdown list during addition of idemat material process
    '''

    trigger_id = request.GET['trigger_id']
    shared_component_uuid  = request.GET['norm_part_uuid']
    shared_component_type= request.GET['shared_component_type']
    shared_model = apps.apps.get_model('NormMan', shared_component_type).objects.filter(UUID = shared_component_uuid ).get()
    context={}
    if trigger_id == 'send_to_framework' and shared_model:
        channel_layer = get_channel_layer()
        retval = async_to_sync(channel_layer.group_send)(
        'chat_' + request.user.username,
        {
            'type': 'framework_command',
            'message': json.dumps({
                'user': request.user.username,
                'shared_component_uuid': shared_component_uuid,
                'shared_component_type' : shared_component_type,
                'parameters':request.GET['parameters'],
                'file_name': "catia_part.CATPart",
                'file_data': "decoded"
        }
            )
        }
    )

   #template part search  (ul -> li option) was selected
    if trigger_id == 'get_configurations':

       '''Import Function for LCA Database. will import
                Step.1 Read imported file and generate list od dictionarys with processes
                Step.2 Generate process with foreign key of self
        '''
    configurations = []      
    if   shared_component_type == 'NormParts_Shared_Component':
        pass
    if   shared_component_type == 'NormParts_Shared_Component':
        
        path_excel_file = shared_model.file_configuration
    
        # Open first sheet of xlsx file, where the configuration is
        df = pd.read_excel(os.path.join(BASE_DIR, path_excel_file.url.strip("/")), sheet_name=0, header=0, na_filter=True)

        #Step.1 Search for processes
        
        for x in df.index:
            dict_temp = df.iloc[x].to_dict()
            configurations.append ( {'id': x, 'parameters': json.dumps(dict_temp) } )

    context['configuration_list']=configurations
    data={}

    data['html_configuration_list'] =render_to_string('modal/normpart/configuration_dropdown_list_options.html', context, request=request)

    return JsonResponse(data)


def propagate(request, id, uid, wid) -> JsonResponse:
    # so this propagate function should modify information related to selected object and then a 
    # load function should be called to update a view, maybe that is to be done from within java?
    pass
    trigger_id = id
    object_uuid = uid
    master_uuid = wid
    session_uuid = None if not 'session_id' in request.POST else request.POST['session_id']    
    session_type = None if not 'session_type' in request.POST else request.POST['session_type'] 
    method_uuid = None if not 'method_id' in request.POST else request.POST['method_id']
    shared_component_type = None if not 'shared_component_type' in request.POST else request.POST['shared_component_type'] 
    user = request.user.username if type(request) is not dict else request["user"]
    user = user if not (not len(user) and 'user' in request.POST) else request.POST["user"]
    uuid = None if not "norm_part_uuid" in request.GET else request.GET["norm_part_uuid"]
    config = None if not "config" in request.GET else request.GET["config"]

    projectuser = ProjectUser.objects.filter(user__username = user).get()
    session_object = projectuser.current_workflow_session    

    # question: where to store objects for future? Some collector?
    # because it does not make sense to overwrite meta all the time...

    if session_object:
        if session_object.workflow_status:
            # if it exist, then use it, otherwise, use meta file
            for obj in session_object.workflow_status.values():
                if "objects" in obj:
                    for sub_obj in obj["objects"].values():
                        if sub_obj["uid"] == object_uuid:
                            # remove it by adding the one different from that one sought
                            sub_obj["object"] = {"uuid": uuid, "config": config}
                            # we have to find picture as well
                            session_object.save()
                            pass


    channel_layer = get_channel_layer()
    channel_name = 'chat_' + request.user.username
    async_obj = async_to_sync(channel_layer.group_send)(channel_name,{
        'type': 'framework_command',
        'message': json.dumps({
            'user': user, 
            'command': "reload_data_after_selection",
            "source": "dotnet",
            'trigger_id': trigger_id,
            'method_id': method_uuid,
            'session_id': session_uuid,
            'workflow_id': master_uuid,
            'session_type': session_type,
            'object_id': object_uuid,            
            'shared_component_type' : shared_component_type,
            'parameters': None
        })
    })  

    # -> so here at the end
    return JsonResponse(dict())


def load_content_shared_component_norm_parts_modal(request):
    '''View used to reload content in the dashboard
    '''

    trigger_id = request.GET['trigger_id']


    context={}
    data={}
    root_group = None

    #Button search was pressed
    if trigger_id == 'search_submit':
        if request.method == 'GET' and 'object_name' in request.GET:
            object_name = request.GET['object_name'].strip()
            object_name =object_name[18:]
        else:
            object_name = None
             
        interactive_categories = {
            "TAILGATE": "512052b1-38df-4040-abdd-14edafc06b3e",
            "TUER": "421017fa-0519-41e3-bd32-9c57019a8e17"
        }
        category_id = interactive_categories[object_name]
        if object_name in interactive_categories.keys():
            current_category_group = Component_Group_Level.objects.filter(UUID =category_id).get()
        else:
            current_category_group = None


    #Category card was clicked
    if trigger_id == 'switch_category':
        category_id = request.GET['category_id']
        current_category_group = Component_Group_Level.objects.filter(UUID = category_id).get()

    query = Component_Group_Level.objects.filter(parent_group__UUID = category_id)          
    context_category_groups={}  
    context_category_groups['category_groups'] = query
    context_category_groups['category_group'] = current_category_group
    from NormMan.forms import Configuration
    norm_parts = current_category_group.normparts_shared_components.filter()
    context['norm_parts_collector'] = [Configuration(request.user.projectuser.current_project_id, meta = obj) for obj in norm_parts if (obj.project_model_id == request.user.projectuser.current_project_id or obj.type == "PART")]
    from . import dynamic_breadcrumb_normparts_modal
    context_category_groups['html_dynamic_breadcrumb'] = format_html(dynamic_breadcrumb_normparts_modal(current_category_group))
    data['html_category_groups'] =render_to_string('modal//normpart//cards_category_group_children.html', context_category_groups, request=request)
    data['html_norm_parts_collector'] =render_to_string('modal//normpart//norm_part_table_modal.html', context, request=request)


    if root_group:
        p = os.path.join(MEDIA_ROOT, root_group.data_path.name, "meta_threejs.json" )
        f = open(p, "r")    
        content = json.load(f)
        data['json_tree'] = content
    else:
        data['json_tree'] = None
    return JsonResponse(data)