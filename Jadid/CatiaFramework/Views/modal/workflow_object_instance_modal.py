from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.html import format_html
from django.db.models import Q
from CatiaFramework.models import Workflow_Action, Workflow, Workflow_Object, Workflow_Session
import json, os
from website import settings
#qlca-----------------------------------------------------------------------------------
def workflow_object_instance_save_form(request, form, template_name, uuid_object_template = None, uuid_current_session = None):
    data = dict()
    context = dict()
    if request.method == 'POST':
        if form.is_valid():
            instance_object = form.save()

            for key, value in form.cleaned_data.items():
                if 'instance_parent_object' in key:
                    instance_object.required_objects.add(Workflow_Object.objects.filter(UUID = value).get())

            instance_object.save()
            if uuid_object_template:
                object_template = get_object_or_404(Workflow_Object, UUID =uuid_object_template )
                object_template.instances.add(instance_object)
                object_template.save()
            if form.cleaned_data.get('selected_instance_uuid', None):
                reference_object = Workflow_Object.objects.filter(UUID = form.cleaned_data.get('selected_instance_uuid', None)).get()
                instance_object.reference_instance = reference_object
                instance_object.save()               

            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    context.update({'form': form})
    if uuid_object_template:
        context['uuid_object_template'] = uuid_object_template
        context['uuid_current_session'] = uuid_current_session


        selected_workflow = None
        context['workflow'] = selected_workflow
        selected_session =None
        context['session'] = selected_session
        selected_instance =None
        context['instance'] = selected_instance

        workflows = Workflow.objects.all()
        workflows = workflows.filter(Q(type = "DATABASE_TEMPLATE") or Q(type = "FRAMEWORK_INTERNAL") )
        context['workflows'] = workflows
        sessions = None
        context['sessions'] = sessions
        instances = None
        context['instances'] = instances        

    data['html_form'] = render_to_string(template_name, context, request=request)

    return JsonResponse(data)


def workflow_object_instance_create_modal(request, uuid_object_template = None, uuid_current_session = None):
    '''View used to create a and add a reference instance (based on other intance) to a Object template
    '''
    from CatiaFramework.models import Project_CatiaFramework_Ref, ProjectUser_CatiaFramework_Ref, Workflow_Instruction, Workflow_Object, Workflow_Session
    object = get_object_or_404(Workflow_Object, pk=uuid_object_template)
    session = get_object_or_404(Workflow_Session, pk=uuid_current_session)
    stage = object.parent_stage
    workflow = Workflow.objects.filter(workflows_children_stages = stage).get()
    user = request.user.username
    projectuser = ProjectUser_CatiaFramework_Ref.objects.filter(nickname = user).get()
    current_project = projectuser.reference_projectuser.current_project
    from CatiaFramework.forms import WorkflowObjectInstanceForm
    if request.method == 'POST':
        form = WorkflowObjectInstanceForm(request.POST, **{"object_template": object})
        form.instance.project_model = Project_CatiaFramework_Ref.objects.filter(UUID = current_project.UUID ).get()
        parent_action = object.get_root_actions().first()
        if parent_action:
            form.instance.parent_action = parent_action.get_last_action()
        else:
            form.instance.parent_action = None
        form.instance.project_model = Project_CatiaFramework_Ref.objects.filter(UUID = current_project.UUID ).get()
        form.instance.owner =  ProjectUser_CatiaFramework_Ref.objects.filter(UUID = request.user.projectuser.UUID).get()   
        form.instance.project_model = Project_CatiaFramework_Ref.objects.filter(UUID = request.user.projectuser.current_project.UUID).get()
        form.instance.instruction = Workflow_Instruction.objects.create()
        form.instance.instance_parameters = None if object.instance_parameters is None else object.instance_parameters.copy()
        form.instance.is_active = False
        form.instance.type = 'REFERENCE'
        form.instance.status = "WAITING" 
        form.instance.accessibility = "PROJECT_USERS"  
        form.instance.workflow_session = session
    else:
        form = WorkflowObjectInstanceForm(**{"object_template": object})
        form.instance.parent_object = object

    return workflow_object_instance_save_form(request, form, 'modals/workflow_object_instance/object_instance_create_modal.html', uuid_object_template, uuid_current_session)

def workflow_object_instance_update_modal(request, uuid_object_instance):

    object_instance = get_object_or_404(Workflow_Object, pk=uuid_object_instance)
    from CatiaFramework.models import Workflow_Stage
    parent_object_template = Workflow_Object.objects.filter(instances = object_instance).get()
    from CatiaFramework.forms import WorkflowObjectInstanceUpdateForm
    if request.method == 'POST':
        form = WorkflowObjectInstanceUpdateForm(request.POST, request.FILES, instance=object_instance)
    else:
        form = WorkflowObjectInstanceUpdateForm(instance=object_instance)
    return workflow_object_instance_save_form(request, form, 'modals/workflow_object_instance/object_instance_update_modal.html')

def workflow_object_instance_delete_modal(request, uuid_object_instance):
    object_instance = get_object_or_404(Workflow_Object, pk=uuid_object_instance)
    data = dict()
    if request.method == 'POST':
        object_instance.delete()

        data['form_is_valid'] = True 
    else:
        context = {'object': object_instance}
        data['html_form'] = render_to_string('modals/workflow_object_instance/object_instance_delete_modal.html',
            context,
            request=request,
        )
    return JsonResponse(data)






