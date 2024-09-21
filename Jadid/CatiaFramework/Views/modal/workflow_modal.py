from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from CatiaFramework.models import Workflow, Workflow_Instruction, ProjectUser_CatiaFramework_Ref, Project_CatiaFramework_Ref
from CatiaFramework.forms import WorkflowForm

def update_save_form(request, form,  template_name, redirect = False):
    '''This function will save modal form of an existing object 
    '''
    data = dict()
    context = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            data['redirect_address'] = reverse('CatiaFramework:workflow_configurator', kwargs={'uuid_workflow': str(form.instance.UUID), 'editor_mode': 'True'})
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['redirect'] = redirect
    context['redirect'] = redirect
    data['html_form'] = render_to_string(template_name, context, request=request),
    return JsonResponse(data)

def workflow_create_modal(request, redirect = False):
    from CatiaFramework.forms import WorkflowForm
    redirect = redirect.lower() == 'true'
    if request.method == 'POST':
        form = WorkflowForm(request.POST, request.FILES)
        form.instance.owner =  ProjectUser_CatiaFramework_Ref.objects.filter(UUID = request.user.projectuser.UUID).get()   
        form.instance.project_model = Project_CatiaFramework_Ref.objects.filter(UUID = request.user.projectuser.current_project.UUID).get()
        form.instance.type = "DATABASE_TEMPLATE"
        form.instance.status = "WAITING"  
        form.instance.instrucion = Workflow_Instruction.objects.create()
        form.instance.is_active = False
    else:
        form = WorkflowForm()
    return update_save_form(request, form, 'modals/workflow/workflow_create_modal.html', redirect)


def workflow_update(request, uuid):
    workflow_session = get_object_or_404(Workflow, UUID=uuid)
    if request.method == 'POST':
        form = WorkflowForm(request.POST, request.FILES, instance=workflow_session)
    else:
        form = WorkflowForm(instance=workflow_session)
    return update_save_form(request, form, 'modals/workflow/workflow_update_modal.html')

def workflow_delete(request, uuid):
    workflow_session = get_object_or_404(Workflow, UUID=uuid)
    data = dict()
    if request.method == 'POST':
        workflow_session.delete()
        data['form_is_valid'] = True 
    else:
        context = {'workflow': workflow_session}
        data['html_form'] = render_to_string('modals/workflow/workflow_delete_modal.html',
            context,
            request=request,
        )
    return JsonResponse(data)



