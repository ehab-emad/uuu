from django.shortcuts import render
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from urllib import request
from django.views import generic
from django.views.generic import View, TemplateView
from django.http import HttpResponseRedirect
from website.models import Project
from EcoMan.models import Analysis
from EcoMan.models import Analysis_Comparison

from ConceptMan.models import Concept
from website.models import Vehicle
from ConceptMan.models import Part
from EcoMan.models import Lca_Part
from EcoMan.models import Lca_Database_Process
from django.db.models import Q


#Index qlcas jobs
class analysis_comparison_index_view(TemplateView):
    template_name = 'EcoMan/analysis_comparison/analysis_comparison_index_view.html'
    def get_context_data(self, **kwargs):
        context = super(analysis_comparison_index_view, self).get_context_data(**kwargs)
        current_project = self.request.user.projectuser.current_project
        current_project_id = self.request.user.projectuser.current_project.UUID
        user = self.request.user
        context['project'] = get_object_or_404(Project, pk=current_project_id)
        query_all = Analysis_Comparison.objects.all()

        context['objects_current_project'] = query_all.filter(Q(project_model__UUID = current_project.UUID) & Q(analysis_settings__is_public = True)).order_by('-updated_at')
        context['objects_current_user'] = query_all.filter(Q(project_model__UUID=current_project.UUID) & Q(owner__UUID = user.projectuser.UUID) & Q(analysis_settings__is_playground=False)).order_by('-updated_at')
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/user/login')
        return super().dispatch(request, *args, **kwargs)