"""website URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import re_path as url
from CatiaFramework.Views import *
from CatiaFramework.Views.modal import *
from website.views.rooms import *
from django.urls import path
from django.conf.urls.static import static
from CatiaFramework.urls.urls_modal import urlpatterns as urls_modal
from django_keycloak.decorators import group_required, check_keycloak_status
from website.security.url_decorators_for_database_content import *
app_name = "CatiaFramework"
group_name ="/be_paramount/app-catiaframework"

_auth = lambda f,required_groups = None, required_roles = None: group_required(check_keycloak_status(f), app_group=group_name,  group_names = required_groups, role_names = required_roles)
_project = lambda f, a=None, m=None: _auth(project_security_check(f, app_name=a, model_name=m))
_object = lambda f, a=None, m=None: _auth(object_security_check(f, app_name=a, model_name=m))
_owner = lambda f, a=None, m=None: _auth(owner_security_check(f, app_name=a, model_name=m))
urlpatterns = [



   #Main index

    url(r'index/$', _auth(index.as_view()), name ='index'),


    ##DotNet Functionality Database
    #Main Dashboard
    url(r'database/methods/dashboard/(?P<uuid_session>[0-9a-f\-]{32,})$', _auth(database_dashboard.as_view()), name ='database_dashboard'), 
    #Main Dashboard
    url(r'database/methods/dashboard/$', _auth(database_dashboard.as_view()), name ='database_dashboard'), 
    #Dashboard Details Ajax Request
    url(r'database/methods/load-contents/$', _auth(load_content), name='load_content'),
    ##Import Database from JSON
    url(r'^database/methods/json_import/$', _auth(vb_project_import), name='vb_project_import'),
    #Component Detail View
    url(r'^database/vbdotnet_component/details/(?P<pk>[0-9a-f\-]{32,})$', _auth(vbdotnet_component_detail_view.as_view(model = DotNet_Component)), name='vbdotnet_component_detail_view'),


    #WORKFLOW SESSION

    #Create new Session
    url(r'database/workflow/dashboard_session_create/(?P<uuid_reference_workflow>[0-9a-f\-]{32,})$', _auth(workflow_session_create), name ='workflow_session_create'), 
    #Continue Session
    url(r'database/workflow/dashboard_session_continue/(?P<uuid_reference_workflow>[0-9a-f\-]{32,})$', _auth(workflow_session_continue), name ='workflow_session_continue'), 
    #Continue Last Session
    url(r'database/workflow/dashboard_session_continue_last/(?P<uuid_workflow>[0-9a-f\-]{32,})$$', _auth(workflow_session_continue_last), name ='workflow_session_continue_last'), 
    #Continue Session
    url(r'database/workflow/dashboard_session_review/(?P<uuid_instance>[0-9a-f\-]{32,})$', _auth(workflow_session_redirect_on_instance), name ='workflow_session_redirect_on_instance'), 
    #WORKFLOW

    #Worflow configure without a session
    url(r'database/workflow/workflow_configurator/worfklow_(?P<uuid_workflow>[0-9a-f\-]{32,})/editor_mode:(?P<editor_mode>True|False)/$', _auth(workflow_configurator.as_view()), name ='workflow_configurator'),
    #Worflow configure with a session
    url(r'database/workflow/workflow_configurator/worfklow_(?P<uuid_workflow>[0-9a-f\-]{32,})/session_(?P<uuid_session>[0-9a-f\-]{32,})/editor_mode:(?P<editor_mode>True|False)/$', _auth(workflow_configurator.as_view()), name ='workflow_configurator'),

    #Worflow dashboard     
    url(r'database/workflow/workflow_dashboard/session_(?P<uuid_session>[0-9a-f\-]{32,})/editor_mode:(?P<editor_mode>True|False)/$', _auth(workflow_dashboard.as_view()), name ='workflow_dashboard'), 
    url(r'database/workflow/workflow_dashboard_react/session_(?P<uuid_workflow>[0-9a-f\-]{32,})/editor_mode:(?P<editor_mode>True|False)/$', _auth(workflow_dashboard_react.as_view()), name ='workflow_dashboard_react'), 

    
    #Workflow Index (Official)
    url(r'database/workflow/index/$', _auth(workflow_index.as_view()), name ='workflow_index'),  
    #Workflow Session Index (User)
    url(r'database/workflow_session/index/$', _auth(workflow_session_index.as_view()), name ='workflow_session_index'),  

    #Workflow Details Ajax Request
    url(r'database/workflow/load-details/$', _auth(load_workflow_session_details), name='load_workflow_session_details'),
    #Framework Status Ajax Request
    url(r'database/workflow/load_framework_status/$', _auth(load_framework_status), name='load_framework_status'),


    #Workflow dashboard
    url(r'database/workflow/instruction_load_hover/$', _auth(instruction_load_hover), name='instruction_load_hover'), 
    url(r'database/workflow/dashboard_switch_edit_configure/(?P<uuid_workflow>[0-9a-f\-]{32,})/(?P<uuid_session>[0-9a-f\-]{32,})/(?P<editor_mode>True|False)/$', _auth(dashboard_switch_edit_configure), name='dashboard_switch_edit_configure'), 
    #this view will be triggered when used hits the instance
    url(r'database/workflow/load_instance_content/$', _auth(load_instance_content), name='load_instance_content'), 
    url(r'database/workflow/create_new_instance/$', _auth(create_new_instance), name='create_new_instance'), 
    url(r'database/workflow/instance_delete_modal/(?P<uuid_instance>[0-9a-f\-]{32,})$', _auth(instance_delete_modal), name='instance_delete_modal'), 
    
                               

    #Framework
    url(r'workflow/get_main_object/(?P<uuid_instance>[0-9a-f\-]{32,})$', _auth(get_main_object), name='get_main_object'), # -> currently debugging
    url(r'workflow/execute_object_action/$', _auth(execute_object_action), name='execute_object_action'),
    url(r'workflow/execute_stage_action/$', _auth(execute_stage_action), name='execute_stage_action'),
    url(r'^workflow/stage_tree_reorder/$', _auth(stage_tree_reorder), name='stage_tree_reorder'),
    url(r'^workflow/object_actions_reorder/$', _auth(object_actions_reorder), name='object_actions_reorder'),
    url(r'^workflow/objects_reorder/$', _auth(objects_reorder), name='objects_reorder'),
    url(r'^workflow/save_instance_parameters/(?P<instance_uuid>[0-9a-f\-]{32,})$', _auth(save_instance_parameters), name='save_instance_parameters'),

    #Franework Instance File Handling - Upload/Download
    url(r'workflow/custom_file_upload', custom_file_upload, name='custom_file_upload'),
    url(r'workflow/instance_upload_catia_file', instance_upload_file, name='instance_upload_file'),
    url(r'workflow/instance_download_catia_file/uuid_instance=(?P<uuid_instance>[0-9a-f\-]{32,})$', instance_download_file, name='instance_download_file'),
    url(r'workflow/instance_download_catia_file_internal/uuid_instance=(?P<uuid_instance>[0-9a-f\-]{32,})$', _auth(instance_download_file_internal), name='instance_download_file_internal'),

    
    #print pdf report
    url(r'^session/(?P<uuid_session>[0-9a-f\-]{32,})/print/$', _auth(print_session_report), name='print_session_report'),


    #upload tesst
    url(r'upload/', _auth(upload_file), name='upload_file'),
    url(r'success/', _auth(upload_success), name='upload_success')


    ]+static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 



urlpatterns += urls_modal