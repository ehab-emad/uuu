import json
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import HttpResponseRedirect, JsonResponse   
from django.shortcuts import  get_object_or_404, redirect
from django.template.loader import render_to_string
from django.views.generic import TemplateView
from CatiaFramework.models import Workflow, Workflow_Object,  Workflow_Stage, Workflow_Action, Workflow_Session, ProjectUser_CatiaFramework_Ref, Project_CatiaFramework_Ref
from django.urls import reverse
from django.contrib import messages
from django.db.models import Q
def workflow_session_create(request, uuid_reference_workflow):
    reference_workflow = Workflow.objects.filter(UUID = uuid_reference_workflow).get()
    new_session = Workflow_Session.objects.create(workflow_model = reference_workflow, 
                                                  name = reference_workflow.name if reference_workflow.name != None else "NONAME" + "_session", 
                                                  owner = ProjectUser_CatiaFramework_Ref.objects.filter(nickname = request.user.username).get(),
                                                  thumbnail = reference_workflow.thumbnail,
                                                  project_model = Project_CatiaFramework_Ref.objects.filter(UUID = request.user.projectuser.current_project.UUID).get()
                                                  )

    return redirect('CatiaFramework:workflow_dashboard', uuid_session = new_session.UUID, editor_mode = False)

def workflow_session_continue(request, uuid_session):
    return redirect('CatiaFramework:workflow_dashboard', uuid_session = uuid_session, editor_mode = False)

def workflow_session_redirect_on_instance(request, uuid_instance):
    obj = get_object_or_404(Workflow_Object, UUID = uuid_instance)
    #check if object is a reference
    if obj.reference_instance:
        obj = obj.reference_instance
    uuid_session = obj.workflow_session.UUID
    return redirect('CatiaFramework:workflow_dashboard', uuid_session = uuid_session, editor_mode = False)

def workflow_session_continue_last(request, uuid_workflow):
    '''User will be redirected to the last workflow session  
    '''
    #query = Workflow_Session.objects.filter(owner__UUID = str(request.user.projectuser.UUID))
    query = Workflow_Session.objects.filter(workflow_model__UUID = uuid_workflow)
    try:
        query=query.latest('updated_at')
    except:
        return  redirect('CatiaFramework:workflow_index')
    url = reverse('CatiaFramework:workflow_dashboard',  kwargs={'uuid_session': query.UUID, 'editor_mode': False} )
    return HttpResponseRedirect(url)


class workflow_dashboard(TemplateView):

    template_name = 'CatiaFramework/workflow/workflow_viewer_dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/user/login')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        target_object_uuid = kwargs.get('uuid_session', None)
        session_object = Workflow_Session.objects.filter(UUID = target_object_uuid).get()
         
        context = super(workflow_dashboard, self).get_context_data(**kwargs)
        if  not bool(session_object.workflow_model.static_structure): #check if dict is empty when yes...
            session_object.workflow_model.static_structure = dict()
            session_object.workflow_model.save()
            session_object.workflow_model.static_structure =  session_object.workflow_model.get_structure_dict(session_UUID = None, stage_UUID = None, complete = True, instances = False)
            session_object.workflow_model.save()    
        context['workflow_dict'] = session_object.workflow_model.static_structure    
        context['workflow'] = session_object.workflow_model
        context['session'] = session_object
        context['current_workflow'] = str(session_object.workflow_model)
        context['editor_mode'] = kwargs.get('editor_mode', False).lower() == "true"
        return context     

class workflow_configurator(TemplateView):

    template_name = 'CatiaFramework/workflow/workflow_viewer_dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/user/login')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        target_object_uuid = kwargs.get('uuid_workflow', None)
        session_object_uuid = kwargs.get('uuid_session', None)   
        if session_object_uuid:
            session_object  = get_object_or_404(Workflow_Session, UUID = session_object_uuid) 
        else:
            session_object = Workflow_Session()
            session_object.UUID = None     

        workflow_object = Workflow.objects.filter(UUID = target_object_uuid).get()       
        session_object.workflow_model = workflow_object
        context = super(workflow_configurator, self).get_context_data(**kwargs)
        context['workflow_dict'] = session_object.workflow_model.get_structure_dict()
        context['workflow'] = session_object.workflow_model
        context['session'] = session_object
        context['current_workflow'] = str(session_object.workflow_model)
        context['editor_mode'] = kwargs.get('editor_mode', False).lower() == "true"
        return context  



