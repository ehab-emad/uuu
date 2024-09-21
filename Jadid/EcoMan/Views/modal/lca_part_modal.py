from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from EcoMan.models import Analysis, Project_EcoMan_Ref, ProjectUser_EcoMan_Ref
from EcoMan.models import Lca_Part
from ConceptMan.models import Part, ProjectUser_ConceptMan_Ref


#qlca-----------------------------------------------------------------------------------
def lca_part_save_form(request, form, template_name, pk_analysis = None, weight_unit = None, is_automotive = False):
    data = dict()
    context = dict()
    if request.method == 'POST':
        if form.is_valid():

            lca_part = form.save()
            if lca_part.part_model:
                part = lca_part.part_model
            else:
                part = Part()
            part.owner = get_object_or_404(ProjectUser_ConceptMan_Ref, UUID=request.user.projectuser.UUID)
            part.weight = float(request.POST['part_weight'])
            if weight_unit == 'GRAMS':
                # Check if part_weight is not zero or None, and then perform the division
                if part.weight and float(part.weight) != 0:
                    part.weight = float(part.weight) / 1000
                else:
                    # Handle the zero or invalid weight case, e.g., by setting a default value or raising an error
                    part.weight = 0  
            part.name = request.POST['name']
            if(form.cleaned_data.get('part_image')):
                part.logo = form.cleaned_data.get('part_image')
            part.save()
            lca_part.part_model = part
            lca_part.project_model =  get_object_or_404(Project_EcoMan_Ref, UUID=request.user.projectuser.current_project.UUID)
            lca_part.owner = get_object_or_404(ProjectUser_EcoMan_Ref, UUID=request.user.projectuser.UUID)
            lca_part.save()
            if pk_analysis:   #if lca part should be added to analysis
                analysis = Analysis.objects.get(pk=pk_analysis)
                analysis.lca_part_models.add(lca_part)
                analysis.save()
                concept_left = analysis.concept_model
                concept_left.parts.add(part)
                concept_left.save()

            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    context.update({'pk_analysis':pk_analysis})
    context.update({'weight_unit':weight_unit})
    context.update({'is_automotive':is_automotive})
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)


def lca_part_create_modal(request, pk_analysis = None, is_automotive = 'False',  weight_unit ='KILOGRAMS'):
    is_automotive = is_automotive.lower() in ('true')
    from EcoMan.forms import LcaPartForm
    if request.method == 'POST':
        form = LcaPartForm(request.POST, request.FILES, weight_unit = weight_unit, is_automotive = is_automotive)
    else:
        form = LcaPartForm(weight_unit = weight_unit, is_automotive = is_automotive)
    return lca_part_save_form(request, form, 'modals/lca_part/lca_part_create_modal.html', pk_analysis, weight_unit, is_automotive)



def lca_part_update(request, pk, is_automotive = 'False', weight_unit ='KILOGRAMS'):
    is_automotive = is_automotive.lower() in ('true')
    lca_part = get_object_or_404(Lca_Part, pk=pk)
    from EcoMan.forms import LcaPartForm
    if request.method == 'POST':
        form = LcaPartForm(request.POST, request.FILES, instance=lca_part, weight_unit = weight_unit, is_automotive = is_automotive)
    else:
        form = LcaPartForm(instance=lca_part, weight_unit = weight_unit, is_automotive = is_automotive)
    return lca_part_save_form(request, form, 'modals/lca_part/lca_part_update_modal.html', is_automotive = False, weight_unit = weight_unit)

def lca_part_delete(request, pk):
    lca_part = get_object_or_404(Lca_Part, pk=pk)
    data = dict()
    if request.method == 'POST':
        lca_part.part_model.delete()
        lca_part.delete()
        data['form_is_valid'] = True 
    else:
        context = {'part': lca_part}
        data['html_form'] = render_to_string('modals/lca_part/lca_part_delete_modal.html',
            context,
            request=request,
        )
    return JsonResponse(data)

