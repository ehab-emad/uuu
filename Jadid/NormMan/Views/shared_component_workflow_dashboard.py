from NormMan.models import NormParts_Shared_Component, Workflow_Session, ProjectUser_NormMan_Ref
from .views import *
from django.views.generic import  TemplateView
import json, os
from django.shortcuts import  get_object_or_404
from django.views.generic import TemplateView
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, JsonResponse   
from website.models import ProjectUser
from channels.layers import get_channel_layer
from NormMan.models import Component_Group_Level
from NormMan.scripts.meta_replication import valid
from website import settings
from website.settings import MEDIA_ROOT

def flatten_json(o):
    o_list = []
    for key in o:
        o_list.append(o[key])
    return o_list


class shared_component_workflow_redirect(TemplateView):

    template_name = 'NormMan/normparts/shared_component_workflow_dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/user/login')
        
        workflow_object = get_object_or_404(NormParts_Shared_Component, UUID=kwargs.get('uuid', None)) 
        target_object_uuid = kwargs.get('uuid', None)
        owner = ProjectUser_NormMan_Ref.objects.filter(nickname = self.request.user.username).get()

        if kwargs.get('continue', None) == "True": #check if user wants to continue or to start a new job
            user_sessions= Workflow_Session.objects.filter(owner_id=owner.pk, workflow_object__UUID = workflow_object.UUID )
            try:
                session_object=user_sessions.latest('updated_at')
            except:
                session_object = Workflow_Session.objects.create(**{ "owner": owner,   "workflow_object" : workflow_object, "is_public": True })          
        else:
            if target_object_uuid:
                session_object = Workflow_Session.objects.create(**{ "owner": owner,   "workflow_object" : workflow_object,"is_public": True }) 

        return HttpResponseRedirect(reverse('NormMan:shared_component_workflow_session', args=[session_object.UUID]))