
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View
from ConceptMan.models import Part
from django.template.loader import render_to_string
from django.conf import settings
from CatiaFramework.models import Workflow, Workflow_Session
from django.http import FileResponse
import io, os
from CatiaFramework.scripts import PdfReport
from pathlib import Path
from datetime import date
import time

def print_session_report(request, **kwargs):
    #Get analysis id and name, generate pdf filename
    session_id = kwargs['uuid_session']
    session = get_object_or_404(Workflow_Session, pk=session_id)
    session_name = session.name
    name_pdf_file = "SESSION_REPORT_" + session_name + "_" + session_id + "_" + request.user.username + "_" + str(date.today()) + ".pdf"

    #Create Bytestream buffer and pdf
    buffer = io.BytesIO()
    report = PdfReport(buffer, session_id)
    pdf = report.createReport(request)
    
    #prepare dst folder
    path_pdf_file = os.path.join(settings.MEDIA_ROOT, "workflow_sessions" , f"User_{str(session.owner.UUID)}" ,  f"Session_{session_id}", "reports")
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





