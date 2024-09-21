from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from EcoMan.models import Lca_Part
from EcoMan.models import Analysis
from django.db.models import Q

def lca_part_add_from_template(request, pk_analysis):
    '''Add Part from a template
    '''
    analysis = get_object_or_404(Analysis, pk=pk_analysis )
    from EcoMan.forms import Lca_Part_Add_From_Template_Form
    if request.method == 'POST':
        form = Lca_Part_Add_From_Template_Form(instance=analysis)
    else:
        form = Lca_Part_Add_From_Template_Form(instance = analysis)

    return lca_part_from_template_save_form(request, form, 'modals/lca_part_from_template/lca_part_add_from_template.html')

#lcastep_save_form-----------------------------------------------------------------------------------
def lca_part_from_template_save_form(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        analysis = get_object_or_404(Analysis, pk=form.instance.id)
        lca_part_template =get_object_or_404(Lca_Part, pk=request.POST.get('selected_template_id'))

        #before lca_part will be cloned we have to generate a list of processes which shouldnt be cloned
        POST_dict = request.POST.dict()

        #extract the key, value pairs with checkbox in name
        POST_dict_filtered = {k:v for (k,v) in POST_dict.items() if 'checkbox' in k}
        process_dict = {}
        for object in lca_part_template.lca_process_model.all():
            process_dict['checkbox_' + object.id] = object.id

        common_values = set(POST_dict_filtered.values()) & set(process_dict.values())

        dict1_substrakt_dict2 = {key: value for key, value in process_dict.items() if value not in common_values}

        new_lca_part = lca_part_template.clone_it(exclude_processes = list(dict1_substrakt_dict2.values()))
        new_lca_part.name = request.POST.get('part_name')
        new_lca_part.part_model.name = new_lca_part.name
        new_lca_part.part_model.save()
        new_lca_part.part_model.weight = lca_part_template.part_model.weight
        new_lca_part.part_model.multiplier = 1

        new_lca_part.save()

        #add new part to the analysis
        analysis.lca_part_models.add(new_lca_part)
        analysis.save()
        data['form_is_valid'] = True
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request),
    return JsonResponse(data)

def load_templates(request):
    '''View used to reload dropdown list during addition of idemat material process
    '''

    trigger_id = request.GET['trigger_id']

    if request.method == 'GET' and 'lca_part_source' in request.GET:
        lca_part_source = int(request.GET['lca_part_source'].strip() or 0)
    else:
        lca_part_source = 0

    if request.method == 'GET' and 'lca_part_template_id' in request.GET:
        lca_part_template_id = int(request.GET['lca_part_template_id'].strip() or 0)
    else:
        lca_part_template_id = 0
    context={}

   #template part search  (ul -> li option) was selected
    if trigger_id == 'option_submit':

        lca_part_template_object = get_object_or_404(Lca_Part, pk=lca_part_template_id)
        context['selected_template_preview']=lca_part_template_object
        data={}
        data['selected_template_id'] = lca_part_template_object.id
        data['selected_template_name'] = lca_part_template_object.name
        data['selected_template_notes'] = lca_part_template_object.notes
  
        data['html_template_preview'] =render_to_string('modals/lca_part_from_template/lca_part_preview_modal_content.html', context, request=request)

        return JsonResponse(data)

   #Button search was pressed
    if trigger_id == 'search_submit':
        search_text = request.GET['search_text']

        if lca_part_source ==1:
            #current Project
            process_query = Lca_Part.objects.filter(Q(istemplate = True) & Q(project_model_id = request.user.projectuser.current_project.UUID))  

        if lca_part_source ==2:
            #EDAG LCA Part Template Database
            process_query = Lca_Part.objects.filter(Q(istemplate = True) & Q(project_model_id = request.user.projectuser.current_project.UUID))  



        process_query = process_query.filter(name__icontains=search_text)  
        context['search_result']=process_query     
        data={}        
        data['html_templates_preview'] =render_to_string('modals/lca_part_from_template/lca_part_preview_modal_content.html', context, request=request)

        return JsonResponse(data)
