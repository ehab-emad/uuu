from django.contrib.staticfiles.storage import staticfiles_storage
from django.views import generic
from EcoMan.models import Lca_Database_Process
from EcoMan.models import Lca_Database
from EcoMan.models import Lca_Database_Category
from EcoMan.models import Lca_Database_Group
from EcoMan.models import Lca_Database_Subgroup
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect

from django.db.models import ProtectedError
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.db.models import Q
import os

from django.http import HttpResponse
from website.security import check_if_user_in_roles
#DB-----------------------------------------------------------------------------------
class LcaProcessListView(generic.ListView):
    model = Lca_Database_Process
    context_object_name = 'process_list'
    template_name = 'EcoMan/lca_database/db_processindex.html'
    def get_queryset(self):
        all_processes = Lca_Database_Process.objects.filter(Q(database_model_id = self.kwargs.get('pk')))
        all_processes = all_processes.filter(Q(accessibility = 'PRIVATE') | Q(accessibility = 'DATABASE_USERS') | Q(accessibility = 'ARCHIVE'))
        all_processes = list(all_processes)      
        for n in range(len(all_processes) - 1, -1, -1):
            process = all_processes[n]
            #remove processes which are private and are not belongiong to user
            if process.accessibility == 'PRIVATE':
                if process.owner.UUID != self.request.user.projectuser.UUID:
                    all_processes.pop(n)
        return all_processes
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/user/login')
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_database = Lca_Database.objects.get(pk=self.kwargs.get('pk'))
        context['database'] = current_database
        if check_if_user_in_roles(self.request,['edag_worker']):
            context['is_staff'] = True
        else:
            context['is_staff'] = False           

        all_processes = Lca_Database_Process.objects.filter(Q(database_model_id = self.kwargs.get('pk')))
        all_processes = all_processes.filter(Q(accessibility = 'PRIVATE') | Q(accessibility = 'DATABASE_USERS') | Q(accessibility = 'ARCHIVE'))
        all_processes_count = len(list(all_processes))

        if "/be_paramount/app-ecoman/user-professional" in self.request.session["groups"] or all_processes_count < 50:
            context['is_add_new_process_allowed'] = True
        else:
            context['is_add_new_process_allowed'] = False  
        return context

class open_database_index_view(generic.ListView):
    template_name = 'EcoMan/lca_database/db_index_open.html'
    '''organise request'''
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/user/login')        
        return super(open_database_index_view, self).dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return Lca_Database.objects.filter(Q(accessibility="OPEN"))
    def get_context_data(self, **kwargs):
        context = super(open_database_index_view, self).get_context_data(**kwargs)     
        if self.request.user.is_staff == True:
            context['is_staff'] = True
        else:
            context['is_staff'] = False            
        return context
