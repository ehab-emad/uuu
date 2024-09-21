from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from EcoMan.models import Analysis, Analysis_Comparison, ProjectUser_EcoMan_Ref
from ConceptMan.models import Concept, Project_ConceptMan_Ref, ProjectUser_ConceptMan_Ref, Vehicle_ConceptMan_Ref
from django.contrib.auth.models import User
from EcoMan.scripts import *
from website.scripts import *
from django.urls import reverse
#qlca-----------------------------------------------------------------------------------
def qlca_create_save_form(request, form, template_name, redirect = False):
    '''This function will save modal form of an existing object Analysis_Comparison
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

            new_qlca.save()
            data['redirect'] = redirect
            data['pk'] =new_qlca.pk
            data['form_is_valid'] = True
            analysis_left = Analysis.objects.create(project_model = new_qlca.project_model, owner = new_qlca.owner)
            analysis_right = Analysis.objects.create(project_model = new_qlca.project_model, owner = new_qlca.owner)

            concept_model_left=Concept.objects.create(project_model = get_object_or_404(Project_ConceptMan_Ref, UUID = UUID_current_project), 
                                                      owner = get_object_or_404(ProjectUser_ConceptMan_Ref, UUID = UUID_current_user))
            concept_model_right=Concept.objects.create(project_model = get_object_or_404(Project_ConceptMan_Ref, UUID = UUID_current_project), 
                                                      owner = get_object_or_404(ProjectUser_ConceptMan_Ref, UUID = UUID_current_user))
            analysis_left.concept_model = concept_model_left
            analysis_right.concept_model = concept_model_right
            userobj = User.objects.get(id=request.user.id)
            analysis_left.concept_model.vehicles.add(get_object_or_404(Vehicle_ConceptMan_Ref, UUID = userobj.projectuser.sandbox_vehicle.UUID))
            analysis_right.concept_model.vehicles.add(get_object_or_404(Vehicle_ConceptMan_Ref, UUID = userobj.projectuser.sandbox_vehicle.UUID))

            if form.cleaned_data['name_concept_left']:
                analysis_left.concept_model.name = form.cleaned_data['name_concept_left']
                analysis_left.name = form.cleaned_data['name_concept_left']

            if form.cleaned_data['name_concept_right']:
                analysis_right.concept_model.name = form.cleaned_data['name_concept_right']
                analysis_right.name = form.cleaned_data['name_concept_right']
            from EcoMan.forms import Analysis_Settings
            analysis_settings = Analysis_Settings.objects.create(name=(new_qlca.name + " settings"))
            analysis_settings.is_public = form.cleaned_data['is_public']
            analysis_settings.is_automotive = form.cleaned_data['is_automotive']
            if not analysis_settings.is_automotive:
                analysis_settings.include_circularity = False
                analysis_settings.include_utilisation = False  
            analysis_settings.weight_units = form.cleaned_data['weight_units']
            analysis_settings.weight_decimal_points = form.cleaned_data['weight_decimal_points']
            analysis_settings.save()
            analysis_left.save()
            analysis_right.save()
            concept_model_left.save()
            concept_model_right.save()

            new_qlca.analysis_left = analysis_left
            new_qlca.analysis_left.analysis_settings.weight_units = form.cleaned_data['weight_units']
            new_qlca.analysis_left.analysis_settings.save()
            new_qlca.analysis_right = analysis_right
            new_qlca.analysis_right.analysis_settings.weight_units = form.cleaned_data['weight_units']
            new_qlca.analysis_right.analysis_settings.save()
            new_qlca.analysis_settings = analysis_settings
            new_qlca.playground = True
            if(form.cleaned_data.get('logo')):
                new_qlca.logo = form.cleaned_data.get('logo')
            new_qlca.save()

            #data['redirect_address'] = request.build_absolute_uri('/eco/qlca/' + new_qlca.id + '/playgrounddetail/')
            data['redirect_address'] = reverse('EcoMan:analysis_comparison_detail_view', kwargs={'pk': new_qlca.id})
        else:
            data['form_is_valid'] = False
    context.update({'form': form})
    data['html_form'] = render_to_string(template_name, context, request=request),
    return JsonResponse(data)

def qlca_update_save_form(request, form, template_name, redirect = False):
    '''This function will save modal form of an existing object Analysis_Comparison
    '''
    data = dict()
    context = dict()
    if request.method == 'POST':
        if form.is_valid():
            new_qlca = form.save()
            if form.cleaned_data['name_concept_left']:
                new_qlca.analysis_left.concept_model.name = form.cleaned_data['name_concept_left']
                new_qlca.analysis_left.name = form.cleaned_data['name_concept_left']

                new_qlca.analysis_left.concept_model.save()
                new_qlca.analysis_left.save()
                new_qlca.analysis_left.analysis_settings.weight_units = form.cleaned_data['weight_units']
                new_qlca.analysis_left.analysis_settings.save()

            if form.cleaned_data['name_concept_right']:
                new_qlca.analysis_right.concept_model.name = form.cleaned_data['name_concept_right']
                new_qlca.analysis_right.name = form.cleaned_data['name_concept_right']
                
                new_qlca.analysis_right.concept_model.save()
                new_qlca.analysis_right.save()
                new_qlca.analysis_right.analysis_settings.weight_units = form.cleaned_data['weight_units']
                new_qlca.analysis_right.analysis_settings.save()

            new_qlca.analysis_settings.is_public = form.cleaned_data['is_public']
            new_qlca.analysis_settings.is_playground = form.cleaned_data['is_playground']
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

            new_qlca.save()
            data['form_is_valid'] = True

        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request),
    return JsonResponse(data)

def analysis_comparison_create(request):
    from EcoMan.forms import AnalysisComparisonCreateForm
    if request.method == 'POST':
        form = AnalysisComparisonCreateForm(request.POST, request.FILES)
    else:
        form = AnalysisComparisonCreateForm()
    if request.user.is_authenticated == True:
        #user can only select project for which he has access
        authorised_projects = request.user.projectuser.authorised_projects.all()
        new_list = []
        for project in authorised_projects:
            new_list.append((str(str(project.UUID)), project.name + " Owner: " + project.owner.username + " ID: " + str(project.UUID)))
        form.fields['project_model'].widget.choices = new_list
        form.fields['project_model'].initial = str(request.user.projectuser.current_project.UUID)
    return qlca_create_save_form(request, form, 'modals/analysis_comparison/analysis_comparison_create_modal.html', redirect=False)

def analysis_comparison_create_and_edit(request):
    from EcoMan.forms import AnalysisComparisonCreateForm
    if request.method == 'POST':
        form = AnalysisComparisonCreateForm(request.POST, request.FILES)
    else:
        form = AnalysisComparisonCreateForm()
    if request.user.is_authenticated == True:
        #user can only select project for which he has access
        authorised_projects = request.user.projectuser.authorised_projects.all()
        new_list = []
        for project in authorised_projects:
            if project.owner:
                new_list.append((str(str(project.UUID)), project.name + " Owner: " + project.owner.username + " ID: " + str(project.UUID)))
                
            else:
                new_list.append((str(str(project.UUID)), project.name + " Owner: " + "Unknown" + " ID: " + str(project.UUID)))               
        form.fields['project_model'].widget.choices = new_list
        form.fields['project_model'].initial = str(request.user.projectuser.current_project.UUID)
    else:
        form.fields['project_model'].choices=[]
    return qlca_create_save_form(request, form, 'modals/analysis_comparison/analysis_comparison_create_modal.html', redirect=True) #redirect site in qlca.js

def analysis_comparison_update(request, pk):
    qlca = get_object_or_404(Analysis_Comparison, pk=pk)
    from EcoMan.forms import AnalysisComparisonEditForm
    if request.method == 'POST':
        form = AnalysisComparisonEditForm(request.POST, request.FILES, instance=qlca)
    else:
        form = AnalysisComparisonEditForm( instance=qlca)
    return qlca_update_save_form(request, form, 'modals/analysis_comparison/analysis_comparison_update_modal.html')

def analysis_comparison_report_update(request, pk):
    qlca = get_object_or_404(Analysis_Comparison, pk=pk)
    from EcoMan.forms import AnalysisComparisonReportEditForm
    if request.method == 'POST':
        form = AnalysisComparisonReportEditForm(request.POST, request.FILES, instance=qlca)
    else:
        form = AnalysisComparisonReportEditForm( instance=qlca)
    return qlca_report_update_save_form(request, form, 'modals/analysis_comparison/analysis_comparison_report_update_modal.html')

def qlca_report_update_save_form(request, form, template_name):
    '''This function will save modal form of an existing object Analysis_Comparison
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

def analysis_comparison_delete(request, pk):
    qlca_analysis = get_object_or_404(Analysis_Comparison, pk=pk)
    data = dict()
    if request.method == 'POST':
        qlca_analysis.delete()
        data['form_is_valid'] = True  # This is just to play along with the existing code

    else:
        context = {'qlca_analysis': qlca_analysis}
        data['html_form'] = render_to_string('modals/analysis_comparison/analysis_comparison_delete_modal.html',
            context,
            request=request,
        )
    return JsonResponse(data)