from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from EcoMan.models import Analysis, Analysis, ProjectUser_EcoMan_Ref
from ConceptMan.models import Concept, Project_ConceptMan_Ref, ProjectUser_ConceptMan_Ref, Vehicle_ConceptMan_Ref
from django.contrib.auth.models import User
from EcoMan.scripts import *
from website.scripts import *
from django.urls import reverse
#analysis-----------------------------------------------------------------------------------
def analysis_create_save_form(request, form, template_name, redirect = False):
    '''This function will save modal form of an existing object Analysis
    '''
    data = dict()
    context = dict()
    if request.method == 'POST':

        if form.is_valid():
            new_qlca =form.save()
            new_qlca.owner=get_object_or_404(ProjectUser_EcoMan_Ref, UUID = str(request.user.projectuser.UUID))
            request.user.projectuser.current_project = new_qlca.project_model.reference_project
            UUID_current_project = request.user.projectuser.current_project.UUID
            UUID_current_user = request.user.projectuser.UUID

            data['redirect'] = redirect
            data['pk'] =new_qlca.pk
            data['form_is_valid'] = True

            concept_model=Concept.objects.create(project_model = get_object_or_404(Project_ConceptMan_Ref, UUID = UUID_current_project), 
                                                      owner = get_object_or_404(ProjectUser_ConceptMan_Ref, UUID = UUID_current_user))
            new_qlca.concept_model = concept_model
            userobj = User.objects.get(id=request.user.id)
            new_qlca.concept_model.vehicles.add(get_object_or_404(Vehicle_ConceptMan_Ref, UUID = userobj.projectuser.sandbox_vehicle.UUID))

            new_qlca.concept_model.name = form.cleaned_data['name']
            new_qlca.name = form.cleaned_data['name']

            from EcoMan.forms import Analysis_Settings
            analysis_settings = Analysis_Settings.objects.create(name=(new_qlca.name + " settings"))
            analysis_settings.is_public = form.cleaned_data['is_public']
            analysis_settings.is_automotive = form.cleaned_data['is_automotive']
            analysis_settings.weight_units = form.cleaned_data['weight_units']
            analysis_settings.weight_decimal_points = form.cleaned_data['weight_decimal_points']
            analysis_settings.is_playground = False
            if not analysis_settings.is_automotive:
                analysis_settings.include_circularity = False
                analysis_settings.include_utilisation = False    
            analysis_settings.save()
            new_qlca.analysis_settings = analysis_settings

            if(form.cleaned_data.get('logo')):
                new_qlca.logo = form.cleaned_data.get('logo')
            new_qlca.save()
            data['redirect_address'] = reverse('EcoMan:analysis_detail_view', kwargs={'pk': new_qlca.id})
        else:
            data['form_is_valid'] = False
    context.update({'form': form})
    data['html_form'] = render_to_string(template_name, context, request=request),
    return JsonResponse(data)

def analysis_update_save_form(request, form, template_name, redirect = False):
    '''This function will save modal form of an existing object Analysis
    '''
    data = dict()
    context = dict()
    if request.method == 'POST':
        if form.is_valid():
            new_qlca = form.save()
            new_qlca.analysis_settings.is_public = form.cleaned_data['is_public']
            new_qlca.analysis_settings.is_automotive = form.cleaned_data['is_automotive']
            new_qlca.analysis_settings.include_upstream = form.cleaned_data['include_upstream']
            new_qlca.analysis_settings.include_core = form.cleaned_data['include_core']
            new_qlca.analysis_settings.include_downstream = form.cleaned_data['include_downstream']
            new_qlca.analysis_settings.include_circularity = form.cleaned_data['include_circularity']
            new_qlca.analysis_settings.include_utilisation = form.cleaned_data['include_utilisation']
            new_qlca.analysis_settings.weight_units = form.cleaned_data['weight_units']
            new_qlca.analysis_settings.weight_decimal_points = form.cleaned_data['weight_decimal_points']


            if not new_qlca.analysis_settings.is_automotive:
                new_qlca.analysis_settings.include_circularity = False
                new_qlca.analysis_settings.include_utilisation = False      
            new_qlca.analysis_settings.save()
            new_qlca.concept_model.name = form.cleaned_data['name']
            if(form.cleaned_data.get('logo')):
                new_qlca.logo = form.cleaned_data.get('logo')

            new_qlca.save()
            data['form_is_valid'] = True

        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request),
    return JsonResponse(data)

