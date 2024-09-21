from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from EcoMan.models import Circularity_Process
from EcoMan.models import Utilisation_Process
from django.contrib import messages
from django.shortcuts import redirect
from django.db.models import ProtectedError
#idemat_process-----------------------------------------------------------------------------------
def circularity_process_save_form(request, form, template_name):
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
   
#circularity instance update
def circularity_process_update(request, pk_circularity_process):
    instance_circularity_process = get_object_or_404(Circularity_Process, pk=pk_circularity_process)
    from EcoMan.forms import CircularityInstanceUpdateForm  
    if request.method == 'POST':
        form = CircularityInstanceUpdateForm(request.POST, instance=instance_circularity_process)
        
    if request.method == 'GET':  
        form = CircularityInstanceUpdateForm(instance=instance_circularity_process)
    return circularity_process_save_form(request, form, 'modals/circularity_process/circularity_process_update_modal.html')


def circularity_instance_process_delete(request, pk):

    circularity_process = get_object_or_404(Utilisation_Process,pk=pk)

    try:

        circularity_process.delete()

        messages.add_message(request,messages.SUCCESS, "Concept Utilisation was successfully removed!")

    except ProtectedError:

        messages.add_message(request,messages.ERROR, "Dependancies error.")

    except Exception as e:

        messages.add_message(request,messages.ERROR, e)

    return redirect(request.META.get('HTTP_REFERER'))