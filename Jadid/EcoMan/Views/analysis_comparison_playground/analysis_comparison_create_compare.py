from django.shortcuts import  redirect
from EcoMan.models import Analysis, Project_EcoMan_Ref, Analysis_Comparison, Analysis_Settings
from django.shortcuts import  get_object_or_404
def analysis_comparison_create_compare(request):
   if request.method == "POST":
      id1 = request.POST.get('selected1')
      id2 = request.POST.get('selected2')

      analysis_comparison = Analysis_Comparison.objects.create(name="Analysis Comparison", 
                                                               project_model=Analysis.objects.get(pk=id1).project_model, 
                                                               )
      analysis_comparison.analysis_left = Analysis.objects.get(pk=id1)
      analysis_comparison.analysis_right = Analysis.objects.get(pk=id2)

      analysis_comparison.analysis_settings.is_playground = True
      analysis_comparison.analysis_settings.is_public = False

      analysis_comparison.analysis_settings.save()

      analysis_comparison.save()


      return redirect('EcoMan:analysis_comparison_detail_view', pk = analysis_comparison.id)
