import time
import json, os
from django.contrib.staticfiles.storage import staticfiles_storage
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse   
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.utils.html import format_html
from django.views.generic import TemplateView
from NormMan.models import Component_Group_Level
from NormMan.forms import SharedComponentFilterForm
from .views import *
from .views import dynamic_breadcrumb
from website import settings


def create_root_component_group():
    root_component_group = Component_Group_Level.objects.create(UUID = 'fd9cea85-83d8-4a79-a1f1-22d1dd578516', 
                                                                name = 'ROOT', 
                                                                data_path = "norm_parts\\db_structure\\ROOT_UUID_fd9cea85-83d8-4a79-a1f1-22d1dd578516",
                                                                parent_group = None,
                                                                group_depth_level = 0)
    root_component_group.save()
    return root_component_group


class shared_components_dashboard(TemplateView):

    template_name = 'NormMan/normparts/shared_components_database_dashboard.html'
    category_group_object = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/user/login')
        return super().dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        i_uuid = kwargs.get('uuid', None)
        if i_uuid is not None:
            category_group_object = Component_Group_Level.objects.filter(UUID = i_uuid).get()
        else:
            category_group_object = Component_Group_Level.objects.filter(group_depth_level = 0).first()
        if category_group_object is None:
            category_group_object = create_root_component_group()
        context = super(shared_components_dashboard, self).get_context_data(**kwargs)
        filter_form = SharedComponentFilterForm()
        context['expiration_timestamp'] = self.request.session.get('expiration_timestamp', int(time.time()))
        context['filter_form'] = filter_form        

        #category_group_object = Component_Group_Level.objects.filter(group_depth_level = 0).first()
        context['category_group'] = category_group_object   

        query = Component_Group_Level.objects.filter(parent_group__UUID = category_group_object.UUID)          
        context['category_groups'] = query

        query_condition = Q(project_model__UUID = self.request.user.projectuser.current_project.UUID)| Q(accessibility = "DATABASE_USERS")

        query = category_group_object.normparts_shared_components.filter(type = 'COMPONENT') 
        context['components'] = query.filter(query_condition)

        query = category_group_object.normparts_shared_components.filter(type = 'PART')
        context['parts'] = query.filter(query_condition)

        query = category_group_object.normparts_shared_components.filter(type = 'SECTION')    
        context['sections'] = query.filter(query_condition)

        query = category_group_object.normparts_shared_components.filter(type = 'TEMPLATE')   
        context['templates'] = query.filter(query_condition)

        query = category_group_object.normparts_shared_components.filter(type = 'WORKFLOW')   
        context['workflows'] = query.filter(query_condition)


  

        p = os.path.join(category_group_object.data_path.path, "meta_threejs.json" ).replace("\\", "/")
        try:
            with open(p,"r") as f:
                content = json.load(f)
                context['json_tree'] = content
        except:
            context['json_tree'] = None

        # p = staticfiles_storage.path('Edag_Light_Cocoon/meta.json')
        # f = open(p, "r")
        # content = json.load(f)
        # stl_file_list = json.dumps(content)
        # stl_file_list_keys = stl_file_list.keys()
        # # Update file names to absolute file paths
        # for key in stl_file_list_keys:
        #     stl_file_list[f"/static/Edag_Light_Cocoon/{key}"] = stl_file_list.pop(key)
        # context['stl_file_list'] = json.dumps(content)
        # f.close()

        context['stl_file_list'] = static('Edag_Light_Cocoon/cocoon.glb')
        
        p = staticfiles_storage.path('Edag_Light_Cocoon/preset_Ground.json')
        f = open(p, "r")
        content = json.load(f)
        context['preset_ground'] = json.dumps(content)
        f.close()

        context['html_dynamic_breadcrumb'] = format_html(dynamic_breadcrumb(category_group_object))

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
        else:
            object_name = None
             
        interactive_categories = {
            "EDAG_Light_Cocoon_BONNET": "42a9b986-0313-43f4-8ef4-808b36caff85",
            "EDAG_Light_Cocoon_CANT_RAIL": "",
            "EDAG_Light_Cocoon_FRONT_BLADE": "fe818d55-9699-411b-b614-0bc783c38734",
            "EDAG_Light_Cocoon_FRONT_BUMPER": "fe818d55-9699-411b-b614-0bc783c38734",
            "EDAG_Light_Cocoon_FRONT_FENDER": "a4f40e58-011a-4705-9576-62d709714a5e",
            "EDAG_Light_Cocoon_FRONT_LIGHT": "cf0101b6-70f4-4a01-b725-e0fae216a70c",
            "EDAG_Light_Cocoon_FRONT_LOGO": "1ef854c5-e722-4ccf-9795-63d4216fda45",
            "EDAG_Light_Cocoon_FRONT_RIM": "",
            "EDAG_Light_Cocoon_FRONT_TYRE": "",
            "EDAG_Light_Cocoon_FRONT_WHEEL_ARCH": "a4f40e58-011a-4705-9576-62d709714a5e",
            "EDAG_Light_Cocoon_GLASS_TAILGATE": "c7ca6544-cdb3-4ed3-9974-ef23f7e3fc95",
            "EDAG_Light_Cocoon_LIGHT_TAILGATE": "",
            "EDAG_Light_Cocoon_REAR_BUMPER": "98513686-9c0c-45a7-9251-66a9b90c7303",
            "EDAG_Light_Cocoon_REAR_DIFFUSOR": "",
            "EDAG_Light_Cocoon_REAR_FENDER": "29aff851-b584-4a29-af47-8b97bb295ebb",
            "EDAG_Light_Cocoon_REAR_LIGHT": "2cc244ca-c52e-43e3-b2af-bba9e6a36992",
            "EDAG_Light_Cocoon_REAR_LOGO": "1ef854c5-e722-4ccf-9795-63d4216fda45",
            "EDAG_Light_Cocoon_REAR_RIM": "",
            "EDAG_Light_Cocoon_REAR_TYRE": "",
            "EDAG_Light_Cocoon_REAR_WHEEL_ARCH": "29aff851-b584-4a29-af47-8b97bb295ebb",
            "EDAG_Light_Cocoon_ROOF": "a41403b0-2c96-4b40-9a4c-ebbc94eb8c94",
            "EDAG_Light_Cocoon_SCHEIBEN_TUER": "",
            "EDAG_Light_Cocoon_TAILGATE": "512052b1-38df-4040-abdd-14edafc06b3e",
            "EDAG_Light_Cocoon_TUER": "11d80763-afcd-40c9-a842-23f1c63ddfe8",
            "EDAG_Light_Cocoon_WINDSCHIELD": "baaef9d9-3f40-452c-a5e6-7cc2ab4e0119"
        }
        if object_name and object_name in interactive_categories.keys() and interactive_categories[object_name]:
            category_id = interactive_categories[object_name]
            current_category_group = Component_Group_Level.objects.filter(UUID = category_id).get()
        else:
            current_category_group = Component_Group_Level.objects.filter(group_depth_level = 0).first()
    #Button search  was pressed
    elif trigger_id == 'search_component_submit':
    #Search in current category was pressed objects in currecnt category will be filtered using its name
        if request.method == 'GET' and 'search_text' in request.GET:
            object_name = request.GET['search_text'].strip()

        else:
            object_name = None
        if request.method == 'GET' and 'current_category' in request.GET:
            category_id = request.GET['current_category'].strip()

        else:
            category_id = None   
        current_category_group = Component_Group_Level.objects.filter(UUID = category_id)
        if current_category_group:
           current_category_group = current_category_group.get()            
        
        query = current_category_group.normparts_shared_components.filter(project_model__UUID = request.user.projectuser.current_project.UUID).filter(name__icontains = object_name )
        context['components'] = query.filter(type = 'COMPONENT') 
        data['html_list_vehicle_components'] =render_to_string('NormMan/normparts/submenus/accordion_vehicle_components.html', context, request=request)  
        data['vehicle_components_hits'] = len(context['components'] )

        context['parts'] = query.filter(type = 'PART') 
        data['html_list_norm_parts'] =render_to_string('NormMan/normparts/submenus/accordion_norm_parts.html', context, request=request)
        data['norm_parts_hits'] = len(context['parts'] )

        context['templates'] = query.filter(type="TEMPLATE")
        data['html_list_templates'] =render_to_string('NormMan/normparts/list_shared_components/shared_component_templates.html', context, request=request)
        data['templates_hits'] = len(context['templates'] )
        
        context['sections'] = query.filter(type = 'SECTION') 
        data['html_list_sections'] =render_to_string('NormMan/normparts/list_shared_components/shared_component_sections.html', context, request=request)
        data['sections_hits'] = len(context['sections'] )

        context['workflows'] = query.filter(type="WORKFLOW")
        data['html_list_workflows'] =render_to_string('NormMan/normparts/list_shared_components/shared_component_workflows.html', context, request=request)
        data['workflows_hits'] = len(context['workflows'] )
        return JsonResponse(data)
    
    #Category card was clicked
    elif trigger_id == 'switch_category':
        category_id = request.GET['category_id']
        current_category_group = Component_Group_Level.objects.filter(UUID = category_id).get()


    query_condition = Q(project_model__UUID = request.user.projectuser.current_project.UUID)| Q(accessibility = "DATABASE_USERS")
    category_id = current_category_group.UUID
    query = Component_Group_Level.objects.filter(parent_group__UUID = category_id)
    context_category_groups={}
    context_category_groups['category_groups'] = query
    context_category_groups['category_group'] = current_category_group

    context_category_groups['html_dynamic_breadcrumb'] = format_html(dynamic_breadcrumb(current_category_group))
    data['html_category_groups'] =render_to_string('NormMan/normparts/list_shared_components/cards_category_group_children.html', context_category_groups, request=request)
                
    query = current_category_group.normparts_shared_components.filter(type = 'COMPONENT') 
    context['components'] = query.filter(query_condition)
    render = render_to_string('NormMan/normparts/submenus/accordion_vehicle_components.html', context, request=request)
    data['html_list_vehicle_components'] = "\n".join(str(r) for r in render.split("\n")[27:-3])
    data['vehicle_components_hits'] = len(context['components'] )

    query = current_category_group.normparts_shared_components.filter(type = 'PART')
    context['parts'] = query.filter(query_condition)
    render = render_to_string('NormMan/normparts/submenus/accordion_norm_parts.html', context, request=request)    
    data['html_list_norm_parts'] = "\n".join(str(r) for r in render.split("\n")[27:-3])
    data['norm_parts_hits'] = len(context['parts'] )


    query = current_category_group.normparts_shared_components.filter(type = 'TEMPLATE')     
    context['templates'] = query.filter(query_condition)
    data['html_list_templates'] =render_to_string('NormMan/normparts/list_shared_components/shared_component_templates.html', context, request=request)
    data['templates_hits'] = len(context['templates'] )
    
    query = current_category_group.normparts_shared_components.filter(type = 'SECTION')    
    context['sections'] = query.filter(query_condition)
    data['html_list_sections'] =render_to_string('NormMan/normparts/list_shared_components/shared_component_sections.html', context, request=request)
    data['sections_hits'] = len(context['sections'] )

    context['workflows'] = current_category_group.normparts_shared_components.filter(type="WORKFLOW")
    data['html_list_workflows'] =render_to_string('NormMan/normparts/list_shared_components/shared_component_workflows.html', context, request=request)
    data['workflows_hits'] = len(context['workflows'] )


    if root_group:
        p = os.path.join( settings.MEDIA_ROOT, root_group.data_path.name, "meta_threejs.json" )
        f = open(p, "r")    
        content = json.load(f)
        data['json_tree'] = content
    else:
        data['json_tree'] = {}
    return JsonResponse(data)


