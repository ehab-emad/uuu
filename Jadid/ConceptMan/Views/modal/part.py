from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ConceptMan.forms import PartForm
from functools import reduce
from ConceptMan.models import Part
#Part-----------------------------------------------------------------------------------
def part_save_form(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            new_part =form.save()
            if request.user.is_authenticated == True:
                new_part.user=request.user
            new_part.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request),
    return JsonResponse(data)

def part_create(request):
    if request.method == 'POST':
        form = PartForm(request.POST)
    else:
        form = PartForm()
    return part_save_form(request, form, 'modals/part/part_create_modal.html')

def part_update(request, pk):
    part = get_object_or_404(Part, pk=pk)
    if request.method == 'POST':
        form = PartForm(request.POST, instance=part)
    else:
        form = PartForm(instance=part)
    return part_save_form(request, form, 'modals/part/part_update_modal.html')

def part_delete(request, pk):
    part = get_object_or_404(Part, pk=pk)
    data = dict()
    if request.method == 'POST':
        part.delete()
        data['form_is_valid'] = True  # This is just to play along with the existing code
    else:
        context = {'part': part}
        data['html_form'] = render_to_string('modals/part/part_delete_modal.html',
            context,
            request=request,
        )
    return JsonResponse(data)
