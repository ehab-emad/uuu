from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from website.models import Project
from BoltMan.models import Bolt_Case
from django.db.models import Q


#Index qlcas jobs
class assessment_index_view(TemplateView):
    template_name = 'BoltMan/SingleAssessment/index.html'
    def get_context_data(self, **kwargs):
        context = super(assessment_index_view, self).get_context_data(**kwargs)
        current_project = self.request.user.projectuser.current_project
        current_project_id = current_project.UUID
        user = self.request.user
        context['project'] = get_object_or_404(Project, pk=current_project_id)
        query_all = Bolt_Case.objects.all()

        context['objects_current_project'] = query_all.filter(Q(project_model__UUID = current_project.UUID) & Q(analysis_settings__is_public = True)).order_by('-updated_at')
        context['objects_current_user'] = query_all.filter(Q(project_model__UUID=current_project.UUID) & Q(owner__UUID = user.projectuser.UUID)).order_by('-updated_at')
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/user/login')
        return super().dispatch(request, *args, **kwargs)




