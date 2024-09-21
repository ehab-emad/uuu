from BoltMan.models.frictionjoint import Friction_Joint
from django.template.loader import render_to_string
from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ...forms.forms import FrictionJointForm

#Boltgeometry-----------------------------------------------------------------------------------
def frictionjoint_save_form(request, form, template_name):
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

def frictionjoint_create(request):
    if request.method == 'POST':
        form = FrictionJointForm(request.POST)
    else:
        form = FrictionJointForm()
    return frictionjoint_save_form(request, form, 'modals/frictionjoint/frictionjoint_create_modal.html')

def frictionjoint_update(request, pk):
    boltgeometry = get_object_or_404(Friction_Joint, pk=pk)
    if request.method == 'POST':
        form = FrictionJointForm(request.POST, instance=boltgeometry)
    else:
        form = FrictionJointForm(instance=boltgeometry)
    return frictionjoint_save_form(request, form, 'modals/frictionjoint/frictionjoint_update_modal.html')

def frictionjoint_delete(request, pk):
    frictionjoint = get_object_or_404(Friction_Joint, pk=pk)
    data = dict()
    if request.method == 'POST':
        frictionjoint.delete()
        data['form_is_valid'] = True  # This is just to play along with the existing code

    else:
        context = {'frictiononjoint': frictionjoint}
        data['html_form'] = render_to_string('modals/frictionjoint/frictionjoint_delete_modal.html',
            context,
            request=request,
        )
    return JsonResponse(data)