from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from NormMan.models import Workflow_Session
from NormMan.forms import WorkflowSessionEditForm

def update_save_form(request, form: WorkflowSessionEditForm, template_name, redirect = False):
    '''This function will save modal form of an existing object Analysis_Comparison
    '''
    data = dict()
    context = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request),
    return JsonResponse(data)

def workflow_session_update(request, uuid):
    workflow_session = get_object_or_404(Workflow_Session, UUID=uuid)
    if request.method == 'POST':
        form = WorkflowSessionEditForm(request.POST, request.FILES, instance=workflow_session)
    else:
        form = WorkflowSessionEditForm(instance=workflow_session)
    return update_save_form(request, form, 'modal/workflows/workflow_session_update_modal.html')

def workflow_session_delete(request, uuid):
    workflow_session = get_object_or_404(Workflow_Session, UUID=uuid)
    data = dict()
    if request.method == 'POST':
        workflow_session.delete()
        data['form_is_valid'] = True  # This is just to play along with the existing code
    else:
        context = {'workflow_session': workflow_session}
        data['html_form'] = render_to_string('modal/workflows/workflow_session_delete_modal.html',
            context,
            request=request,
        )
    return JsonResponse(data)