from BoltMan.models.boltgeometry import Bolt_Geometry
from django.template.loader import render_to_string
from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ...forms.forms import BoltGeometryForm

#Boltgeometry-----------------------------------------------------------------------------------
def boltgeometry_save_form(request, form, template_name):
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

def boltgeometry_create(request):
    if request.method == 'POST':
        form = BoltGeometryForm(request.POST)
    else:
        form = BoltGeometryForm()
    return boltgeometry_save_form(request, form, 'modals/boltgeometry/boltgeometry_create_modal.html')

def boltgeometry_update(request, pk):
    boltgeometry = get_object_or_404(Bolt_Geometry, pk=pk)
    if request.method == 'POST':
        form = BoltGeometryForm(request.POST, instance=boltgeometry)
    else:
        form = BoltGeometryForm(instance=boltgeometry)
    return boltgeometry_save_form(request, form, 'modals/boltgeometry/boltgeometry_update_modal.html')

def boltgeometry_delete(request, pk):
    boltgeometry = get_object_or_404(Bolt_Geometry, pk=pk)
    data = dict()
    if request.method == 'POST':
        boltgeometry.delete()
        data['form_is_valid'] = True  # This is just to play along with the existing code

    else:
        context = {'boltgeometry': boltgeometry}
        data['html_form'] = render_to_string('modals/boltgeometry/boltgeometry_delete_modal.html',
            context,
            request=request,
        )
    return JsonResponse(data)