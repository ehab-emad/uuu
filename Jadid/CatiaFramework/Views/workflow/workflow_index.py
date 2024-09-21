from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from website.models import Project
from CatiaFramework.models import Workflow, ProjectUser_CatiaFramework_Ref
from django.db.models import Q


# Index of OfiicialCatiaFramework Workflows
class workflow_index(TemplateView):
    template_name = 'CatiaFramework/workflow/workflow_index.html'
    def get_context_data(self, **kwargs):
        context = super(workflow_index, self).get_context_data(**kwargs)
        current_project = self.request.user.projectuser.current_project
        current_project_id = current_project.UUID
        user = self.request.user
        context['project'] = get_object_or_404(Project, pk=current_project_id)
        query_all = Workflow.objects.all()
        query_all = query_all.filter(Q(type = "DATABASE_TEMPLATE") or Q(type = "FRAMEWORK_INTERNAL") )

        context['workflows'] = query_all
        return context
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/user/login')
        return super().dispatch(request, *args, **kwargs)
    