from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from functools import reduce
from EcoMan.models import Instance_Idemat_Database_Process
from EcoMan.models import Lca_Part
from django.db.models import ProtectedError
from django.contrib import messages
from django.shortcuts import redirect

#idemat_process-----------------------------------------------------------------------------------
def instance_idemat_process_save_form(request, form, template_name, qlca_step=None):
    data = dict()
    context = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            #find all referencing Lca_Parts and save them accordingly
            steps = Lca_Part.objects.filter(material_instance_idemat_model__id=form.instance.id)
            for step in steps:
                temp=step.save()

            steps = Lca_Part.objects.filter(process_instance_idemat_model__id=form.instance.id)
            for step in steps:
                temp=step.save()

            steps = Lca_Part.objects.filter(transport_instance_idemat_model__id=form.instance.id)
            for step in steps:
                temp=step.save()
        else:
            data['form_is_valid'] = False

    if qlca_step:
        part_name=qlca_step.part_model.name
        context['part_name']=part_name
        form.fields['part_weight'].initial=qlca_step.part_model.weight 
    else:
        context['part_name']=""
    context = {'form': form}

    data['html_form'] = render_to_string(template_name, context, request=request),
    return JsonResponse(data)

def instance_idemat_process_delete(request, pk):

    instance_idemat_process = get_object_or_404(Instance_Idemat_Database_Process,pk=pk)

    try:

        instance_idemat_process.delete()

        messages.add_message(request,messages.SUCCESS, "Idemat Process was successfully removed!")

    except ProtectedError:

        messages.add_message(request,messages.ERROR, "Dependancies error.")

    except Exception as e:

        messages.add_message(request,messages.ERROR, e)

    return redirect(request.META.get('HTTP_REFERER'))