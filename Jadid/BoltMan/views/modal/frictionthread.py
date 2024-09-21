from BoltMan.models.frictionthread import Friction_Thread
from django.template.loader import render_to_string
from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ...forms.forms import FrictionThreadForm

#Boltgeometry-----------------------------------------------------------------------------------
def frictionthread_save_form(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request),
    return JsonResponse(data)

def frictionthread_create(request):
    if request.method == 'POST':
        form = FrictionThreadForm(request.POST)
    else:
        form = FrictionThreadForm()
    return frictionthread_save_form(request, form, 'modals/frictionthread/frictionthread_create_modal.html')

def frictionthread_update(request, pk):
    boltgeometry = get_object_or_404(Friction_Thread, pk=pk)
    if request.method == 'POST':
        form = FrictionThreadForm(request.POST, instance=boltgeometry)
    else:
        form = FrictionThreadForm(instance=boltgeometry)
    return frictionthread_save_form(request, form, 'modals/frictionthread/frictionthread_update_modal.html')

def frictionthread_delete(request, pk):
    frictionthread = get_object_or_404(Friction_Thread, pk=pk)
    data = dict()
    if request.method == 'POST':
        frictionthread.delete()
        data['form_is_valid'] = True  # This is just to play along with the existing code

    else:
        context = {'frictiononthread': frictionthread}
        data['html_form'] = render_to_string('modals/frictionthread/frictionthread_delete_modal.html',
            context,
            request=request,
        )
    return JsonResponse(data)