def load_workflow_session_details(request):
    '''View used to reload dashboard content after framework execution was completed 
    '''

    #read post request
    context, data = dict(), dict()
    worklfow_uuid = request.POST.get('workflow_id',None)
    stage_uuid = request.POST.get('stage_id', None) 
    session_uuid = request.POST.get('session_id', None)  
    session_uuid = None if session_uuid == "None" else session_uuid
    editor_mode = request.POST.get('editor_mode', "False")    

    #find django objects
    user = request.user.username
    user = user if not (not len(user) and 'user' in request.POST) else request.POST["user"]
    workflow_object = get_object_or_404(Workflow, UUID=worklfow_uuid) 
    session_object = None if session_uuid is None else get_object_or_404(Workflow_Session, UUID=session_uuid)    
    stage_object = get_object_or_404(Workflow_Stage, UUID=stage_uuid)

    #check if object workflow was modified

    if workflow_object.modified:
        workflow_object.static_structure = dict()
        workflow_object.save()
        workflow_object.static_structure = workflow_object.get_structure_dict(session_UUID = None, stage_UUID = None, complete = True, instances = False)
        workflow_object.modified = False
        workflow_object.save()

    #add some context information
    
    
    #get workflow dictionary
    workflow_dict = workflow_object.static_structure
    stage_dict = next((item for item in workflow_dict if item["UUID"] == stage_uuid), None)
    #extend static dictionary with dynamic instances
    for template in stage_dict['objects']:
        query = Workflow_Object.objects.filter((Q(type = "INSTANCE") or Q(type = "REFERENCE")) and 
                                               
                                               Q(workflow_session__UUID = session_uuid)
                                               ).filter(instances_object__UUID = template['UUID'] )
        for instance in query:
            parent_stage = instance.instances_object.first().get_root_object().parent_stage
            if str(parent_stage.UUID) == stage_uuid:
                template['instances'].append(instance.as_dict())

    context['stage'] = stage_dict #it is taken from static dictionary and extended with dynamic content (instances)


    context['instruction'] = stage_object.instruction            
    context['workflow'] = workflow_object   
    context['session'] = session_object        
    context['editor_mode'] = editor_mode.lower() == "true"

    

    # Render information    
    data['user'] = user
    data['html_workflow_instruction'] = render_to_string('CatiaFramework/workflow/viewer/workflow_instruction.html', context, request=request)
    data['html_workflow_object'] = render_to_string('CatiaFramework/workflow/viewer/workflow_objects.html', context, request=request)
    data['html_workflow_stage'] = render_to_string('CatiaFramework/workflow/viewer/workflow_stage.html', context, request=request)

    return JsonResponse(data)


def execute_url_action(request, optional_parameters = None,**kwargs):
    from django.shortcuts import get_object_or_404, redirect
    from django.urls import reverse
    from CatiaFramework.models import Workflow_Action
    from django_keycloak.decorators import group_required
    _auth = lambda f: group_required(f, group_name = "/be_paramount/app-ecoman")
    from django.urls import re_path as url

    #get action object
    action = get_object_or_404(Workflow_Action, UUID = str(kwargs['action_uuid']))
    ikwargs = {'uuid_session': kwargs['session_uuid']}

    # Generate the URL with arguments using reverse()
    url = reverse(action.url_route, kwargs=ikwargs)
    # Build the absolute URL using request.build_absolute_uri()
    full_url = request.build_absolute_uri(url)
    
    
    return dict({"redirect_url": full_url})


