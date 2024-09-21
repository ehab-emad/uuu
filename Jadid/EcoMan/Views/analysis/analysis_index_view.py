from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from website.models import Project
from EcoMan.models import Analysis
from django.db.models import Q
from django.views.generic import ListView
from django.db.models import Count
#Index qlcas jobs
class analysis_index_view(ListView):
    template_name = 'EcoMan/analysis/analysis_index_view.html'
    model = Analysis


    def get_context_data(self, **kwargs):
        context = super(analysis_index_view, self).get_context_data(**kwargs)
        context['include_playground'] = self.request.GET.get('include_playground') == 'True'
        current_project = self.request.user.projectuser.current_project
        current_project_id = current_project.UUID
        context['project'] = get_object_or_404(Project, pk=current_project_id)
        user = self.request.user
        include_playground = self.request.GET.get('include_playground')
        query_all = Analysis.objects.all()
        queryset = query_all.filter(project_model__UUID = current_project.UUID) .order_by('-updated_at')
    
        if include_playground:
            # Filter queryset to include objects related to the 'playground'                    
            queryset = queryset.annotate(parent_left_count=Count('analysis_comparison_Left')).annotate(parent_right_count=Count('analysis_comparison_Right'))
            queryset = queryset.filter(Q(parent_left_count__gt=0) | Q(parent_right_count__gt=0) ) #>0 greater than
        else:
            # Filter queryset to exclude objects related to the 'playground'
            queryset = queryset.annotate(parent_left_count=Count('analysis_comparison_Left') ).annotate(parent_right_count=Count('analysis_comparison_Right'))
            # Filter for unused ChildModel instances
            queryset = queryset.filter(Q(parent_left_count=0)  & Q(parent_right_count=0) )



        context['objects_current_project'] = queryset.filter(analysis_settings__is_public = True).order_by('-updated_at')
        context['objects_current_user'] = queryset.filter(owner__UUID = user.projectuser.UUID).order_by('-updated_at')


        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/user/login')
        return super().dispatch(request, *args, **kwargs)

class analysis_index_view_compare(TemplateView):
    template_name = 'EcoMan/analysis/analysis_index_view_compare.html'
    def get_context_data(self, **kwargs):
        context = super(analysis_index_view_compare, self).get_context_data(**kwargs)
        current_project = self.request.user.projectuser.current_project
        current_project_id = self.request.user.projectuser.current_project.UUID
        user = self.request.user
        context['project'] = get_object_or_404(Project, pk=current_project_id)
        query_all = Analysis.objects.all()

        context['objects_current_project'] = query_all.filter(Q(project_model__UUID=current_project.UUID) & Q(analysis_settings__is_public = True)).order_by('-updated_at')
        context['objects_current_user'] = query_all.filter(Q(project_model__UUID=current_project.UUID) & Q(owner__UUID = user.projectuser.UUID)).order_by('-updated_at')




        
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/user/login')
        return super().dispatch(request, *args, **kwargs)






