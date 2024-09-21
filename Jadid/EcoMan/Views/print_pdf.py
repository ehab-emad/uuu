
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View
from ConceptMan.models import Part
from django.template.loader import render_to_string
from django.conf import settings
from EcoMan.models import Analysis_Comparison, Analysis
from django.http import FileResponse
import io, os
from EcoMan.scripts import PdfReport, PdfReport_one_column
from pathlib import Path
from datetime import date
import time

def lca_comparison_print_reportlab(request, **kwargs):
    #Get analysis id and name, generate pdf filename
    analysis_id = kwargs['pk']
    analysis = get_object_or_404(Analysis_Comparison, pk=analysis_id)
    analysis_name = analysis.name
    name_pdf_file = "QLCA_REPORT_" + analysis_name + "_" + analysis_id + "_" + request.user.username + "_" + ''.join(str(x) for x in time.localtime()) + ".pdf"

    #Create Bytestream buffer and pdf
    buffer = io.BytesIO()
    report = PdfReport(buffer, analysis_id)
    pdf = report.createReport(request)
    #prepare dst folder
    path_pdf_file = os.path.join(settings.MEDIA_ROOT, "QLCA_Reports")   
    p = Path(path_pdf_file)
    p.mkdir(parents=True, exist_ok=True)
    
    file_path = os.path.join(settings.MEDIA_ROOT, path_pdf_file, name_pdf_file)
    if os.path.exists(p):          #if destination path exists dump pdf
            with open(file_path, 'wb') as outfile:
                outfile.write(pdf)
                outfile.close()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'filename="%s"' % name_pdf_file


    return response


def lca_analysis_print_reportlab(request, **kwargs):
    #Get analysis id and name, generate pdf filename
    analysis_id = kwargs['pk']
    analysis = get_object_or_404(Analysis, pk=analysis_id)
    analysis_name = analysis.name
    name_pdf_file = "QLCA_REPORT_" + analysis_name + "_" + analysis_id + "_" + request.user.username + "_" + str(date.today()) + ".pdf"
    #Create Bytestream buffer and pdf
    buffer = io.BytesIO()
    report = PdfReport_one_column(buffer, analysis_id)
    pdf = report.createReportForAnalysis(request)
    
    #prepare dst folder
    path_pdf_file = os.path.join(settings.MEDIA_ROOT, "QLCA_Reports")   
    p = Path(path_pdf_file)
    p.mkdir(parents=True, exist_ok=True)
    
    file_path = os.path.join(settings.MEDIA_ROOT, path_pdf_file, name_pdf_file)
    if os.path.exists(p):          #if destination path exists dump pdf
            with open(file_path, 'wb') as outfile:
                outfile.write(pdf)
                outfile.close()
    #django response showing the bytestream, not the saved file from server
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'filename="%s"' % name_pdf_file
    return response