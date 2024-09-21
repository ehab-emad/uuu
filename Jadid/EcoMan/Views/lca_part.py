from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from EcoMan.models import Analysis
from EcoMan.models import Lca_Part
#Move part move
def lca_part_move(request, pk_source_analysis, pk_target_analysis, pk_lca_part):

    if request.method == "GET":
        source_analysis = get_object_or_404(Analysis, pk = pk_source_analysis)
        target_analysis = get_object_or_404(Analysis, pk = pk_target_analysis)
        lca_part_to_move = get_object_or_404(Lca_Part, pk=pk_lca_part)

        target_analysis.lca_part_models.add(lca_part_to_move)
        source_analysis.lca_part_models.remove(lca_part_to_move)

        target_analysis.concept_model.parts.add(lca_part_to_move.part_model)
        source_analysis.concept_model.parts.remove(lca_part_to_move.part_model)
        target_analysis.concept_model.save()
        source_analysis.concept_model.save()
        return redirect(request.META.get('HTTP_REFERER'))

#mirror part
def lca_part_add_mirror(request, pk_source_analysis, pk_target_analysis, pk_lca_part):

    if request.method == "GET":
        target_analysis = get_object_or_404(Analysis, pk = pk_target_analysis)
        lca_part_to_copy = get_object_or_404(Lca_Part, pk=pk_lca_part)
  
        target_analysis.lca_part_models.add(lca_part_to_copy)
        target_analysis.concept_model.parts.add(lca_part_to_copy.part_model)

        return redirect(request.META.get('HTTP_REFERER'))


#Reduce part to the concept on the right
def lca_part_remove_mirror(request, pk_target_analysis, pk_lca_part):

    if request.method == "GET":
        target_analysis = get_object_or_404(Analysis, pk = pk_target_analysis)
        lca_part_to_copy = get_object_or_404(Lca_Part, pk=pk_lca_part)
  
        target_analysis.lca_part_models.remove(lca_part_to_copy)
        target_analysis.concept_model.parts.remove(lca_part_to_copy.part_model)

        return redirect(request.META.get('HTTP_REFERER'))

def quick_part_clone(request, pk_analysis, pk_lca_part):
    '''Analysis Comparison (Playground): Duplicate quick part for given analysis
    '''
    if request.method == "GET":
        analysis = get_object_or_404(Analysis, pk=pk_analysis)
        lca_part = get_object_or_404(Lca_Part, pk=pk_lca_part)

        duplicated_lca_part = lca_part.clone_it()

        #add steps to the analysis
        analysis.lca_part_models.add(duplicated_lca_part)
        analysis.save()

        #add part to the concept
        analysis.concept_model.parts.add(duplicated_lca_part.part_model)
        analysis.concept_model.save()

        return redirect(request.META.get('HTTP_REFERER'))




