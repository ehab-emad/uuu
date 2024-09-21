from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from website.models import Project
from CatiaFramework.models import Workflow_Session, ProjectUser_CatiaFramework_Ref
from django.db.models import Q


# Index of CatiaFramework Workflows
class workflow_session_index(TemplateView):
    template_name = 'CatiaFramework/workflow/workflow_session_index.html'
    def get_context_data(self, **kwargs):
        context = super(workflow_session_index, self).get_context_data(**kwargs)
        current_project = self.request.user.projectuser.current_project
        current_project_id = current_project.UUID        
        templates = list({session.workflow_model for session in Workflow_Session.objects.all()})
        context['project'] = get_object_or_404(Project, pk=current_project_id)        
        context['templates'] = templates
        # -> User probably for future usage, if there is a need to filter session by currently logged in user.
        # context['user'] = ProjectUser_CatiaFramework_Ref.objects.filter(nickname=self.request.user).get()
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/user/login')
        return super().dispatch(request, *args, **kwargs)