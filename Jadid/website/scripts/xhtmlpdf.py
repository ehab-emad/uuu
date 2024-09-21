# importing the necessary libraries
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template, render_to_string  
from django.http import HttpResponse
from django.views.generic import View
from django.template.loader import render_to_string
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.db.models import ProtectedError
from django.shortcuts import render
import os
from website import settings
# defining the function to convert an HTML file to a PDF file

def html_to_pdf(template_src, request, context_dict={}):
     template = get_template(template_src)
     html  = template.render(context_dict)
     result = BytesIO()
     pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
     if not pdf.err:
         return HttpResponse(result.getvalue(), content_type='application/pdf')
     return None
