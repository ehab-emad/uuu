from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from functools import reduce
from EcoMan.models import Analysis
from EcoMan.models import Analysis_Comparison
from EcoMan.models import Utilisation_Process, Vehicle_EcoMan_Ref
from website.models import Vehicle
from django.contrib import messages
from django.shortcuts import redirect
from django.db.models import ProtectedError


'''
Devoted to analysis 
'''
#analysis_save_form-----------------------------------------------------------------------------------
def analysis_save_form(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            analysis=get_object_or_404(Analysis, pk=form.instance.pk)
            if request.POST.get('vehicle'):
                vehicle = get_object_or_404(Vehicle_EcoMan_Ref, pk=request.POST['vehicle'])
                utilisation_instance=Utilisation_Process()
                utilisation_instance.vehicle=vehicle
                utilisation_instance.save()
                analysis.utilisation_instance_model.add(utilisation_instance)
                analysis.save()
                utilisation_instance.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request),
    return JsonResponse(data)


#Add Utilisation
def analysis_add_utilisation(request, pk):
    analysis = get_object_or_404(Analysis, pk=pk)
    vehicle = analysis.concept_model.vehicles.first()
    from EcoMan.forms import UtilisationInstanceCreateForm
    if request.method == 'POST':
        form = UtilisationInstanceCreateForm(request.POST, instance=analysis)
    else:
        form = UtilisationInstanceCreateForm(instance=analysis)
    form.fields['vehicle'].choices=[(vehicle.UUID, vehicle.reference_vehicle.name + " Owner: " + vehicle.reference_vehicle.owner.username)]
    return analysis_save_form(request, form, 'modals/utilisation_process/analysis_addnew_utilisation.html')

'''
Devoted to analysis two column
'''
#analysis_save_form-----------------------------------------------------------------------------------
def analysis_comparison_save_form(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            analysis_comparison=get_object_or_404(Analysis_Comparison, pk=form.instance.pk)
            if request.POST.get('vehicle'):
                vehicle =  get_object_or_404(Vehicle_EcoMan_Ref, pk=request.POST['vehicle'])
                utilisation_instance=Utilisation_Process()
                utilisation_instance.vehicle=vehicle
                utilisation_instance.save()
                analysis_comparison.utilisation_instance_model.add(utilisation_instance)
                analysis_comparison.save()
                utilisation_instance.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request),
    return JsonResponse(data)


#Add Utilisation to analysis comparison
def analysis_comparison_add_utilisation(request, pk):
    analysis_comparison = get_object_or_404(Analysis_Comparison, pk=pk)
    vehicle = analysis_comparison.analysis_left.concept_model.vehicles.first()
    from EcoMan.forms import UtilisationInstanceCreateForm_Analysis_Comparison
    if request.method == 'POST':
        form = UtilisationInstanceCreateForm_Analysis_Comparison(request.POST, instance=analysis_comparison)
    else:
        form = UtilisationInstanceCreateForm_Analysis_Comparison(instance=analysis_comparison)
    form.fields['vehicle'].choices=[(vehicle.UUID, vehicle.reference_vehicle.name + " Owner: " + vehicle.reference_vehicle.owner.username)]
    return analysis_comparison_save_form(request, form, 'modals/utilisation_process/analysis_comparison_addnew_utilisation.html')



#idemat_process-----------------------------------------------------------------------------------
def utilisation_instance_process_save_form(request, form, template_name):
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
#utilisation instance create
def utilisation_instance_process_create(request, pk_analysis=None):
    from EcoMan.forms import UtilisationInstanceCreateForm
    if request.method == 'POST':
        form = UtilisationInstanceCreateForm(request.POST)
    else:
        form = UtilisationInstanceCreateForm()
    return utilisation_instance_process_save_form(request, form, 'modals/utilisation_process/utilisation_instance_process_create_modal', pk_analysis)
   
#utilisation instance update
def utilisation_instance_process_update(request, pk_instance, pk_analysis=None):
    instance_utilisation_process = get_object_or_404(Utilisation_Process, pk=pk_instance)
    analysis=None
    from EcoMan.forms import UtilisationInstanceUpdateForm
    if request.method == 'POST':
        form = UtilisationInstanceUpdateForm(request.POST, instance=instance_utilisation_process)
    if request.method == 'GET':  
        form = UtilisationInstanceUpdateForm(instance=instance_utilisation_process)
    return utilisation_instance_process_save_form(request, form, 'modals/utilisation_process/instance_utilisation_update_modal.html')

def utilisation_instance_process_delete(request, pk):
    utilisation_process = get_object_or_404(Utilisation_Process,pk=pk)
    try:
        utilisation_process.delete()
        messages.add_message(request,messages.SUCCESS, "Concept Utilisation was successfully removed!")
    except ProtectedError:
        messages.add_message(request,messages.ERROR, "Dependancies error.")
    except Exception as e:
        messages.add_message(request,messages.ERROR, e)
    return redirect(request.META.get('HTTP_REFERER'))