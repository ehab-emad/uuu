

from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from EcoMan.models import Analysis_Comparison, Analysis, Analysis_Settings, ProjectUser_EcoMan_Ref
from ConceptMan.models import Concept
from django.urls import reverse
import json

def create_new_analysis_comparison(name,project_model, user, json_file):

   analysis = Analysis_Comparison.objects.create(name=name, project_model=project_model)

   #concept_left
   concept_left= Concept.objects.create(project_model=project_model)
   concept_left.save()
   concept_left.vehicles.add(user.projectuser.sandbox_vehicle)
   concept_left.save()

   #concept_right
   concept_right= Concept.objects.create(project_model=project_model)
   concept_right.save()
   concept_right.vehicles.add(user.projectuser.sandbox_vehicle)
   concept_right.save()

   #analysis_left
   analysis_left= Analysis()
   analysis_left.owner = user
   analysis_left.project_model = project_model
   analysis_left.concept_model = concept_left
   analysis_left.save()
   analysis.analysis_left = analysis_left

   #analysis_right
   analysis_right= Analysis()
   analysis_right.owner = user
   analysis_right.project_model = project_model
   analysis_right.concept_model = concept_right
   analysis_right.save()
   analysis.analysis_right = analysis_right

   analysis.analysis_settings = Analysis_Settings()
   analysis.analysis_settings.save()

   analysis.save()
   return analysis


def import_json_save_form(request, form, template_name, redirect = False):
   data = dict()
   context = dict()
   if request.method == 'POST':
      if form.is_valid():

         try:
            # Import JSON data to existing analysis_comparison
            if form.cleaned_data['id']:
               analysis = form.save()

         except:
            # Import JSON to new analysis_comparison
            if form.cleaned_data['project_model'] == None:
               proj_model = request.user.projectuser.sandbox_project
            else:
               proj_model = form.cleaned_data['project_model']
            analysis = create_new_analysis_comparison(name=form.cleaned_data['name'], project_model=proj_model , projectuser=request.user.projectuser)

            json_file = form.cleaned_data['JSON_file']      
            #concept_left
            concept_left= Concept.objects.create(project_model=proj_model)
            concept_left.save()
            concept_left.vehicles.add(request.user.projectuser.sandbox_vehicle)
            concept_left.save()

            #concept_right
            concept_right= Concept.objects.create(project_model=proj_model)
            concept_right.save()
            concept_right.vehicles.add(request.user.projectuser.sandbox_vehicle)
            concept_right.save()

            #analysis_left
            analysis_left= Analysis()
            analysis_left.owner = request.user
            analysis_left.project_model = proj_model
            analysis_left.concept_model = concept_left
            analysis_left.save()
            analysis.analysis_left = analysis_left

            #analysis_right
            analysis_right= Analysis()
            analysis_right.owner = request.user
            analysis_right.project_model = proj_model
            analysis_right.concept_model = concept_right
            analysis_right.save()
            analysis.analysis_right = analysis_right

            analysis.analysis_settings = Analysis_Settings()
            analysis.analysis_settings.save()

            analysis.save()

         if request.user.is_authenticated == True:
               analysis.owner=ProjectUser_EcoMan_Ref.objects.filter(UUID = request.user.projectuser.UUID).get()
         analysis.save()
         data['redirect'] = redirect
         data['redirect_address'] = reverse('EcoMan:analysis_comparison_detail_view', kwargs={'pk': analysis.id })
         data['pk'] =analysis.pk
         data['form_is_valid'] = True

         #if file uploaded try to import processes from self.last_import_document as parameter not provided
         if request.FILES:
               analysis.import_json()
      else:
         data['form_is_valid'] = False

   context = {'form': form}
   data['html_form'] = render_to_string(template_name, context, request=request),
   return JsonResponse(data)

def import_json_analysis_save_form(request, form, template_name, redirect = False):
   data = dict()
   context = dict()
   if request.method == 'POST':
      if form.is_valid():

         try:
            # Import JSON data to existing analysis_comparison
            if form.cleaned_data['id']:
               analysis = form.save()

         except:
            pass

         if request.user.is_authenticated == True:
               analysis.owner=ProjectUser_EcoMan_Ref.objects.filter(UUID = request.user.projectuser.UUID).get()
         analysis.save()
         data['redirect'] = redirect
         data['redirect_address'] = reverse('EcoMan:analysis_detail_view', kwargs={'pk': analysis.id })
         data['pk'] =analysis.pk
         data['form_is_valid'] = True

         #if file uploaded try to import processes from self.last_import_document as parameter not provided
         if request.FILES:
               json_data = json.load(request.FILES['JSON_file'])
               analysis.import_json(json_data['analysis'][0])
      else:
         data['form_is_valid'] = False

   context = {'form': form}
   data['html_form'] = render_to_string(template_name, context, request=request),
   return JsonResponse(data)