def workflow_object_instance_next_tab(request):
    '''View used to reload content in the dashboard
    '''

    trigger = request.GET.get('trigger',None)
    workflow_id = request.GET.get('workflow_id',None)
    session_id = request.GET.get('session_id',None)
    instance_id = request.GET.get('instance_id',None)    
    context={}
    data={}

    #User has selected a workflow
    if trigger == 'workflow_selected':
        current_workflow = Workflow.objects.filter(UUID =workflow_id).get()
        query = Workflow_Session.objects.filter(workflow_model = current_workflow)          
        context['sessions'] = query.all()
        context['workflow'] = current_workflow
        context['instance'] = None
        context['session'] = None    
        data['html_session_index'] =render_to_string('modals//workflow_object_instance//workflow_session_index_for_modal.html', context, request=request)
        data['context'] = {'instance' : None, 'trigger' : trigger }
    #User has selected a session
    if trigger == 'session_selected':

        if workflow_id:
            current_workflow = Workflow.objects.filter(UUID =workflow_id)
            current_workflow=current_workflow.get()

        if session_id:     
            current_session = Workflow_Session.objects.filter(UUID =session_id)       
            current_session=current_session.get()

        #collect all interesting instances from selected session
        session_dict = current_session.workflow_model.get_structure_dict( session_UUID = str(current_session.UUID), complete = True)
        context['session'] = session_dict
        context['instance'] = None        
        data['html_session_index'] =render_to_string('modals//workflow_object_instance//workflow_instance_index_for_modal.html', context, request=request)
        data['context'] = {'instance' : None, 'trigger' : trigger }


    #User has selected an instance
    if trigger == 'instance_selected':

        if workflow_id:
            current_workflow = Workflow.objects.filter(UUID =workflow_id)
            current_workflow=current_workflow.get()
            context['workflow'] = current_workflow.as_dict()
        if session_id:     
            current_session = Workflow_Session.objects.filter(UUID =session_id)       
            current_session=current_session.get()
            context['session'] = current_session.as_dict()
        if instance_id:     
            current_instance = Workflow_Object.objects.filter(UUID =instance_id)       
            current_instance=current_instance.get()            
            context['instance'] = current_instance.as_dict()      

        data['html_session_index'] =render_to_string('modals//workflow_object_instance//workflow_instance_summary_for_modal.html', context, request=request)
        data['context'] = context
        data['context']['trigger'] = trigger 

    return JsonResponse(data)


def workflow_object_select_tab(request):
    '''View used to reload content in the dashboard
    '''
# select_workflow_tab
# select_session_tab
# select_instance_tab
# select_summary_tab

    #read ajax request
    trigger = request.GET.get('trigger',None)
    workflow_id = request.GET.get('workflow_id',None)
    session_id = request.GET.get('session_id',None)
    instance_id = request.GET.get('instance_id',None)    

    #try to obtain objects
    current_workflow = Workflow.objects.filter(UUID=workflow_id).get() if workflow_id else None
    current_session = Workflow_Session.objects.filter(UUID=session_id).get()  if session_id else None
    current_instance = Workflow_Object.objects.filter(UUID=instance_id).get()  if instance_id else None

    current_workflow_dict = current_workflow.as_dict() if workflow_id else None
    current_session_dict = current_session.as_dict()  if session_id else None
    current_instance_dict = current_instance.as_dict()  if instance_id else None             

    context={}
    data={}

    #User has clicked abreadcrumb "select_workflow_tab"
    if trigger == 'select_workflow_tab':
        workflows = Workflow.objects.all()
        workflows = workflows.filter(Q(type = "DATABASE_TEMPLATE") or Q(type = "FRAMEWORK_INTERNAL") )          
        context['workflows'] = workflows
        data['html_session_index'] =render_to_string('modals//workflow_object_instance//workflow_index_for_modal.html', context, request=request)
        data['context'] = {'workflow' : current_workflow_dict, 'session' : current_session_dict, 'instance' : current_instance_dict, 'trigger' : trigger }

    #User has clicked abreadcrumb "select_session_tab"
    if trigger == 'select_session_tab':
        if current_workflow:
            sessions = Workflow_Session.objects.filter(workflow_model = current_workflow).all() 
        else: 
            sessions = None         
        context['sessions'] = sessions
        data['html_session_index'] =render_to_string('modals//workflow_object_instance//workflow_session_index_for_modal.html', context, request=request)
        data['context'] = {'workflow' : current_workflow_dict, 'session' : current_session_dict, 'instance' : current_instance_dict, 'trigger' : trigger  }

    #User has clicked abreadcrumb "select_instance_tab"
    if trigger == 'select_instance_tab':         
        context['workflow'] = current_workflow
        if current_session:
            session_dict = current_session.workflow_model.get_structure_dict( session_UUID = str(current_session.UUID), complete = True)
        else:
            session_dict = None
        context['session'] = session_dict
        data['html_session_index'] =render_to_string('modals//workflow_object_instance//workflow_instance_index_for_modal.html', context, request=request)
        data['context'] = {'workflow' : current_workflow_dict, 'session' : current_session_dict, 'instance' : current_instance_dict, 'trigger' : trigger  }

    #User has clicked abreadcrumb "select_summary_tab"
    if trigger == 'select_summary_tab':         
        context['instance'] = current_instance        
        data['html_session_index'] =render_to_string('modals//workflow_object_instance//workflow_instance_summary_for_modal.html', context, request=request)
        data['context'] = {'workflow' : current_workflow_dict, 'session' : current_session_dict, 'instance' : current_instance_dict, 'trigger' : trigger  }

    return JsonResponse(data)