def load_content_on_demand(request):
    '''
    Here goes a description
    '''
    context={}
    data={}
    root_group = None

    category_id = request.POST['category_id']
    current_category_group = Component_Group_Level.objects.filter(UUID = category_id).get()

    query = Component_Group_Level.objects.filter(parent_group__UUID = category_id)
    context_category_groups={}
    context_category_groups['category_groups'] = query
    context_category_groups['category_group'] = current_category_group

    data['html_category_groups'] =render_to_string('NormMan/normparts/list_shared_components/cards_category_group_children.html', context_category_groups, request=request)
                
    context['components'] = current_category_group.normparts_shared_components.filter(type="COMPONENT")
    data['html_list_vehicle_components'] =render_to_string('NormMan/normparts/list_shared_components/shared_component_components.html', context, request=request)  
    data['vehicle_components_hits'] = len(context['components'] )

    context['parts'] = current_category_group.normparts_shared_components.filter(type="PART")
    data['html_list_norm_parts'] =render_to_string('NormMan/normparts/list_shared_components/shared_component_parts.html', context, request=request)
    data['norm_parts_hits'] = len(context['parts'] )

    context['templates'] = current_category_group.normparts_shared_components.filter(type="TEMPLATE")
    data['html_list_templates'] =render_to_string('NormMan/normparts/list_shared_components/shared_component_templates.html', context, request=request)
    data['templates_hits'] = len(context['templates'] )
    
    context['sections'] = current_category_group.normparts_shared_components.filter(type="SECTION")
    data['html_list_sections'] =render_to_string('NormMan/normparts/list_shared_components/shared_component_sections.html', context, request=request)
    data['sections_hits'] = len(context['sections'] )

    context['workflows'] = current_category_group.normparts_shared_components.filter(type="WORKFLOW")
    data['html_list_workflows'] =render_to_string('NormMan/normparts/list_shared_components/shared_component_workflows.html', context, request=request)
    data['workflows_hits'] = len(context['workflows'] )

    if root_group:
        p = os.path.join(MEDIA_ROOT, root_group.data_path.name, "meta_threejs.json" )
        f = open(p, "r")    
        content = json.load(f)
        data['json_tree'] = content
    else:
        data['json_tree'] = None
    return JsonResponse(data)

def filter_shared_component(request):
    from NormMan.forms import SharedComponentFilterForm
    if request.user.is_authenticated == True:
        if request.method == 'POST':            
            form = SharedComponentFilterForm(request.POST)  
            query = Q()
            for field in form:
                field_value = field.data
                if field_value is not None and field_value != '' and field.name != 'search_policy':
                    if form.data.get('search_policy') == 'OR':
                        query |= Q(**{field.name: field_value})
                    if form.data.get('search_policy') == 'AND':
                        query &= Q(**{field.name: field_value})
            queried_objects = NormParts_Shared_Component.objects.filter(query)
        else:
            pass
    # return redirect('/shared_components/database/dashboard/filter_result')
    context = {
        'form': form,        
        'parts': queried_objects,
        }
    data = {
        'form_is_valid': True if request.method == 'POST' else False,
        'html_form': render_to_string('modal/shared_component_filter/static_shared_component_select.html', context, request=request)
    }
    return JsonResponse(data)