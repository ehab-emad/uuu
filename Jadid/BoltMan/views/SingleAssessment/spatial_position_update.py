from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404


from BoltMan.models import Spatial_Position



def spatial_position_update(request):

    spatial_position_uuid = request.POST.get('workflow_id',None)
    spatial_position = get_object_or_404(Spatial_Position, UUID=spatial_position_uuid)
    from BoltMan.forms import spatial_position_form
    if request.method == 'POST':
        form = spatial_position_form(request.POST, request.FILES, instance=spatial_position)
    return spatial_position_update_save_form(request, form, 'modals/SingleAssessment/assessment_detail_view/position.html')


def spatial_position_update_save_form(request, form, template_name):
    data = dict()
    context = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    context = {'form_spatial_position': form}
    data['html_form'] = render_to_string(template_name, context, request=request),
    return JsonResponse(data)


