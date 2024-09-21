from MatMan.models.engineering_material import Engineering_Material
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

    
#engineeringmaterial_-----------------------------------------------------------------------------------
def engineeringmaterial_save_form(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            boltmaterial = Engineering_Material.objects.all()
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request),
    return JsonResponse(data)

def EngineeringMaterial_create(request):
    if request.method == 'POST':
        from MatMan.forms import EngineeringMaterialForm
        form = EngineeringMaterialForm(request.POST)
    else:
        form = EngineeringMaterialForm()
    return engineeringmaterial_save_form(request, form, 'modals/engineeringmaterial/engineeringmaterial_create_modal.html')

def EngineeringMaterial_update(request, pk):
    boltmaterial = get_object_or_404(Engineering_Material, pk=pk)
    if request.method == 'POST':
        from MatMan.forms import EngineeringMaterialForm
        form = EngineeringMaterialForm(request.POST, instance=boltmaterial)
    else:
        form = EngineeringMaterialForm(instance=boltmaterial)
    return engineeringmaterial_save_form(request, form, 'modals/engineeringmaterial/engineeringmaterial_update_modal.html')

def EngineeringMaterial_delete(request, pk):
    boltmaterial = get_object_or_404(Engineering_Material, pk=pk)
    data = dict()
    if request.method == 'POST':
        boltmaterial.delete()
        data['form_is_valid'] = True  
    else:
        context = {'boltmaterial': boltmaterial}
        data['html_form'] = render_to_string('modals/engineeringmaterial/engineeringmaterial_delete_modal.html',
            context,
            request=request,
        )
    return JsonResponse(data)

