from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from EcoMan.forms import MaterialProcessInstanceUpdateForm
from django.http import JsonResponse
from EcoMan.models import Lca_Part
from EcoMan.models import Instance_Idemat_Database_Process
def material_process_instance_update(request, pk_instance):
    '''
    View function allowing edit of Material Instance
    '''
    instance_lca_process = get_object_or_404(Instance_Idemat_Database_Process, pk=pk_instance)
    lca_part = Lca_Part.objects.filter(lca_process_model = pk_instance).get()
    part =  lca_part.part_model      
    if request.method == 'POST':
        form = MaterialProcessInstanceUpdateForm(request.POST, instance=instance_lca_process)
    if request.method == 'GET':  
        #calculate meq
        if int(instance_lca_process.process_quantity) == 0:
            meq = 100
        else:
            meq = int(100 + instance_lca_process.process_auxiliary_quantity / instance_lca_process.process_quantity*100)
        initial_dict={'meq': meq , 
                        'part_id': part.id,
                        'part_name': part.name,
                        'part_weight': part.weight,
                        'part_area': part.area,
                        'process_name':instance_lca_process.process_model.name ,
                        'process_unit':instance_lca_process.process_model.unit ,                        
                         }
        form = MaterialProcessInstanceUpdateForm(instance=instance_lca_process, initial = initial_dict )
    html_template = 'modals/instance_idemat_process/material_instance_idemat_process_update_modal.html'
    return save_form(request, form, html_template)


def save_form(request, form, template_name):
    data = dict()
    context = dict()
    if request.method == 'POST':
        if form.is_valid():
            instance=form.save()
            data['form_is_valid'] = True

            meq =int(request.POST['meq'])
            instance.process_auxiliary_quantity = (meq - 100)/100 *  instance.process_quantity
            instance.save()
            #find all referencing Lca_Part and save them accordingly
            lca_parts = Lca_Part.objects.filter(lca_process_model__id=form.instance.id)
            for lca_part in lca_parts:
                lca_part.save()
        else:
            data['form_is_valid'] = False

    context = {'form': form}
    context.update({'part_name': 'Test'})
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)