def load_json_preview(request):
   from EcoMan.forms import AnalysisComparisonImportFromJSONForm
   if request.method == 'POST':
      form = AnalysisComparisonImportFromJSONForm(request.POST, files=request.FILES,)
      json_file = request.FILES['JSON_file']

      json_data = json.load(json_file.file)
      json_data['preview'] = 'preview'
      json_data['comparison'] = json_load_process_comparison(json_data)
      return JsonResponse(json_data)

def json_load_process_comparison(json_data):

   json_preview = {}

   for part in json_data['analysis'][0]['parts'].values():
      for step_name, step_data in part['lca_part'].items():
         if(step_name == 'lca_result'):
            continue
         for process_name, process_data in step_data.items():
            if(process_name == 'lca_result'):
               continue
            from EcoMan.models import Instance_Idemat_Database_Process, Lca_Database_Process
            for item_name, item_data in process_data.items():
               if(item_name == 'lca_result'):
                     continue

               instance_process_model=Instance_Idemat_Database_Process()

               calculation_model = Lca_Database_Process()

               calculation_model.name = item_data['lca_input']['name']
               # Set all the values for calculation
               for field in instance_process_model.lca_fields:
                     setattr(calculation_model, field, item_data['lca_input'][field])

               # calculation_model.save()

               instance_process_model.calculation_model = calculation_model

               try:
                  idemat_process = Lca_Database_Process.objects.get(pk=item_data['lca_input']['id'])
                  instance_process_model.process_model=idemat_process
                  if compare_process_details(instance_process_model, idemat_process, calculation_model) == True:
                     instance_process_model.process_flag = "REF_CORRECT"
                  else:
                     instance_process_model.process_flag = "PROCESS_CHANGED"


               except Lca_Database_Process.DoesNotExist:
                  instance_process_model.process_model=calculation_model
                  instance_process_model.process_flag = "ORPH_UNIDENTIFIED"

               data_dict = {}
               for field in instance_process_model.lca_fields:
                  data_dict[field] =  {
                     'db_process'  : getattr(instance_process_model.process_model, field),
                     'json_Process' : getattr(calculation_model, field),
                     'same_value' : (getattr(calculation_model, field) == getattr(instance_process_model.process_model, field))
                  }

               json_preview[calculation_model.name] = {
                  'flag' : instance_process_model.process_flag,
                  'data' :  data_dict
               }

               # lca_part.lca_process_model.add(instance_process_model)

   # for part in json_data['analysis'][1]['parts'].values():
   #   pass

   return json_preview

def compare_process_details(instance, model, calc_model):

        is_equal = True

        # Check all the calculation fields
        for field in instance.lca_fields:
            is_equal &= (getattr(calc_model, field) == getattr(model, field))

        return is_equal

def json_import_analysis_comparison_append(request, pk_analysis_comparison):
    analysis = get_object_or_404(Analysis_Comparison, pk=pk_analysis_comparison)
    from EcoMan.forms.import_json import ImportJsonForm
    if request.method == 'POST':
        form = ImportJsonForm(request.POST, files=request.FILES, instance=analysis, )
    else:
        form = ImportJsonForm(request = request, instance=analysis)
    return import_json_save_form(request, form, 'modals/analysis_comparison/analysis_comparison_import_json_append_modal.html')


def json_import_analysis_comparison_create_new(request):
   from EcoMan.forms import AnalysisComparisonImportFromJSONForm
   if request.method == 'POST':
      form = AnalysisComparisonImportFromJSONForm(request.POST, files=request.FILES,)
   else:
      form = AnalysisComparisonImportFromJSONForm()
   return import_json_save_form(request, form, 'modals/analysis_comparison/analysis_comparison_import_JSON_modal.html')


def json_import_analysis_append(request, pk_analysis):
   analysis = get_object_or_404(Analysis, pk=pk_analysis)
   from EcoMan.forms.import_json import ImportJsonAnalysisForm
   if request.method == 'POST':
      form = ImportJsonAnalysisForm(request.POST, files=request.FILES, instance=analysis, )
   else:
      form = ImportJsonAnalysisForm(request = request, instance=analysis)
   return import_json_analysis_save_form(request, form, 'modals/analysis/analysis_import_JSON_modal.html')