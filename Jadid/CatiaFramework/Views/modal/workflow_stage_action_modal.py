from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.html import format_html
from django.db.models import Q
from CatiaFramework.models import Workflow_Action, Workflow_Object, Workflow, DotNet_ProjectFolder, DotNet_Component
import json, os
from website import settings
#qlca-----------------------------------------------------------------------------------
def workflow_stage_action_save_form(request, form, template_name):
    data = dict()
    context = dict()
    if request.method == 'POST':


        if form.is_valid():
            action = form.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    context.update({'form': form})
    category_group_object = DotNet_ProjectFolder.objects.filter(group_depth_level = 0).first()
    context['category_group'] = category_group_object  
    # query = DotNet_ProjectFolder.objects.filter(parent_folder__UUID = category_group_object.UUID)          
    query = DotNet_ProjectFolder.objects.all()
    context['category_groups'] = query
    from . import dynamic_breadcrumb_modal
    context['html_dynamic_breadcrumb'] = format_html(dynamic_breadcrumb_modal(category_group_object))

    data['html_form'] = render_to_string(template_name, context, request=request)

    return JsonResponse(data)


def workflow_stage_action_create_modal(request, uuid_stage = None):
    from CatiaFramework.models import Workflow_Stage, Project_CatiaFramework_Ref, ProjectUser_CatiaFramework_Ref, Workflow_Instruction, Workflow_Object
    stage = get_object_or_404(Workflow_Stage, pk=uuid_stage)
    workflow = Workflow.objects.filter(workflows_children_stages = stage).get()

    user = request.user.username
    projectuser = ProjectUser_CatiaFramework_Ref.objects.filter(nickname = user).get()
    current_project = projectuser.reference_projectuser.current_project
    from CatiaFramework.forms import ActionStageForm


    if request.user.is_authenticated == True:  
        if request.method == 'POST':
            form = ActionStageForm(request.POST, request.FILES, **{"parent_workflow": workflow, "parent_stage": stage})
            form.instance.parent_stage = stage
            parent_action = stage.get_root_actions().first()
            if parent_action:
                form.instance.parent_action = parent_action.get_last_action()
            else:
                form.instance.parent_action = None
            form.instance.project_model = Project_CatiaFramework_Ref.objects.filter(UUID = current_project.UUID ).get()
            form.instance.owner =  ProjectUser_CatiaFramework_Ref.objects.filter(UUID = request.user.projectuser.UUID).get()   
            form.instance.project_model = Project_CatiaFramework_Ref.objects.filter(UUID = request.user.projectuser.current_project.UUID).get()
            form.instance.instrucion = Workflow_Instruction.objects.create()
            form.instance.is_active = False
            form.instance.type = 'TEMPLATE'
            form.instance.status = "WAITING" 
            form.instance.accessibility = "PROJECT_USERS" 
        else:
            form = ActionStageForm(**{"parent_workflow": workflow, "parent_stage": stage})
            form.instance.parent_stage = stage

    #required object instances are defined with help of target object
    # #find all required objects within current stage-->parent_workflow
    # query = Workflow_Object.objects.filter(parent_stage__parent_workflow_id = workflow.UUID)
    # form.fields['required_objects'].queryset = query
    # #find all required actions within current stage-->parent_workflow
    # query = Workflow_Action.objects.filter(parent_stage__parent_workflow_id = workflow.UUID)
    # form.fields['required_actions'].queryset = query

 
    return  workflow_stage_action_save_form(request, form, 'modals/workflow_action/action_create_modal_addto_stage.html')


def workflow_stage_action_update_modal(request, uuid_action):

    action = get_object_or_404(Workflow_Action, pk=uuid_action)
    from CatiaFramework.models import Workflow_Stage

    if action.parent_stage: #if it is stage action
        workflow = action.parent_stage.parent_workflow
        stage = action.parent_stage
    if action.parent_object:   #if it is object action    
        workflow = action.parent_object.parent_stage.parent_workflow
        stage = action.parent_object.parent_stage

    
    from CatiaFramework.forms import ActionStageForm
    if request.method == 'POST':
        form = ActionStageForm(request.POST, request.FILES, instance=action, **{"parent_workflow": workflow, "parent_stage": stage})
    else:
        form = ActionStageForm(instance=action, **{"parent_workflow": workflow, "parent_stage": stage})
    return workflow_stage_action_save_form(request, form, 'modals/workflow_action/stage_action_update_modal.html')

def workflow_stage_action_delete_modal(request, uuid_action):
    action = get_object_or_404(Workflow_Action, pk=uuid_action)
    data = dict()
    if request.method == 'POST':
        action.delete()
        data['form_is_valid'] = True 
    else:
        context = {'action': action}
        data['html_form'] = render_to_string('modals/workflow_action/action_delete_modal.html',
            context,
            request=request,
        )
    return JsonResponse(data)