def analysis_create(request):
    from EcoMan.forms import AnalysisCreateForm
    if request.method == 'POST':
        form = AnalysisCreateForm(request.POST, request.FILES)
    else:
        form = AnalysisCreateForm()
        authorised_projects = request.user.projectuser.authorised_projects.all()
        new_list = []
        for project in authorised_projects:
            new_list.append( (str(project.UUID), project.name + " Owner: " + project.owner.username + " ID: " + str(project.UUID)  ))
        form.fields['project_model'].widget.choices = new_list
        form.fields['project_model'].initial = str(request.user.projectuser.current_project.UUID)
    return analysis_create_save_form(request, form, 'modals/analysis/analysis_create_modal.html', redirect=False)

def analysis_create_and_edit(request):
    from EcoMan.forms import AnalysisCreateForm
    if request.method == 'POST':
        form = AnalysisCreateForm(request.POST, request.FILES)
    else:
        form = AnalysisCreateForm()
        authorised_projects = request.user.projectuser.authorised_projects.all()
        new_list = []
        for project in authorised_projects:
            if project.owner:
                new_list.append((str(str(project.UUID)), project.name + " Owner: " + project.owner.username + " ID: " + str(project.UUID)))
            else:
                new_list.append((str(str(project.UUID)), project.name + " Owner: No Owner" + " ID: " + str(project.UUID)))    
        form.fields['project_model'].widget.choices = new_list
        form.fields['project_model'].initial = str(request.user.projectuser.current_project.UUID)
    return analysis_create_save_form(request, form, 'modals/analysis/analysis_create_modal.html', redirect=True) #redirect site in analysis.js

def analysis_update(request, pk):
    analysis = get_object_or_404(Analysis, pk=pk)
    from EcoMan.forms import AnalysisEditForm
    if request.method == 'POST':
        form = AnalysisEditForm(request.POST, request.FILES, instance=analysis)
    else:
        form = AnalysisEditForm( instance=analysis)
    return analysis_update_save_form(request, form, 'modals/analysis/analysis_update_modal.html')

def analysis_report_update(request, pk):
    analysis = get_object_or_404(Analysis, pk=pk)
    from EcoMan.forms import AnalysisEditForm
    if request.method == 'POST':
        form = AnalysisEditForm(request.POST, request.FILES, instance=analysis)
    else:
        form = AnalysisEditForm( instance=analysis)
    return analysis_report_update_save_form(request, form, 'modals/analysis/analysis_report_update_modal.html')

def analysis_report_update_save_form(request, form, template_name):
    '''This function will save modal form of an existing object Analysis
    '''
    data = dict()
    context = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True

        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request),
    return JsonResponse(data)

def analysis_delete(request, pk):
    analysis= get_object_or_404(Analysis, pk=pk)
    data = dict()
    if request.method == 'POST':
        analysis.delete()
        data['form_is_valid'] = True  # This is just to play along with the existing code

    else:
        context = {'analysis': analysis}
        data['html_form'] = render_to_string('modals/analysis/analysis_delete_modal.html',
            context,
            request=request,
        )
    return JsonResponse(data)


def analysis_settings_update(request, pk):
    qlca = get_object_or_404(Analysis, pk=pk)
    from EcoMan.forms import AnalysisReportEditForm
    if request.method == 'POST':
        form = AnalysisReportEditForm(request.POST, instance=qlca)
    else:
        form = AnalysisReportEditForm( instance=qlca)
    return analysis_settings_update_save_form(request, form, 'modals/analysis/analysis_report_update_modal.html')

def analysis_settings_update_save_form(request, form, template_name):
    '''This function will save modal form of an existing object Analysis
    '''
    data = dict()
    context = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            settings_list  = form.instance.analysis_settings.as_list()

            settings = form.instance.analysis_settings
            for f in settings._meta.fields:
                    if "report_" in f.name:
                            setattr(settings, f.name, False)
                            setting = request.POST.get(f.name)
                            if setting == 'on':
                                setattr(settings, f.name, True)
            settings.save()            
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request),
    return JsonResponse(data)