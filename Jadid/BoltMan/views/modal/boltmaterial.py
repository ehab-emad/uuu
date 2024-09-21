from BoltMan.models.boltmaterial import Bolt_Material
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ...forms.forms import BoltMaterialForm
    
#BoltMaterial-----------------------------------------------------------------------------------
def boltmaterial_save_form(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            boltmaterial = Bolt_Material.objects.all()
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request),
    return JsonResponse(data)

def boltmaterial_create(request):
    if request.method == 'POST':
        form = BoltMaterialForm(request.POST)
    else:
        form = BoltMaterialForm()
    return boltmaterial_save_form(request, form, 'modals/boltmaterial/boltmaterial_create_modal.html')

def boltmaterial_update(request, pk):
    boltmaterial = get_object_or_404(Bolt_Material, pk=pk)
    if request.method == 'POST':
        form = BoltMaterialForm(request.POST, instance=boltmaterial)
    else:
        form = BoltMaterialForm(instance=boltmaterial)
    return boltmaterial_save_form(request, form, 'modals/boltmaterial/boltmaterial_update_modal.html')

def boltmaterial_delete(request, pk):
    boltmaterial = get_object_or_404(Bolt_Material, pk=pk)
    data = dict()
    if request.method == 'POST':
        boltmaterial.delete()
        data['form_is_valid'] = True  
    else:
        context = {'boltmaterial': boltmaterial}
        data['html_form'] = render_to_string('modals/boltmaterial/boltmaterial_delete_modal.html',
            context,
            request=request,
        )
    return JsonResponse(data)