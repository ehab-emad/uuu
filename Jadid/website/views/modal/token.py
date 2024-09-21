from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from website.forms import TokenForm
from website.models import Token, ProjectUser
#Vehicle-----------------------------------------------------------------------------------

def token_save_form(request, form, template_name, uuid_component):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            new_token =form.save()
            new_token.owner=request.user
            new_token.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    context['uuid_component'] = uuid_component

    'query has to deliver all project users which are within current organisation'



    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)

def token_create_modal(request, uuid_component):
    projectusers = ProjectUser.objects.all()
    if request.method == 'POST':
        form = TokenForm(request.POST)
    else:
        form = TokenForm(projectusers = projectusers)
    return token_save_form(request, form, 'modals/token/create_modal.html', uuid_component)

def token_update(request, uuid):
    token = get_object_or_404(Token, pk=uuid)
    projectusers = ProjectUser.objects.all()
    if request.method == 'POST':
        form = TokenForm(request.POST, instance=token)
    else:
        form = TokenForm(projectusers = projectusers)
    return token_save_form(request, form, 'modals/token/update_modal.html')

def token_delete(request, uuid):
    token = get_object_or_404(Token, pk=uuid)
    data = dict()
    if request.method == 'POST':
        token.delete()
        data['form_is_valid'] = True  # This is just to play along with the existing code     
    else:
        context = {'token': token}
        data['html_form'] = render_to_string('modals/token/delete_modal.html',
            context,
            request=request,
        )
    return JsonResponse(data)