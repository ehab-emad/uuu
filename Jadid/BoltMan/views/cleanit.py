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
from ..forms.forms import BoltCaseInstanceFormCreate, BoltCaseFormBoltGeometry, BoltCaseFormWasher, BoltCaseFormPart, BoltCaseFormFrictionThread, BoltCaseFormFrictionHead, BoltCaseFormFrictionJoint
from functools import reduce
from django.db.models import Q
from .modal import *
from website.models import Project, Vehicle
from django.http import HttpResponseRedirect
def vehicle_index(request):

    vehicles= Vehicle.objects.all()

    return render(request, 'BoltMan/carindex.html', {'vehicles': vehicles})

class index(TemplateView):
    vehicles= Vehicle.objects.all()
    template_name = 'BoltMan/index_vehicle.html'

class index_vehicle(TemplateView):
    template_name = 'BoltMan/vehicle_cards.html'
    def get_context_data(self, **kwargs):
        current_project_id = self.request.user.projectuser.current_project.UUID
        context = super(index_vehicle, self).get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=current_project_id)
        temporary = Vehicle.objects.all()
        temporary = temporary.filter(project__pk=current_project_id)
        context['vehicles'] = temporary
        return context
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/user/login')

        return super().dispatch(request, *args, **kwargs)

class PartDetailView(TemplateView):
    template_name = 'BoltMan/partdetail.html'
    def get_context_data(self, **kwargs):
        context = super(PartDetailView, self).get_context_data(**kwargs)
        context['part'] = get_object_or_404(Part, pk=self.kwargs['pk'])
        temporary = Bolt_Case.objects.all()
        temporary = temporary.filter(Q(part1__pk=self.kwargs['pk']) | Q(part2__pk=self.kwargs['pk']) | Q(part3__pk=self.kwargs['pk']))
        #(part1__vehicles__pk=self.kwargs['pk'], part2__vehicles__pk=self.kwargs['pk'], part3__vehicles__pk=self.kwargs['pk'] )
        context['boltcase'] = temporary
        return context

class CarIndexView(generic.ListView):
    template_name = 'BoltMan/carindex.html'
    def get_queryset(self):
        return Vehicle.objects.all()

class CarDetailView(generic.DetailView):
    model = Vehicle
    template_name = 'BoltMan/cardetail.html'


class BoltCaseIndexView(generic.ListView):
    template_name = 'BoltMan/boltcaseindex.html'
    def get_queryset(self):
        return Bolt_Case.objects.all()

class BoltCaseDetailView(generic.DetailView):
    model = Bolt_Case
    template_name = 'BoltMan/boltcasedetail.html'

    def get_context_data(self, **kwargs):
        context = super(BoltCaseDetailView, self).get_context_data(**kwargs)
        context['boltcase'] = get_object_or_404(Bolt_Case, pk=self.kwargs['pk'])

        context['boltcase'].set_vdi_input_param()
        context['boltcase'].save()

        boltcase = context['boltcase']
        vehicles_ids = []
        for vehicle in boltcase.vehicle.all():
            vehicles_ids.append(vehicle.pk)

        vehicles_in_use = Car.objects.filter(pk__in=vehicles_ids)
        context['vehicles'] = vehicles_in_use
        return context

class BoltCaseInstanceCreate(CreateView):
    model = Bolt_Case_Instance
    fields ='__all__' #['name', 'picture', 'requirement', 'bolt_geometry', 'part1', 'part2', 'part3', 'steelwasher', 'nonstandardwasher', 'name', 'is_favorite']

class BoltCaseResultView(TemplateView):
    model = Bolt_Case
    template_name = 'BoltMan/boltcaseresult.html'   
    def get_context_data(self, **kwargs):
        context = super(BoltCaseResultView, self).get_context_data(**kwargs)
        context['boltcase'] = get_object_or_404(Bolt_Case, pk=self.kwargs['pk'])
        part1 = context['boltcase'].part1
        part2 = context['boltcase'].part2
        part3 = context['boltcase'].part3
        vehicles_ids = []
        for vehicle in part1.vehicles.all():
            vehicles_ids.append(vehicle.pk)
        for vehicle in part2.vehicles.all():
            vehicles_ids.append(vehicle.pk)
        for vehicle in part3.vehicles.all():
            vehicles_ids.append(vehicle.pk)    
        vehicles_in_use = Car.objects.filter(pk__in=vehicles_ids)
        context['vehicles'] = vehicles_in_use
        print(context)
        return context


