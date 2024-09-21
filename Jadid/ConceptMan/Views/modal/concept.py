from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

#Concept-----------------------------------------------------------------------------------
def concept_save_form(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            new_concept =form.save()
            if request.user.is_authenticated == True:
                new_concept.user=request.user
            new_concept.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request),
    return JsonResponse(data)

def concept_create(request):
    if request.method == 'POST':
        from ConceptMan.forms import ConceptForm
        form = ConceptForm(request.POST)
    else:
        form = ConceptForm()
    return concept_save_form(request, form, 'modals/concept/concept_create_modal.html')

def concept_update(request, pk):
    from ConceptMan.models import Concept
    concept = get_object_or_404(Concept, pk=pk)
    if request.method == 'POST':
        from ConceptMan.forms import ConceptForm
        form = ConceptForm(request.POST, instance=concept)
    else:
        form = ConceptForm(instance=concept)
    return concept_save_form(request, form, 'modals/concept/concept_update_modal.html')

def concept_delete(request, pk):
    from ConceptMan.models import Concept
    concept = get_object_or_404(Concept, pk=pk)
    data = dict()
    if request.method == 'POST':
        concept.delete()
        data['form_is_valid'] = True  # This is just to play along with the existing code
    else:
        context = {'concept': concept}
        data['html_form'] = render_to_string('modals/concept/concept_delete_modal.html',
            context,
            request=request,
        )
    return JsonResponse(data)
