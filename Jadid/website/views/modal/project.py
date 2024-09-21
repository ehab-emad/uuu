from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from website.forms import *
from functools import reduce
from django.db.models import Q
#from EcoMan.models import ProjectUser
#project-----------------------------------------------------------------------------------
def project_save_form(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            project = form.save()
            if(form.cleaned_data.get('logo')):
                project.logo = form.cleaned_data.get('logo')
                project.save()
            if request.user:
                project.owner = request.user
                project.save()
                request.user.projectuser.authorised_projects.add(project)
                request.user.projectuser.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False

    context = {'form': form}
    'query has to deliver all project users which are active project members'
    current_project_object =  request.user.projectuser.current_project
    context['authorised_users']=ProjectUser.objects.filter(Q(authorised_projects = current_project_object)& ~Q(user__username__icontains = "anonymous"))    
    #context['authorised_users'] = ProjectUser.objects.filter(authorised_projects = current_project_object).filter(~Q(authorised_projects__name = "Organisation_LCA_Project"))
    data['html_form'] = render_to_string(template_name, context, request=request),
    return JsonResponse(data)

def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        
    else:
        form = ProjectForm()
    return project_save_form(request, form, 'modals/project/project_create_modal.html')

def project_update(request, uuid, **kwargs):
    project = get_object_or_404(Project, pk=uuid)
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
    else:
        form = ProjectForm(instance=project)
    return project_save_form(request, form, 'modals/project/project_update_modal.html')

def project_delete(request, uuid):
    project = get_object_or_404(project, pk=uuid)
    data = dict()
    if request.method == 'POST':
        project.delete()
        data['form_is_valid'] = True  # This is just to play along with the existing code
    else:
        context = {'project': project}
        data['html_form'] = render_to_string('modals/project/project_delete_modal.html',
            context,
            request=request,
        )
    return JsonResponse(data)


def project_update_authorised_users(request, uuid ):
    project = get_object_or_404(Project, pk=uuid)
    if request.method == 'POST':
        form = ProjectSelectAuthForm(request.POST, instance=project)
    else:
        form = ProjectSelectAuthForm(instance=project)

    return project_save_form(request, form, 'modals/project/project_update_authorised_users.html')


def load_project_users(request):
    '''View used to reload dropdown list during addition of idemat material process
    '''
    if request.method == 'POST':

        trigger_id = request.POST['trigger_id']
    else:
        trigger_id = request.GET['trigger_id']

    if request.method == 'GET' and 'project_user_id' in request.GET:
        project_user_id = request.GET['project_user_id'].strip()
    else:
        project_user_id = ''
    context={}

   #template part search  (ul -> li option) was selected
    if trigger_id == 'option_submit':

        project_user_object = get_object_or_404(ProjectUser, UUID=project_user_id)
        project_user_object.authorised_projects.add (Project.objects.filter(UUID = request.user.projectuser.current_project.UUID).get())
        project_user_object.save()
        current_project_object =  request.user.projectuser.current_project
        #get all users which have project of user in request
        context['authorised_users']=ProjectUser.objects.filter(Q(authorised_projects = current_project_object)& ~Q(user__username__icontains = "anonymous"))
        data={}
        data['html_template_preview'] =render_to_string('modals/project/project_update_authorised_users/project_authorised_users_modal_content.html', context, request=request)

        return JsonResponse(data)

   #Button search was pressed
    if trigger_id == 'search_submit':
        search_text = request.GET['search_text']
        project_user_query = ProjectUser.objects.all()
        project_user_query = project_user_query.filter(Q(user__username__icontains=search_text) & ~Q(user__username__icontains = "anonymous"))
        context['search_result']=project_user_query
        data={}
        data['html_templates_preview'] =render_to_string('modals/project/project_update_authorised_users/project_authorised_users_modal_content.html', context, request=request)

        return JsonResponse(data)


    if trigger_id == 'remove_selected':
        current_project_object =  request.user.projectuser.current_project
        #get all users which have project of user in request
        context['authorised_users']=ProjectUser.objects.filter(authorised_projects = current_project_object )
        #extract the key, value pairs with checkbox in name
        POST_dict = request.GET.dict()
        POST_dict_filtered = {k:v for (k,v) in POST_dict.items() if 'checkbox' in k}

        for checkbox in POST_dict_filtered.items():
            ProjectUserObject = ProjectUser.objects.filter(UUID = checkbox[1]).get()
            if ProjectUserObject.UUID != current_project_object.owner.projectuser.UUID:
                ProjectUserObject.authorised_projects.remove(current_project_object)
                ProjectUserObject.save()
        #refresh context
        context['authorised_users']=ProjectUser.objects.filter(Q(authorised_projects = current_project_object)& ~Q(user__username__icontains = "anonymous"))
        data={}
        data['html_templates_preview'] =render_to_string('modals/project/project_update_authorised_users/project_authorised_users_modal_content.html', context, request=request)

        return JsonResponse(data)