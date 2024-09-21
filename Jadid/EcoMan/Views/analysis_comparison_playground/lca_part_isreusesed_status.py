from EcoMan.models import Circularity_Process
from EcoMan.models import Lca_Part
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
def lcastep_ispartreused_status(request, pk_lca_part):
    '''This view is triggered when user toggles the switch "reusability" of the part'''
    lca_part = get_object_or_404(Lca_Part, pk=pk_lca_part) 
    circularity_process = get_object_or_404(Circularity_Process, pk=lca_part.circularity_process_model.pk) 
    if circularity_process.ispartreused:
        circularity_process.ispartreused = False
        circularity_process.save()
    else:
        circularity_process.ispartreused = True
        circularity_process.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