def execute_stage_action(request, optional_parameters = None):
    """
    Execution of stage action. The stage action can be executed sort of "plain"
    which will execute just some action that does not need any output and produces 
    no output as well. In the other case, stage action targets an object which
    is to be produced within the method.
    Naming convention here (as example):
        target_object_required_object_instances
            ↑               ↑             ↑
        part 1          part 2          part 3
        -> which translates to: dictionary of instances of required object of 
            selected target object
    
    :param request: ASGI-Request object 
    :return: Nothing but executes communication endpoint
    """
    workflow_uuid = request.POST.get('UUID_workflow', None)
    action_uuid = request.POST.get('UUID_action', None)  
    request_uuid = request.POST.get('UUID_request', None)
    stage_uuid = request.POST.get('UUID_stage', None)   
    session_uuid = request.POST.get('UUID_session', None)
    component_uuid = request.POST.get('component_uuid', None)
    editor_mode = request.POST.get('editor_mode', None)           
    
    workflow = get_object_or_404(Workflow, UUID = str(workflow_uuid))
    action = get_object_or_404(Workflow_Action, UUID = str(action_uuid))
    session = get_object_or_404(Workflow_Session, UUID = str(session_uuid))
    stage = get_object_or_404(Workflow_Stage, UUID = str(stage_uuid))

    #check if action contain URL
    if action.url_route:      
        kwargs = {"workflow_uuid":workflow_uuid, "action_uuid":action_uuid , "request_uuid":request_uuid, "stage_uuid":stage_uuid , "session_uuid": session_uuid, "component_uuid": component_uuid,  }
        
        return JsonResponse(execute_url_action(request, **kwargs))





    target_object_required_object_instances = dict()
    if action.target_object is not None:
        for req_object in action.target_object.required_objects.all():
            all_instances = req_object.instances.filter(workflow_session__UUID = session_uuid)
            if action.is_for_all_instances:
                for req_instance in all_instances:
                    target_object_required_object_instances[str(req_instance.UUID)] = instance_dict(req_instance) 
            else:
                for req_instance in all_instances:
                    if req_instance.is_active:
                        target_object_required_object_instances[str(req_instance.UUID)] = instance_dict(req_instance) 

    action_required_object_instances = dict()
    for req_object in action.required_objects.all():
        all_instances = req_object.instances.filter(workflow_session__UUID = session_uuid)
        if action.is_for_all_instances:
            for req_instance in all_instances:
                action_required_object_instances[str(req_instance.UUID)] = instance_dict(req_instance) 
        else:
            for req_instance in all_instances:
                if req_instance.is_active:
                    action_required_object_instances[str(req_instance.UUID)] = instance_dict(req_instance)          

    async_to_sync(get_channel_layer().group_send)(
        'chat_' + request.user.username,
        {
            'type': 'framework_command',
            'message': json.dumps({
                'trigger': "StageAction",
                'user': request.user.username, 
                'session_uuid': session_uuid,
                'session_name': session.name,
                'workflow_uuid': str(workflow.UUID),
                'workflow_name': session.workflow_model.name,
                'framework_action_uuid': request_uuid,
                'action_uuid': action_uuid,
                'object_uuid': None,                
                'stage_uuid': str(stage.UUID),
                'executed_instances' : None,
                'action_required_objects' : action_required_object_instances,
                'target_object': None if action.target_object is None else {
                    "UUID": str(action.target_object.UUID),
                    "Name": action.target_object.name,
                    "Description": action.target_object.description,
                    "required_objects": target_object_required_object_instances,
                    "parameters": optional_parameters
                    },
                'new_instance': None,
                'shared_component_uuid': component_uuid,             
                })  
        })
    return JsonResponse(dict())