class edag_database_index_view(generic.ListView): #ORGANISATION
    template_name = 'EcoMan/lca_database/db_index_organisation.html'
    '''organise request'''
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/user/login')        
        return super(edag_database_index_view, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        query = Lca_Database.objects.filter(accessibility="ORGANISATION")
        query = query.filter()
        auth_project_ids = []
        for project in self.request.user.projectuser.authorised_projects.all():
            auth_project_ids.append(project.UUID)
        query = query.filter(projects__UUID__in = auth_project_ids)
        return query
    def get_context_data(self, **kwargs):
        context = super(edag_database_index_view, self).get_context_data(**kwargs)   
        if self.request.user.is_staff == True:
            context['is_staff'] = True
        else:
            context['is_staff'] = False   
        return context            
class project_database_index_view(generic.ListView):
    template_name = 'EcoMan/lca_database/db_index_project.html'
    '''organise request'''
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated: #force user to login
            return HttpResponseRedirect('/user/login')
        return super().dispatch(request, *args, **kwargs)
 
    
    def get_queryset(self):
        query = Lca_Database.objects.filter(accessibility="PROJECT")
        query = query.filter()


        auth_project_ids = []
        for project in self.request.user.projectuser.authorised_projects.all():
            auth_project_ids.append(project.UUID)
        from EcoMan.models import Project_EcoMan_Ref
        current_project = get_object_or_404(Project_EcoMan_Ref, pk=str(self.request.user.projectuser.current_project.UUID))
        
        #Filter objects belonging to 
        from operator import and_, or_
        from django.db.models import Q
        import functools 
        query = query.filter(functools.reduce(or_, [Q(projects__UUID=c) for c in auth_project_ids]))
        query = query.filter(projects__UUID = current_project.UUID)
        return query


    def get_context_data(self, **kwargs):
        context = super(project_database_index_view, self).get_context_data(**kwargs)      
        if self.request.user.is_staff == True:
            context['is_staff'] = True
        else:
            context['is_staff'] = False   
        return context
    
def lca_db_export_excel(request, pk):
    '''Function will export current LCA database to excel '''
    lca_db = get_object_or_404(Lca_Database, pk=pk)

    try:
        path_file_to_export = lca_db.LCADatabaseFileExport(request.user.username)

        if os.path.exists(path_file_to_export):
            with open(path_file_to_export, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(path_file_to_export)
                return response

    except ProtectedError:
        messages.add_message(request,messages.ERROR, "No permision")

    except Exception as e:
        messages.add_message(request,messages.ERROR, e)

    return redirect(request.META.get('HTTP_REFERER'))

#Import Database Categories
def IdematDatabaseImportCategories(request):
    if request.method == "GET":
        if request.user.is_staff == True:
           #"""This function fill Lca_Database_Category, Lca_Database_Group and Lca_Database_Subgroup based on all official Idemat LCA Databases  """

            query=Lca_Database_Process.objects.filter( Q(database_model__accessibility="OFFICIAL_GLOBAL")) #limited to official databases

            #query if Lca_Database_Subgroup exists
            new_subgroup = False
            new_group = False
            new_category = False
            for process in query:

               category_query =Lca_Database_Category.objects.filter(Q(name=process.category_name) &
                                                                    Q(category_id=process.category_id) ).distinct()

               group_query =Lca_Database_Group.objects.filter(Q(category_model__category_id=process.category_id) &
                                                              Q(category_model__name=process.category_name) &
                                                              Q(name=process.group_name) &
                                                              Q(group_id=process.group_id) ).distinct()

               subgroup_query =Lca_Database_Subgroup.objects.filter(Q(group_model__group_id=process.group_id) &
                                                                    Q(group_model__name=process.group_name) &
                                                                    Q(group_model__category_model__category_id=process.category_id) &
                                                                    Q(group_model__category_model__name=process.category_name) &
                                                                    Q(name=process.subgroup_name) &
                                                                    Q(subgroup_id=process.subgroup_id)).first()

               if (not category_query) and (not group_query) and (not subgroup_query): #everything has to be created
                    temp_category = Lca_Database_Category.objects.create(name=process.category_name, category_id=process.category_id,)
                    temp_group = Lca_Database_Group.objects.create(name=process.group_name, group_id=process.group_id, category_model = temp_category)
                    temp_subgroup = Lca_Database_Subgroup.objects.create(name=process.subgroup_name, subgroup_id=process.subgroup_id, group_model = temp_group)

               if (category_query) and (not group_query) and (not subgroup_query): #category exists
                    temp_category = category_query.get()
                    temp_group = Lca_Database_Group.objects.create(name=process.group_name, group_id=process.group_id, category_model = temp_category)
                    temp_subgroup = Lca_Database_Subgroup.objects.create(name=process.subgroup_name, subgroup_id=process.subgroup_id, group_model = temp_group)

               if (category_query) and (group_query) and (not subgroup_query): #category exists
                    temp_category = category_query.get()
                    temp_group = group_query.get()
                    temp_subgroup = Lca_Database_Subgroup.objects.create(name=process.subgroup_name, subgroup_id=process.subgroup_id, group_model = temp_group)


            messages.add_message(request,messages.SUCCESS, "Idemat Database Categories successfully imported!")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.add_message(request,messages.ERROR, "Idemat Database Import Categories only for Staff!")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def lca_database_template_download(request):
    '''Function will download static lca template '''
    try:
        path_file_to_export = staticfiles_storage.path('EcoMan/QLCA_process_upload_templateV2.5.xlsx')
        if os.path.exists(path_file_to_export):
            with open(path_file_to_export, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(path_file_to_export)
                return response

    except ProtectedError:
        messages.add_message(request,messages.ERROR, "No permision")

    except Exception as e:
        messages.add_message(request,messages.ERROR, e)

    return redirect(request.META.get('HTTP_REFERER'))

def qlca_documentation_download(request):
    '''Function will donload static lca template '''
    try:
        path_file_to_export = staticfiles_storage.path('EcoMan/2.1_Tutorial_QLCA.pdf')
        if os.path.exists(path_file_to_export):
            with open(path_file_to_export, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(path_file_to_export)
                return response

    except ProtectedError:
        messages.add_message(request,messages.ERROR, "No permision")

    except Exception as e:
        messages.add_message(request,messages.ERROR, e)

    return redirect(request.META.get('HTTP_REFERER'))