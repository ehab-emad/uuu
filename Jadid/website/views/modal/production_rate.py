from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ConceptMan.forms import ProductionRateForm
from functools import reduce
from website.models import Production_Rate

def production_rate_save_form(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            new_part =form.save()
            if request.user.is_authenticated == True:
                new_part.user=request.user
            new_part.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request),
    return JsonResponse(data)

def production_rate_update(request, pk):
    production_rate = get_object_or_404(Production_Rate, pk=pk)
    if request.method == 'POST':
        form = ProductionRateForm(request.POST, instance=production_rate)
    else:
        form = ProductionRateForm(instance=production_rate)
    return production_rate_save_form(request, form, 'modals/production_rate/production_rate_update_modal.html')