def execute_object_action(request, optional_parameters = None):
    """
    Execution of an object action. This can execute action of template object
    on selected instance of this object (or more instances at the same time). 
    Flow of the method is then to be defined in VB.Net, where the script should
    use communicated resources as is. Moreover, the method might produce a target 
    object as well, for which the information is collected as well.
    Naming convention here (as example):
        target_object_required_object_instances
            ↑               ↑             ↑
        part 1          part 2          part 3
        -> which translates to: dictionary of instances of required object of 
            selected target object
    :param request: ASGI-Request object 
    :return: Nothing but executes communication endpoint
    """
    workflow_uuid = request.POST.get('UUID_workflow', None)
    action_uuid = request.POST.get('UUID_action', None)  
    request_uuid = request.POST.get('UUID_request', None)
    object_uuid = request.POST.get('UUID_object', None)   
    session_uuid = request.POST.get('UUID_session', None)
    component_uuid = request.POST.get('UUID_component', None)
    editor_mode = request.POST.get('editor_mode', None) 
    shared_component_parameters = request.POST.get('config', None)   

    workflow = get_object_or_404(Workflow, UUID = str(workflow_uuid))
    session = get_object_or_404(Workflow_Session, UUID = str(session_uuid))
    object = get_object_or_404(Workflow_Object, UUID = str(object_uuid))
    action = get_object_or_404(Workflow_Action, UUID = str(action_uuid)) if action_uuid else Workflow_Action(type='FRAMEWORK_INTERNAL')    






    target_object_required_object_instances = dict()
    if action.target_object is not None:
        for req_object in action.target_object.required_objects.all():
            all_instances = req_object.instances.filter(workflow_session__UUID = session_uuid)
            if action.is_for_all_instances:
                for req_instance in all_instances:
                    target_object_required_object_instances[str(req_instance.UUID)] = instance_dict(req_instance) 
            else:
                for req_instance in all_instances:
                    if req_instance.is_active:
                        target_object_required_object_instances[str(req_instance.UUID)] = instance_dict(req_instance) 

    action_required_object_instances = dict()
    for req_object in action.required_objects.all():
        all_instances = req_object.instances.filter(workflow_session__UUID = session_uuid)
        if action.is_for_all_instances:
            for req_instance in all_instances:
                action_required_object_instances[str(req_instance.UUID)] = instance_dict(req_instance) 
        else:
            for req_instance in all_instances:
                if req_instance.is_active:
                    action_required_object_instances[str(req_instance.UUID)] = instance_dict(req_instance) 

    object_execution_instances, object_required_object_instances = [], dict()

    all_instances = object.instances.filter(workflow_session__UUID = session_uuid)
    for req_object in object.required_objects.all():
        for req_instance in req_object.instances.filter(workflow_session__UUID = session_uuid):
            if req_instance.is_active:
                object_required_object_instances[str(req_instance.UUID)] = instance_dict(req_instance)
    
    if action.is_for_all_instances:
        for obj_instance in all_instances:           
            object_execution_instances.append({str(obj_instance.UUID): instance_dict(obj_instance, object_required_object_instances)})
    else:
        for obj_instance in all_instances:
            if  obj_instance.is_active:
                object_execution_instances.append({str(obj_instance.UUID): instance_dict(obj_instance, object_required_object_instances)})
    
    
    async_to_sync(get_channel_layer().group_send)(
        'chat_' + request.user.username,
        {
            'type': 'framework_command',
            'message': json.dumps({
                'trigger': "ObjectInstanceAction",
                'user': request.user.username, 
                'session_uuid': session_uuid,
                'session_name': session.name,
                'workflow_uuid': str(workflow.UUID),
                'workflow_name': session.workflow_model.name,
                'framework_action_uuid': request_uuid,
                'action_uuid': action_uuid,
                'object_uuid': object_uuid,
                'stage_uuid': str(object.get_root_object().parent_stage.UUID),                                 
                'executed_instances' : object_execution_instances,
                'action_required_objects' : action_required_object_instances,
                'target_object': None if action.target_object is None else {
                    "UUID": str(action.target_object.UUID),
                    "Name": action.target_object.name,
                    "Description": action.target_object.description,
                    "required_objects": target_object_required_object_instances,
                    "parameters": optional_parameters
                    },
                'new_instance': None,
                'shared_component_uuid': component_uuid, 
                'shared_component_parameters': shared_component_parameters,
                }) 
        })
    return JsonResponse(dict())



def instance_dict(instance: object, instances_of_required_object:dict = None) -> dict:
    """
    This function returns instance dictionary based on given input arguments.
    :param instance: Object instance
    :param instances_of_required_object: Instances of selected required object
    :return: Instance dictionary
    """
    return_dict = {
        "Name": instance.name, 
        "Description": instance.description,
        "shared_component" : None if instance.thumbnail is not None else instance.thumbnail.url.split("/")[-2].split("_")[-1],
        "metadata": instance.instance_framework_metadata,
        "parameters": instance.instance_parameters,        
        }
    if instances_of_required_object is not None:
        return_dict["required_objects"] = instances_of_required_object
    return return_dict




def create_new_instance(request):
    # -> manual creation of object's instance
    UUID_object = request.POST['UUID_object']    
    stage_id = request.POST['stage_id']     
    editor_mode = request.POST['editor_mode']    
    session_id = request.POST['session_id'] 
    context, data = dict(), dict()         
    template_object = Workflow_Object.objects.filter(UUID = UUID_object ).get()   
    new_instance = template_object.instances.create()
    from CatiaFramework.models import Workflow_Session
    new_instance.workflow_session = Workflow_Session.objects.filter(UUID = session_id).get() 
    new_instance.save()
    context['stage'] = get_object_or_404(Workflow_Stage, UUID=stage_id).get_structure_dict()
    context['editor_mode'] = editor_mode.lower() == "true"
    data['html_workflow_object'] = render_to_string('CatiaFramework/workflow/viewer/workflow_objects.html', context, request=request)
    # Here maybe automatic activation? Maybe not really...
    return JsonResponse(data)
   
