from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from website.forms import *
from functools import reduce
from website.models import ProjectUser


#project_user-----------------------------------------------------------------------------------
def project_user_save_form(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            #check additional information in request
            if request.POST.get('email'):
                form.instance.user.email = request.POST.get('email')
                form.instance.user.save()
            project_user = form.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request),
    return JsonResponse(data)

def project_user_select_current_project(request, uuid ):
    project_user = ProjectUser.objects.get(UUID = uuid)
    if request.method == 'POST':
        form = ProjectUserSelectProjectForm(request.POST, instance=project_user)
    else:
        form = ProjectUserSelectProjectForm( instance=project_user)
    return project_user_save_form(request, form, 'modals/project_user/project_user_select_current_project_modal.html')


def project_user_update(request, uuid ):
    project_user = ProjectUser.objects.get(UUID = uuid)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project_user)
    else:
        form = ProjectForm(instance=project_user)

    return project_user_save_form(request, form, 'modals/project_user/project_user_update_modal.html')




