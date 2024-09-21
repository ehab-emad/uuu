from EcoMan.models import Circularity_Process
from EcoMan.models import Instance_Idemat_Database_Process
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
def process_instance_is_active(request, pk_process_instance):
    '''This view is triggered when user toggles the switch "is used" of the process instance'''
    process_instance = get_object_or_404(Instance_Idemat_Database_Process, pk=pk_process_instance) 
    
    if process_instance.is_active:
        process_instance.is_active = False
        process_instance.save()
    else:
        process_instance.is_active = True
        process_instance.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