def boltcase_part(request, pk):
    boltcase = get_object_or_404(Bolt_Case, pk=pk)
    if request.method == 'POST':
        form = BoltCaseFormPart(request.POST, instance=boltcase)
    else:
        form = BoltCaseFormPart(instance=boltcase)
    return boltcase_save_form(request, form, 'modals/boltcase/boltcase_update_part_modal.html')  

def boltcase_instance(request, pk):
    boltcase = get_object_or_404(Bolt_Case, pk=pk)
    if request.method == 'POST':
        form = BoltCaseFormInstance(request.POST, instance=boltcase)
    else:
        form = BoltCaseFormInstance(instance=boltcase)
    return boltcase_save_form(request, form, 'modals/boltcase/boltcase_select_instance_modal.html')      

def boltcase_washer(request, pk):
    boltcase = get_object_or_404(Bolt_Case, pk=pk)
    if request.method == 'POST':
        form = BoltCaseFormWasher(request.POST, instance=boltcase)
    else:
        form = BoltCaseFormWasher(instance=boltcase)
    return boltcase_save_form(request, form, 'modals/boltcase/boltcase_select_washer_modal.html')  

def boltcase_boltgeometry(request, pk):
    boltcase = get_object_or_404(Bolt_Case, pk=pk)
    if request.method == 'POST':
        form = BoltCaseFormBoltGeometry(request.POST, instance=boltcase)
    else:
        form = BoltCaseFormBoltGeometry(instance=boltcase)
    return boltcase_save_form(request, form, 'modals/boltcase/boltcase_select_boltgeometry_modal.html')  

def boltcase_frictionthread(request, pk):
    boltcase = get_object_or_404(Bolt_Case, pk=pk)
    if request.method == 'POST':
        form = BoltCaseFormFrictionThread(request.POST, instance=boltcase)
    else:
        form = BoltCaseFormFrictionThread(instance=boltcase)
    return boltcase_save_form(request, form, 'modals/boltcase/boltcase_select_frictionthread_modal.html')

def boltcase_frictionhead(request, pk):
    boltcase = get_object_or_404(Bolt_Case, pk=pk)
    if request.method == 'POST':
        form = BoltCaseFormFrictionHead(request.POST, instance=boltcase)
    else:
        form = BoltCaseFormFrictionHead(instance=boltcase)
    return boltcase_save_form(request, form, 'modals/boltcase/boltcase_select_frictionhead_modal.html') 

def boltcase_frictionjoint(request, pk):
    boltcase = get_object_or_404(Bolt_Case, pk=pk)
    if request.method == 'POST':
        form = BoltCaseFormFrictionJoint(request.POST, instance=boltcase)
    else:
        form = BoltCaseFormFrictionJoint(instance=boltcase)
    return boltcase_save_form(request, form, 'modals/boltcase/boltcase_select_frictionjoint_modal.html')  
    
def load_parts(request):
    vehicle_id = request.GET.getlist('vehicle[]')

    parts=Part.objects.all()
    for item in vehicle_id:
        parts=parts.filter(vehicles__in=[item])

    return render(request, 'modals/part/part_dropdown_list_options.html', {'parts': parts})

def load_boltcaseinstances(request):
    vehicle_id = request.GET.getlist('vehicle[]')

    instances=Bolt_Case_Instance.objects.all()
    for item in vehicle_id:
        instances=instances.filter(vehicles__in=[item])

    return render(request, 'modals/part/part_dropdown_list_options.html', {'parts': instances})

class BoltCaseInstanceDetailView(generic.DetailView):
    model = Bolt_Case_Instance
    template_name = 'BoltMan/boltcaseinstancedetail.html'

    def get_context_data(self, **kwargs):
        context = super(BoltCaseInstanceDetailView, self).get_context_data(**kwargs)
        context['boltcaseinstance'] = get_object_or_404(Bolt_Case_Instance, pk=self.kwargs['pk'])
        context['boltcaseinstance'].calculate_settling_rate()
        context['boltcaseinstance'].save()
        boltcaseinstance = context['boltcaseinstance']
        vehicles_ids = []
        for vehicle in boltcaseinstance.vehicle.all():
            vehicles_ids.append(vehicle.pk)

        vehicles_in_use = Car.objects.filter(pk__in=vehicles_ids)
        context['vehicles'] = vehicles_in_use
        #print(context)
        return context