def load_content_stage_action_create_modal(request):
    '''View used to reload content in the dashboard
    '''
    trigger_id = request.GET.get('trigger_id')
    folder_id = request.GET.get('folder_id')
    component_id = request.GET.get('component_id')

    current_category_group = DotNet_ProjectFolder.objects.filter(UUID = folder_id).get()

    context={}
    context_category_groups={}
    data={}

    context['category_group'] = current_category_group

    #Category card was clicked
    if trigger_id == 'switch_category':

        query = DotNet_ProjectFolder.objects.filter(parent_folder__UUID = folder_id)           
        context_category_groups['category_groups'] = query
        context['category_group'] = current_category_group        
        from . import dynamic_breadcrumb_modal
        context_category_groups['html_dynamic_breadcrumb'] = format_html(dynamic_breadcrumb_modal(current_category_group))
        data['html_category_groups'] =render_to_string('modals/workflow_action/cards_category_group_children.html', context_category_groups, request=request)
        #get all users which have project of user in request

        context['dotnet_components']=current_category_group.dotnet_components
        data['html_dotnet_components'] =render_to_string('modals/workflow_action/dotnet_component_list_modal_content.html', context, request=request)

   #Component was selected
    if trigger_id == 'component_selection':
        current_component = DotNet_Component.objects.filter(UUID = component_id).get()
        data['dotnet_component_id']=str(current_component.UUID)

        context['dotnet_component']=current_component
        data['html_dotnet_component'] =render_to_string('modals/workflow_action/dotnet_component_details_modal_content.html', context, request=request)
    data['folder_id']=str(current_category_group.UUID)
    return JsonResponse(data)


def workflow_stage_action_execute_modal(request):
    if request.method == 'POST':
        workflow_uuid = request.POST.get('UUID_workflow', None)
        action_uuid = request.POST.get('UUID_action', None)  
        request_uuid = request.POST.get('UUID_request', None)
        stage_uuid = request.POST.get('UUID_stage', None)   
        session_uuid = request.POST.get('UUID_session', None)
        component_uuid = request.POST.get('component_uuid', None)
        target_object_uuid = request.POST.get('UUID_target_object', None)
    else:
        workflow_uuid = request.GET.get('UUID_workflow', None)
        action_uuid = request.GET.get('UUID_action', None)  
        request_uuid = request.GET.get('UUID_request', None)
        stage_uuid = request.GET.get('UUID_stage', None)   
        session_uuid = request.GET.get('UUID_session', None)
        component_uuid = request.GET.get('component_uuid', None)
        target_object_uuid = request.GET.get('UUID_target_object', None)
    data = dict()
    if request.method == 'POST':
        target_object = get_object_or_404(Workflow_Object, pk=target_object_uuid)
        target_object_parameters = target_object.instance_parameters
        from CatiaFramework.forms import ObjectFormParameters
        formdata = request.POST.get('formdata')
        if formdata:

            # Parse the formdata string into a dictionary
            parsed_data = json.loads(formdata)
            # Flatten the dictionary to match form's expected data structure
            # Replace "on" and "off" with True and False in each dictionary in the list
            for dictionary in parsed_data:
                for key, value in dictionary.items():
                    if value == "on":
                        dictionary[key] = True
                    elif value == "off":
                        dictionary[key] = False
            #formdata is not returning checkboxes if they are not selected. They have to extended in order to make the mparameters visible in Framework
            existing_names = {item['name'] for item in parsed_data if 'name' in item}
            for key, value in target_object_parameters.items():
                if isinstance(value, bool) and key not in existing_names:
                    parsed_data.append({"name": key, "value": value})    


            form = ObjectFormParameters(parsed_data)
            if form.is_valid():
                data['form_is_valid'] = True
                action = get_object_or_404(Workflow_Action, UUID = action_uuid )

                from CatiaFramework.Views.workflow.workflow_viewer_dashboard import execute_url_action, execute_stage_action
                if action.url_route:      
                    kwargs = {"workflow_uuid":workflow_uuid, "action_uuid":action_uuid , "request_uuid":request_uuid, "stage_uuid":stage_uuid , "session_uuid": session_uuid, "component_uuid": component_uuid,  }
                    if target_object_parameters:
                        kwargs = {**kwargs, **target_object_parameters}
                    return JsonResponse(execute_url_action(request, **kwargs))
                execute_stage_action(request, parsed_data)
            else:
                context={}
                context.update({'form': form})
                data['form_is_valid'] = False

    if request.method == 'GET':
        context = {}
        target_object = get_object_or_404(Workflow_Object, pk=target_object_uuid)
        target_object_parameters = target_object.instance_parameters
        from CatiaFramework.forms import ObjectFormParameters
        form = ObjectFormParameters(**{"instance_parameters": target_object_parameters })
        context.update({                            "instance_parameters": target_object_parameters,
                                                    "UUID_workflow":workflow_uuid,
                                                    "UUID_action": action_uuid,
                                                    "UUID_request": request_uuid,
                                                    "UUID_stage": stage_uuid,
                                                    "UUID_session": session_uuid,
                                                    "UUID_target_object": target_object_uuid,
                                                    "component_uuid": component_uuid,
            
        })
        context.update({'form': form})
        data['html_form'] = render_to_string('modals/workflow_action/stage_action_execute_modal.html',
            context,
            request=request,
        )


    return JsonResponse(data)

