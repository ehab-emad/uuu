from BoltMan.models.frictionhead import Friction_Head
from django.template.loader import render_to_string
from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ...forms.forms import FrictionHeadForm

#Boltgeometry-----------------------------------------------------------------------------------
def frictionhead_save_form(request, form, template_name):
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

def frictionhead_create(request):
    if request.method == 'POST':
        form = FrictionHeadForm(request.POST)
    else:
        form = FrictionHeadForm()
    return frictionhead_save_form(request, form, 'modals/frictionhead/frictionhead_create_modal.html')

def frictionhead_update(request, pk):
    boltgeometry = get_object_or_404(Friction_Head, pk=pk)
    if request.method == 'POST':
        form = FrictionHeadForm(request.POST, instance=boltgeometry)
    else:
        form = FrictionHeadForm(instance=boltgeometry)
    return frictionhead_save_form(request, form, 'modals/frictionhead/frictionhead_update_modal.html')

def frictionhead_delete(request, pk):
    frictionhead = get_object_or_404(Friction_Head, pk=pk)
    data = dict()
    if request.method == 'POST':
        frictionhead.delete()
        data['form_is_valid'] = True  # This is just to play along with the existing code

    else:
        context = {'frictiononhead': frictionhead}
        data['html_form'] = render_to_string('modals/frictionhead/frictionhead_delete_modal.html',
            context,
            request=request,
        )
    return JsonResponse(data)