from django.shortcuts import  get_object_or_404
from .views import *
from django.views import generic
from django.views.generic import  TemplateView
from website.models import Project
from CatiaFramework.models import dotnet_component, dotnet_projectfolder
from django.http import HttpResponseRedirect
from ConceptMan.models import Concept
from EcoMan.QLCA_Idemat_Calculation import * 
from website.scripts import *
from website.models import ProjectUser
class vbdotnet_component_detail_view(generic.DetailView):
    '''vbdotnet_component_detail_view
    '''
    template_name = 'CatiaFramework/database/vbdotnet_component_detail_view.html'
    model = dotnet_component
    def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['project_user'] = ProjectUser.objects.filter(user_id = self.request.user.pk) 


        content_section = self.object.content_section
        # Replace "\r\n" with <code></code>
        result_string = content_section.replace("\r\n", "</code>\r\n<code>")

        # Add <code> at the beginning and </code> at the end
        result_string = "<code>" + result_string + "</code>\r\n"
        context['content_section'] = result_string


        comment_section = self.object.comment_section
        # Replace "\r\n" with <code></code>
        result_string = comment_section.replace("\r\n", "</code>\r\n<code>")

        # Add <code> at the beginning and </code> at the end
        result_string = "<code>" + result_string + "</code>\r\n"
        context['comment_section'] = result_string

        #context['parent_folder']
        #context['parent_component']
        #context['object']
        #context['children']

        return context
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/user/login')
        return super().dispatch(request, *args, **kwargs)
