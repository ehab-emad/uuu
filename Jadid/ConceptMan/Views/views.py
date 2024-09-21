from django.shortcuts import get_object_or_404
from website.models.vehicle import Vehicle
from ConceptMan.models.concept import Concept
from website.models.project import Project
from django.views.generic import  TemplateView
from django.http import HttpResponseRedirect
class index_vehicle(TemplateView):
    template_name = 'ConceptMan/index_vehicle.html'
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

class index_concept(TemplateView):
    template_name = 'ConceptMan/index_concept.html'
    def get_context_data(self, **kwargs):
        context = super(index_concept, self).get_context_data(**kwargs)
        context['vehicle'] = get_object_or_404(Vehicle, pk=self.kwargs['pk'])
        temporary = Concept.objects.all()
        temporary = temporary.filter(vehicles__pk=self.kwargs['pk'])
        context['concepts'] = temporary
        return context