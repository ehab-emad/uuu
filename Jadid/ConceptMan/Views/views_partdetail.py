from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import View, TemplateView
from django.urls import reverse_lazy
from django.urls import reverse


from django.contrib.auth import authenticate, login
from django.template.loader import render_to_string
from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from BoltMan.models import *
from ConceptMan.models import *
from ConceptMan.forms import PartForm, PartFormManufacturingProcess
from functools import reduce
from django.db.models import Q
from .modal import *
from website.models import Project

from MatMan.models import Engineering_Material
from ConceptMan.models import Manufacturing_Process

class PartDetailView(generic.DetailView):
    model = Part
    template_name = 'ConceptMan/partdetail/partdetail.html'







def part_manufacturingprocess(request, pk):
    part = get_object_or_404(Part, pk=pk)
    if request.method == 'POST':
        form = PartFormManufacturingProcess(request.POST, instance=part)
    else:
        form = PartFormManufacturingProcess(instance=part)


    return part_save_form(request, form, 'modals/part/part_select_manufacturingprocess_modal.html')  

