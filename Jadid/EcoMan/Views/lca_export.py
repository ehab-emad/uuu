from django.core import serializers
from django.shortcuts import get_object_or_404
from EcoMan.models import Analysis_Comparison, Lca_Property, Analysis
from django.shortcuts import redirect
from django.conf import settings
from django.template import loader
import pathlib
from pathlib import Path
import os, json
from datetime import date
from django.http import HttpResponse
from EcoMan.Views import analysis_comparison_playground

def analysis_comparison_to_json(request, pk_analysis_comparison):
    '''This function will import analysis_comparison jobs exported as json
    '''
    if request.method == "GET":
        analysis_comparison =get_object_or_404(Analysis_Comparison, pk=pk_analysis_comparison)

        analysis_dict = analysis_comparison.as_dict()
        analysis_json= json.dumps(analysis_dict, indent = 4)
        #prepare dst folder
        path_json_file = settings.MEDIA_ROOT + "\\LCA_Analysis_Exports\\"
        p = pathlib.Path(path_json_file)
        p.mkdir(parents=True, exist_ok=True)

        #prepare template for output file
        name_dst_file = "QLCA_EXPORT_" + analysis_comparison.name + "_" + request.user.username + "_" + str(date.today()) + ".json"
        dst_path = path_json_file + name_dst_file
        file_path = os.path.join(settings.MEDIA_ROOT, dst_path)

        if os.path.exists(p):          #if destination path exists dump to json
            with open(file_path, 'w') as fh:
                fh.write(analysis_json)
                fh.close()
        if os.path.exists(file_path):  #if file was generated serve it to user
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/force-download") #content_type="application/json"  content_type="application/force-download")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                return response

    return redirect(request.META.get('HTTP_REFERER'))

def analysis_to_json(request, pk_analysis):
    '''This function will import analysis_comparison jobs exported as json
    '''
    if request.method == "GET":
        analysis =get_object_or_404(Analysis, pk=pk_analysis)

        analysis_dict = analysis.as_comparison_dict()
        analysis_json= json.dumps(analysis_dict, indent = 4)
        #prepare dst folder    
        path_json_file = os.path.join(settings.MEDIA_ROOT, 'LCA_Analysis_Exports')
        p = pathlib.Path(path_json_file)
        p.mkdir(parents=True, exist_ok=True)

        #prepare template for output file
        name_dst_file = "QLCA_EXPORT_" + analysis.name + "_" + request.user.username + "_" + str(date.today()) + ".json"
        dst_path = path_json_file + name_dst_file
        file_path = os.path.join(settings.MEDIA_ROOT, dst_path)

        if os.path.exists(p):          #if destination path exists dump to json
            with open(file_path, 'w') as fh:
                fh.write(analysis_json)
                fh.close()
        if os.path.exists(file_path):  #if file was generated serve it to user
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/force-download") #content_type="application/json"  content_type="application/force-download")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                return response

    return redirect(request.META.get('HTTP_REFERER'))

def analysis_comparison_to_diagram(request, pk_analysis_comparison):
    '''This function will import analysis_comparison jobs exported as json
    '''
    if request.method == "GET":
        analysis_comparison =get_object_or_404(Analysis_Comparison, pk=pk_analysis_comparison)

        analysis_dict = analysis_comparison.as_dict()
        analysis_json= json.dumps(analysis_dict, indent = 4)
        context = {"json_dict": analysis_json}
        template = loader.get_template('EcoMan/analysis_comparison/analysis_comparison_diagram_view.html')

    return HttpResponse(template.render(context, request))

def lca_properties_to_json(request):
    '''This function will simply export all lca properties
    '''
    if request.method == "GET":
        query_properties = Lca_Property.objects.all()
        result_json =''
        temp_dict = {}
        for object in query_properties:
            temp_dict.update(object.as_dict())

        result_json = json.dumps({temp_dict['name'] : temp_dict}, indent = 4)

    response = HttpResponse(result_json, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="result.json"'
    return response