def load_instance_content(request):    
    '''View used to reload content after instance was selected
    '''     
    UUID_instance = request.POST['UUID_instance']       
    UUID_stage = request.POST['UUID_stage']     
    UUID_session = request.POST['UUID_session']     
    instance_object = Workflow_Object.objects.get(UUID = UUID_instance)
    editor_mode = "False"
    #change status of instances accordingly. currently only one can be active
    template_object = Workflow_Object.objects.filter(instances__UUID = UUID_instance ).first()
    all_instances = template_object.instances.all()
    for inst in all_instances:    
        if str(inst.UUID) != UUID_instance:
            inst.is_active = False
            inst.save()

        if str(inst.UUID) == UUID_instance:
            inst.is_active = True
            inst.save()           
    context={}
    data={}
    from CatiaFramework.forms import ObjectFormParameters
    form  = ObjectFormParameters(**{"instance_parameters": instance_object.instance_parameters })
    context['form'] = form
    context['instance_object'] = instance_object
    #context['stage'] = get_object_or_404(Workflow_Stage, UUID=UUID_stage).get_structure_dict()
    context['session'] = get_object_or_404(Workflow_Session, UUID=UUID_session)  
    context['editor_mode'] = editor_mode.lower() == "true"
    data['html_workflow_object'] = render_to_string('CatiaFramework/workflow/viewer/workflow_objects.html', context, request=request)
    data['html_parameters'] = render_to_string('CatiaFramework/workflow/viewer/object/object_instance_parameters.html', context, request=request)
    return JsonResponse(data)


def save_instance_parameters(request, instance_uuid):
    from CatiaFramework.models import Workflow_Object
    instance_object = get_object_or_404(Workflow_Object, UUID=instance_uuid)
    data={}
    context ={}
    if request.method == 'POST':
        from CatiaFramework.forms import ObjectFormParameters
        form = ObjectFormParameters(request.POST, **{"instance_parameters": instance_object.instance_parameters })
        if form.is_valid():

            # Convert form fields and values to JSON
            form_data = {field.name: form.cleaned_data[field.name] for field in form}
            instance_object.instance_parameters = form_data
            instance_object.save()
            messages.add_message(request,messages.SUCCESS, "Parameters Successfully changed!")
            data['html_message'] = render_to_string('website/messages_content.html', context, request=request)
            return JsonResponse(data)
        else:
            errors = form.errors.as_json()
            messages.add_message(request,messages.ERROR, "Parameters Could not be changed! "+ errors)
            data['html_message'] = render_to_string('website/messages_content.html', context, request=request)
            return JsonResponse(data)


def instance_delete_modal(request, uuid_instance):
    # -> deletion of object's instance
    instance = get_object_or_404(Workflow_Object, pk=uuid_instance)    
    target = 'modals/workflow_object/instance_delete_modal.html'
    None if request.method != 'POST' else instance.delete()
    data = {'form_is_valid': True} if request.method == 'POST' else {'html_form': render_to_string(target, {'instance': instance}, request=request,)}
    # -> here comes removement callback for framework
    return JsonResponse(data)


def instruction_load_hover(request):
    editor_mode = request.POST.get('editor_mode', None)
    object_type = request.POST.get('id', None)
    target = 'CatiaFramework/workflow/viewer/workflow_instruction.html'
    match object_type:
        case "object_action_card":
            instruction_object = get_object_or_404(Workflow_Action, UUID=request.POST['UUID_action']).instruction    
        case "stage_action_card":
            instruction_object = get_object_or_404(Workflow_Action, UUID=request.POST['UUID_action']).instruction   
        case "object_card":
            instruction_object = get_object_or_404(Workflow_Object, UUID=request.POST['UUID_object']).instruction
        case "stage":
            instruction_object = get_object_or_404(Workflow_Stage, UUID=request.POST['UUID_stage']).instruction    
    context = {
        'instruction': instruction_object,
        'editor_mode': editor_mode.lower() == "true"
    }
    data = {
        'html_workflow_instruction': render_to_string(target, context, request=request)
    }
    return JsonResponse(data)


