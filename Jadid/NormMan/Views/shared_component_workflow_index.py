from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from website.models import Project
from EcoMan.models import Analysis_Comparison
from NormMan.models import NormParts_Shared_Component, Workflow_Session, ProjectUser_NormMan_Ref
from django.db.models import Q


# Index of NormMan workflows
class shared_component_workflow_index(TemplateView):
    template_name = 'NormMan/normparts/shared_component_workflow_index.html'
    def get_context_data(self, **kwargs):
        context = super(shared_component_workflow_index, self).get_context_data(**kwargs)
        workflow_object = get_object_or_404(NormParts_Shared_Component, UUID=kwargs.get('uuid', None)) 
        owner = ProjectUser_NormMan_Ref.objects.filter(nickname = self.request.user.username).get()
        user_sessions= Workflow_Session.objects.filter(owner_id=owner.pk, workflow_object__UUID = workflow_object.UUID).order_by('-updated_at')

        current_project = self.request.user.projectuser.current_project
        current_project_id = current_project.UUID
        context['project'] = get_object_or_404(Project, pk=current_project_id)
        context['workflow_uuid'] = kwargs.get('uuid', None)
        context['objects_public'] = None
        context['objects_user'] = user_sessions
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/user/login')
        return super().dispatch(request, *args, **kwargs)