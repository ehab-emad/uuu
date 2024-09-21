from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from CatiaFramework.models import Workflow_Object, Workflow, ProjectUser_CatiaFramework_Ref, Project_CatiaFramework_Ref, Workflow_Instruction

#qlca-----------------------------------------------------------------------------------
def object_save_form(request, form, template_name, uuid_stage = None):
    data = dict()
    context = dict()
    if request.method == 'POST':
        if form.is_valid():
            object = form.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    context.update({'uuid_stage':uuid_stage})
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)


def workflow_object_create_modal(request, uuid_stage= None):
    from CatiaFramework.forms import ObjectForm, Workflow_Stage
    parent_stage = Workflow_Stage.objects.filter(UUID = uuid_stage).get()
    parent_workflow = parent_stage.parent_workflow
    if request.method == 'POST':
        form = ObjectForm(request.POST, request.FILES)


        form = ObjectForm(request.POST, request.FILES)
        form.instance.owner =  ProjectUser_CatiaFramework_Ref.objects.filter(UUID = request.user.projectuser.UUID).get()   
        form.instance.project_model = Project_CatiaFramework_Ref.objects.filter(UUID = request.user.projectuser.current_project.UUID).get()
        form.instance.type = "TEMPLATE"
        form.instance.status = "WAITING"  

        first_template = parent_stage.get_root_objects().first()

        if first_template:
            last_template = first_template.get_last_object()
            form.instance.parent_object = last_template
            form.instance.parent_stage = None
        else:
            form.instance.parent_object = None 
            form.instance.parent_stage = parent_stage
        form.instance.parent_workflow = parent_workflow
        form.instance.instruction = Workflow_Instruction.objects.create()
        form.instance.is_active = False
    else:
        form = ObjectForm(**{"parent_workflow": parent_workflow})
    return object_save_form(request, form, 'modals/workflow_object/object_create_modal.html', uuid_stage)



def workflow_object_update_modal(request, uuid_object):
    object = get_object_or_404(Workflow_Object, pk=uuid_object)
    parent_workflow = object.get_root_object().parent_stage.get_root_stage().parent_workflow
    from CatiaFramework.forms import ObjectForm
    if request.method == 'POST':
        form = ObjectForm(request.POST, request.FILES, instance=object)
    else:
        form = ObjectForm(instance=object, **{"parent_workflow": parent_workflow})
    return object_save_form(request, form, 'modals/workflow_object/object_update_modal.html')

def workflow_object_delete_modal(request, uuid_object):
    object = get_object_or_404(Workflow_Object, pk=uuid_object)
    data = dict()
    if request.method == 'POST':
        parent_template = object.parent_object
        children_template = object.objects_children_objects.first()
        parent_stage = object.parent_stage

        #template is a an only template in stage
        if parent_stage and children_template == None and parent_template == None:
            object.delete()
            data['form_is_valid'] = True 
            return JsonResponse(data)  

        #template is a first template
        if parent_stage and children_template and parent_template == None:
            children_template.parent_stage = parent_stage
            children_template.parent_object = None
            children_template.save()
            object.delete()
            data['form_is_valid'] = True 
            return JsonResponse(data) 
        #template is between first and last template
        if parent_template and children_template and parent_stage == None:
            children_template.parent_stage = None
            children_template.parent_object = parent_template      
            children_template.save()      
            object.delete()
            data['form_is_valid'] = True 
            return JsonResponse(data) 
        #template is last
        if parent_template and children_template == None and parent_stage == None:
            object.delete()
            data['form_is_valid'] = True 
            return JsonResponse(data) 


    else:
        context = {'object': object}
        data['html_form'] = render_to_string('modals/workflow_object/object_delete_modal.html',
            context,
            request=request,
        )
    return JsonResponse(data) 


def workflow_object_delete_all_instances_modal(request, uuid_object):
    workflow_object = get_object_or_404(Workflow_Object, UUID=uuid_object)
    data = dict()
    if request.method == 'POST':
        instances = workflow_object.instances.all()
        for instance in instances:
            instance.delete()
        data['redirect_url'] = request.META.get('HTTP_REFERER', '/')
        data['form_is_valid'] = True 
    else:
        context = {'workflow_object': workflow_object}
        data['html_form'] = render_to_string('modals/workflow_object/object_delete_all_instances_modal.html',
            context,
            request=request,
        )
    return JsonResponse(data)