def stage_tree_reorder(request):
    '''View used to reorder the structure of the workflow tree
    '''
    context, data = dict(), dict()
    order = request.POST.getlist('order[]')

    user = request.user.username
    user = user if not (not len(user) and 'user' in request.POST) else request.POST["user"]
    try:               
# Get the model instances based on the received order
        instances = Workflow_Stage.objects.filter(UUID__in=order)

        # Create a mapping of ID to instance
        instance_mapping = {str(instance.UUID): instance for instance in instances}

        # Update the parent_stage field based on the order
        for i in range(1, len(order)):
            instance_mapping[order[i]].parent_stage = instance_mapping[order[i - 1]]
        
        # Set the parent_stage of the first element to None
        instance_mapping[order[0]].parent_stage = None

        # Save the instances with updated order
        for instance in instances:
            instance.save()

        response_data = {
            'status': 'success',
            'message': 'Order updated successfully',
        }
        #here sections should be reloaded since there is no guarantee that server did it correctly
        return JsonResponse(response_data)

    except Exception as e:
        # Handle exceptions or errors
        response_data = {
            'status': 'error',
            'message': str(e)
        }
        return JsonResponse(response_data, status=500)
    
def objects_reorder(request):
    '''View used to reorder the structure of the workflow tree
    '''
    # -> This is actually bullshit, because there is no relation between objects that assures proper position.
    #   Thus some modification is needed
    context, data = dict(), dict()
    order = request.POST.getlist('order[]')
    order = [ins for ins in order if ins != '']

    user = request.user.username
    user = user if not (not len(user) and 'user' in request.POST) else request.POST["user"]
    try:               
    # Get the model instances based on the received order        
        instances = Workflow_Object.objects.filter(UUID__in=order)
        stage = instances[0].parent_stage

        # Create a mapping of ID to instance
        instance_mapping = {str(instance.UUID): instance for instance in instances}
        # Update the parent_stage field based on the order
        for i in range(1, len(order)):
            instance_mapping[order[i]].parent_object = instance_mapping[order[i - 1]]
            instance_mapping[order[i]].parent_stage = None


        # Set the parent_stage of the first element to None
        instance_mapping[order[0]].parent_object = None        
        instance_mapping[order[0]].parent_stage = stage  
        # # Save the instances with updated order
        for instance in instances:
            instance.save()

        response_data = {
            'status': 'success',
            'message': 'Order updated successfully',
        }
        #here sections should be reloaded since there is no guarantee that server did it correctly
        return JsonResponse(response_data)

    except Exception as e:
        # Handle exceptions or errors
        response_data = {
            'status': 'error',
            'message': str(e)
        }
        return JsonResponse(response_data, status=500)
    
def object_actions_reorder(request):
    '''View used to reorder the structure of the workflow tree
    '''
    context, data = dict(), dict()
    order = request.POST.getlist('order[]')

    user = request.user.username
    user = user if not (not len(user) and 'user' in request.POST) else request.POST["user"]
    try:               
# Get the model instances based on the received order
        instances = Workflow_Action.objects.filter(UUID__in=order)

        # Create a mapping of ID to instance
        instance_mapping = {str(instance.UUID): instance for instance in instances}

        # Update the parent_stage field based on the order
        for i in range(1, len(order)):
            instance_mapping[order[i]].parent_action = instance_mapping[order[i - 1]]
        
        # Set the parent_stage of the first element to None
        instance_mapping[order[0]].parent_action = None

        # Save the instances with updated order
        for instance in instances:
            instance.save()

        response_data = {
            'status': 'success',
            'message': 'Order updated successfully',
        }

        return JsonResponse(response_data)

    except Exception as e:
        # Handle exceptions or errors
        response_data = {
            'status': 'error',
            'message': str(e)
        }
        #here sections should be reloaded since there is no guarantee that server did it correctly
        return JsonResponse(response_data, status=500)
    
def dashboard_switch_edit_configure(request, uuid_workflow, uuid_session, editor_mode):
    old_mode = editor_mode
    new_mode = not editor_mode.lower() == "true"

    
    if old_mode:
        #we were in editor mode so we need a session uuid
        return redirect('CatiaFramework:workflow_dashboard', uuid_session = uuid_session, editor_mode = new_mode)
    else:
        #we were in productive mode se we need workflow uuid
        return redirect('CatiaFramework:workflow_configurator', uuid_workflow = uuid_workflow, uuid_session = uuid_session,   editor_mode = new_mode)        



