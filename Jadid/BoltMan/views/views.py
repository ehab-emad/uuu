import time
from django.shortcuts import  get_object_or_404
from .views import *
from django.views import generic
from django.views.generic import  TemplateView
from website.models import Project
from EcoMan.models import Analysis, Lca_Database
from django.http import HttpResponseRedirect
from ConceptMan.models import Concept
from EcoMan.QLCA_Idemat_Calculation import * 
from website.scripts import *
from website.models import ProjectUser
class index(TemplateView):
    '''EcoMan index page
    '''
    template_name = 'BoltMan/index.html'
    def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
        c = super().get_context_data(**kwargs)
        c['user'] = self.request.user
        c['project_user'] = ProjectUser.objects.filter(user_id = self.request.user.pk) 
        c['expiration_timestamp'] = self.request.session.get('expiration_timestamp', int(time.time()))

        #check if corporate project for qlca was created where processes visible only for whitelisted users will be visible
        query = Project.objects.filter(name = "Organisation_LCA_Project")
        if not query:
            new_project = Project.objects.create(name = "Organisation_LCA_Project" )
        return c
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/user/login')
        return super().dispatch(request, *args, **kwargs)

class assessment_welcome_screen(TemplateView):
    '''Welcome Screen For Single Assessment
    '''
    template_name = 'BoltMan/SingleAssessment/welcome_screen.html'
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/user/login')
        return super().dispatch(request, *args, **kwargs)

class manager_welcome_screen(TemplateView):
    '''Welcome Screen For Manager of Bolt Cases
    '''
    template_name = 'BoltMan/SingleAssessment/welcome_screen.html'
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/user/login')
        return super().dispatch(request, *args, **kwargs)    
