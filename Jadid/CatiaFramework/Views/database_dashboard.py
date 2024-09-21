import json, os
from django.contrib.staticfiles.storage import staticfiles_storage
from django.http import HttpResponseRedirect, JsonResponse   
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.views.generic import TemplateView
from .views import *
from .views import dynamic_breadcrumb
from website import settings
from CatiaFramework.scripts import create_root_module
from CatiaFramework.models import DotNet_ProjectFolder




class database_dashboard(TemplateView):

    template_name = 'CatiaFramework/database/database_dashboard.html'
    module_object = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/user/login')
        return super().dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        i_uuid = kwargs.get('uuid', None)
        if i_uuid is not None:
            module_object = DotNet_ProjectFolder.objects.filter(UUID = i_uuid).get()
        else:
            module_object = DotNet_ProjectFolder.objects.filter(group_depth_level = 0).first()
        if module_object is None:
            module_object = create_root_module()
        context = super(database_dashboard, self).get_context_data(**kwargs)

        context['category_group'] = module_object   

        query = DotNet_ProjectFolder.objects.filter(parent_folder__UUID = module_object.UUID)          

        context['category_groups'] = query

        query = module_object.dotnet_components.filter(type = 'VBDOTNET_LIBRARY') 
        #query = query.filter(project_model__UUID = self.request.user.projectuser.current_project.UUID)
        context['vbdotnet_libraries'] = query

        query = module_object.dotnet_components.filter(type = 'VBDOTNET_SUB') 
        #query = query.filter(project_model__UUID = self.request.user.projectuser.current_project.UUID)
        context['vbdotnet_methods'] = query

        query = module_object.dotnet_components.filter(type = 'VBDOTNET_CLASS')
        # query = query.filter(project_model__UUID = self.request.user.projectuser.current_project.UUID)
        context['vbdotnet_classes'] = query

        query = module_object.dotnet_components.filter(type = 'VBDOTNET_MODULE')
        # query = query.filter(project_model__UUID = self.request.user.projectuser.current_project.UUID)
        context['vbdotnet_modules'] = query 


        p = staticfiles_storage.path('Edag_Light_Cocoon/meta.json')
        f = open(p, "r")
        content = json.load(f)
        context['stl_file_list'] = json.dumps(content)
        f.close()
        p = staticfiles_storage.path('Edag_Light_Cocoon/preset_Ground.json')
        f = open(p, "r")
        content = json.load(f)
        context['preset_ground'] = json.dumps(content)
        f.close()

        context['html_dynamic_breadcrumb'] = format_html(dynamic_breadcrumb(module_object))

        return context   

def load_content(request):    
    '''View used to reload content in the dashboard
    '''

    trigger_id = request.GET['trigger_id']


    context={}
    data={}
    root_group = None

    #Button search was pressed (category tree)
    if trigger_id == 'search_submit':
        if request.method == 'GET' and 'object_name' in request.GET:
            object_name = request.GET['object_name'].strip()
            object_name =object_name[18:]
        else:
            object_name = None
             
        interactive_categories = {
            "TAILGATE": "512052b1-38df-4040-abdd-14edafc06b3e",
            "TUER": "421017fa-0519-41e3-bd32-9c57019a8e17"
        }
        category_id = interactive_categories[object_name]
        if object_name in interactive_categories.keys():
            current_category_group = DotNet_ProjectFolder.objects.filter(UUID =category_id).get()
        else:
            current_category_group = None
    #Button search  was pressed
    if trigger_id == 'search_component_submit':
    #Search in current category was pressed objects in currecnt category will be filtered using its name
        if request.method == 'GET' and 'search_text' in request.GET:
            object_name = request.GET['search_text'].strip()

        else:
            object_name = None
        if request.method == 'GET' and 'current_category' in request.GET:
            category_id = request.GET['current_category'].strip()

        else:
            category_id = None   
        current_category_group = DotNet_ProjectFolder.objects.filter(UUID = category_id)
        if current_category_group:
           current_category_group = current_category_group.get()            
        query = current_category_group.dotnet_components.filter(project_model__UUID = request.user.projectuser.current_project.UUID).filter(name__icontains = object_name )

        context['vbdotnet_modules'] = query.filter(type = 'VBDOTNET_MODULE') 
        data['html_list_vbdotnet_modules'] =render_to_string('CatiaFramework/database/list_shared_components/component_modules.html', context, request=request)  
        data['vbdotnet_modules_hits'] = len(context['vbdotnet_modules'] )

        context['vbdotnet_classes'] = current_category_group.dotnet_components.filter(type="VBDOTNET_CLASS")
        data['html_list_vbdotnet_classes'] =render_to_string('CatiaFramework/database/list_shared_components/component_classes.html', context, request=request)
        data['vbdotnet_classes_hits'] = len(context['vbdotnet_classes'] )

        context['vbdotnet_methods'] = current_category_group.dotnet_components.filter(type="VBDOTNET_SUB")
        data['html_list_vbdotnet_methods'] =render_to_string('CatiaFramework/database/list_shared_components/component_methods.html', context, request=request)
        data['vbdotnet_methods_hits'] = len(context['vbdotnet_methods'] )
        return JsonResponse(data)



    #Category card was clicked
    if trigger_id == 'switch_category':
        category_id = request.GET['category_id']
        current_category_group = DotNet_ProjectFolder.objects.filter(UUID = category_id).get()

    query = DotNet_ProjectFolder.objects.filter(parent_folder__UUID = category_id)
    context_category_groups={}
    context_category_groups['category_groups'] = query
    context_category_groups['category_group'] = current_category_group

    context_category_groups['html_dynamic_breadcrumb'] = format_html(dynamic_breadcrumb(current_category_group))
    data['html_category_groups'] =render_to_string('CatiaFramework/database/list_shared_components/cards_category_group_children.html', context_category_groups, request=request)
                
    query = current_category_group.dotnet_components.all() 
    #query = query.filter(project_model__UUID = request.user.projectuser.current_project.UUID)

    context['vbdotnet_modules'] = query.filter(type = 'VBDOTNET_MODULE') 
    data['html_list_vbdotnet_modules'] =render_to_string('CatiaFramework/database/list_shared_components/component_modules.html', context, request=request)  
    data['vbdotnet_modules_hits'] = len(context['vbdotnet_modules'] )

    context['vbdotnet_classes'] = query.filter(type="VBDOTNET_CLASS")
    data['html_list_vbdotnet_classes'] =render_to_string('CatiaFramework/database/list_shared_components/component_classes.html', context, request=request)
    data['vbdotnet_classes_hits'] = len(context['vbdotnet_classes'] )

    context['vbdotnet_methods'] = query.filter(type="VBDOTNET_SUB")
    data['html_list_vbdotnet_methods'] =render_to_string('CatiaFramework/database/list_shared_components/component_methods.html', context, request=request)
    data['vbdotnet_methods_hits'] = len(context['vbdotnet_methods'] )

    context['vbdotnet_libraries'] = query.filter(type="VBDOTNET_LIBRARY")
    data['html_list_vbdotnet_libraries'] =render_to_string('CatiaFramework/database/list_shared_components/component_libraries.html', context, request=request)
    data['vbdotnet_libraries_hits'] = len(context['vbdotnet_libraries'] )

    return JsonResponse(data)


def load_instance_content(request):    
    '''View used to reload content after instance was selected
    '''

    trigger_id = request.GET['trigger_id']


    context={}
    data={}
    root_group = None

 

    return JsonResponse(data)
