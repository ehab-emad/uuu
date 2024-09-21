from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from website.models import Energy_Source
from EcoMan.scripts import *
from website.scripts import *
#qlca-----------------------------------------------------------------------------------
def energysource_save_form(request, form, template_name):
    data = dict()
    context = dict()
    if request.method == 'POST':
        if form.is_valid():
            data['form_is_valid'] = True
            new_qlca =form.save()
            if request.user.is_authenticated == True:
                new_qlca.owner=request.user
            new_qlca.save()
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request),
    return JsonResponse(data)

def energysource_update(request, pk_energysource): 
    energysource = get_object_or_404(Energy_Source, pk=pk_energysource)
    from EcoMan.forms import EnergySourceForm
    if request.method == 'POST':
        form = EnergySourceForm(request.POST, instance=energysource)
    else:
        form = EnergySourceForm(instance=energysource)
    return energysource_save_form(request, form, 'modals/energy_source/energy_source_update_modal.html')
