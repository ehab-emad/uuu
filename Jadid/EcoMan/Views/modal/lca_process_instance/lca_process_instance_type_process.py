from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.http import JsonResponse
from EcoMan.models import Lca_Part
from ConceptMan.models import Part
from EcoMan.models import Instance_Idemat_Database_Process


def processing_process_instance_update(request, pk_instance,   weight_unit = None, weight_decimals = 3):
    '''
    View function allowing edit of Processing Instance
    '''
    instance_lca_process = get_object_or_404(Instance_Idemat_Database_Process, pk=pk_instance)
    lca_part = Lca_Part.objects.filter(lca_process_model = pk_instance).get()
    part =  lca_part.part_model
    from EcoMan.forms import ProcessingProcessInstanceUpdateForm
    if request.method == 'POST':
        form = ProcessingProcessInstanceUpdateForm(request.POST, instance=instance_lca_process, weight_unit= weight_unit)

    if request.method == 'GET':  

        #calculate meq
        if float(instance_lca_process.process_quantity) == 0:
            meq = 100
        else:
            meq = float(100 + instance_lca_process.process_auxiliary_quantity / instance_lca_process.process_quantity*100)
        initial_dict={'meq': meq , 
                        'part_id': part.id,
                        'part_name': part.name,
                        'part_weight': f"{part.get_weight_in_units(weight_unit):.{weight_decimals}f}",    
                        'part_area': part.area,
                        'process_name':instance_lca_process.process_model.name ,
                        'process_unit':instance_lca_process.process_model.unit ,                        
                         }
        form = ProcessingProcessInstanceUpdateForm(instance=instance_lca_process, initial = initial_dict, weight_unit= weight_unit )
    html_template = 'modals/instance_idemat_process/process_instance_idemat_process_update_modal.html'
    return save_form(request, form, html_template, part, weight_unit, weight_decimals )

def save_form(request, form, template_name, part,  weight_unit ='KILOGRAMS', weight_decimals = 3):
    data = dict()
    context = dict()
    if request.method == 'POST':
        if form.is_valid():
            instance=form.save()
            data['form_is_valid'] = True

            meq =float(request.POST['meq'])
            instance.process_auxiliary_quantity = (meq - 100)/100 *  instance.process_quantity
            instance.save()
            #find all referencing Lca_Part and save them accordingly
            lca_parts = Lca_Part.objects.filter(lca_process_model__id=form.instance.id)
            for lca_part in lca_parts:
                lca_part.save()
        else:
            data['form_is_valid'] = False

    context = {'form': form}
    context.update({'part': part}) 
    context.update({'weight_unit': weight_unit})
    context.update({'weight_decimals': weight_decimals})    
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)
