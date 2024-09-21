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
from django.urls import path
from django_keycloak.decorators import group_required, check_keycloak_status
from website.security.url_decorators_for_database_content import *
group_name ="/be_paramount/app-catiaframework"
_auth = lambda f,required_groups = None, required_roles = None: group_required(check_keycloak_status(f), app_group=group_name,  group_names = required_groups, role_names = required_roles)

urlpatterns = [

    #Workflow Object Update
    url(r'database/workflow/index/update/(?P<uuid>[0-9a-f\-]{32,})$', _auth(workflow_update), name ='workflow_update'),  
    url(r'database/workflow/index/delete/(?P<uuid>[0-9a-f\-]{32,})$', _auth(workflow_delete), name ='workflow_delete'), 
    url(r'workflow/redirect:(?P<redirect>True|False)/create/', _auth(workflow_create_modal), name='workflow_create_modal'), 

    #Workflow Object Update
    url(r'database/workflow_session/index/update/(?P<uuid>[0-9a-f\-]{32,})$', _auth(workflow_session_update), name ='workflow_session_update'),  
    url(r'database/workflow_session/index/delete/(?P<uuid>[0-9a-f\-]{32,})$', _auth(workflow_session_delete), name ='workflow_session_delete'), 
    #url(r'workflow/redirect:(?P<redirect>True|False)/create/', workflow_create_modal, name='workflow_create_modal'), 

    #Stage
    url(r'^stage/create/$', _auth(workflow_stage_create_modal), name='workflow_stage_create_modal'),
    url(r'^stage/create/workflow:(?P<uuid_workflow>[0-9a-f\-]{32,})/$', _auth(workflow_stage_create_modal), name='workflow_stage_create_modal'),
    url(r'^stage/(?P<uuid_stage>[0-9a-f\-]{32,})/update/$', _auth(workflow_stage_update_modal), name='workflow_stage_update_modal'),
    url(r'^stage/(?P<uuid_stage>[0-9a-f\-]{32,})/delete/$', _auth(workflow_stage_delete_modal), name='workflow_stage_delete_modal'),

    #Action_Stage
    url(r'^action_stage/create/target_stage:(?P<uuid_stage>[0-9a-f\-]{32,})/$', _auth(workflow_stage_action_create_modal), name='workflow_stage_action_create_modal'),
    url(r'^action_stage/(?P<uuid_action>[0-9a-f\-]{32,})/update/$', _auth(workflow_stage_action_update_modal), name='workflow_stage_action_update_modal'),
    url(r'^action_stage/(?P<uuid_action>[0-9a-f\-]{32,})/delete/$', _auth(workflow_stage_action_delete_modal), name='workflow_stage_action_delete_modal'),
    url(r'^action_stage/load_content_stage_action/$', _auth(load_content_stage_action_create_modal), name='load_content_stage_action_create_modal'),    


    #Action_Object
    url(r'^action_object/create/target_object:(?P<uuid_object>[0-9a-f\-]{32,})/$', _auth(workflow_object_action_create_modal), name='workflow_object_action_create_modal'),
    url(r'^action_object/(?P<uuid_action>[0-9a-f\-]{32,})/update/$', _auth(workflow_object_action_update_modal), name='workflow_object_action_update_modal'),
    url(r'^action_object/(?P<uuid_action>[0-9a-f\-]{32,})/delete/$', _auth(workflow_object_action_delete_modal), name='workflow_object_action_delete_modal'),
    url(r'^action_object/load_content_action/$', _auth(load_content_object_action_create_modal), name='load_content_object_action_create_modal'), 

    url(r'^action_object/shared_component_select_modal/$', _auth(static_shared_component_select), name='static_shared_component_select'),
    url(r'^action_object/shared_component_propagate_modal/$', _auth(static_shared_component_propagate), name='static_shared_component_propagate'),
    url(r'^action_object/shared_component_reload_modal/$', _auth(static_shared_component_reload), name='static_shared_component_reload'),


    #Session
    
    url(r'^session/(?P<uuid_session>[0-9a-f\-]{32,})/delete/$', _auth(workflow_session_reset_modal), name='workflow_session_reset_modal'),


    #Object Template
    
    url(r'^object_template/(?P<uuid_object>[0-9a-f\-]{32,})/delete/$', _auth(workflow_object_delete_all_instances_modal), name='workflow_object_delete_all_instances_modal'),

    #Object
    url(r'^object/create/$', _auth(workflow_object_create_modal), name='workflow_object_create_modal'),
    url(r'^object/create/stage:(?P<uuid_stage>[0-9a-f\-]{32,})/$', _auth(workflow_object_create_modal), name='workflow_object_create_modal'),
    url(r'^object/(?P<uuid_object>[0-9a-f\-]{32,})/update/$', _auth(workflow_object_update_modal), name='workflow_object_update_modal'),
    url(r'^object/(?P<uuid_object>[0-9a-f\-]{32,})/delete/$', _auth(workflow_object_delete_modal), name='workflow_object_delete_modal'),    
    url(r'^object/shared_component_select_modal/(?P<object_id>[0-9a-f\-]{32,})&(?P<instance_id>[0-9a-f\-]{32,})$', _auth(shared_component_select), name='shared_component_select'),
    url(r'^object/shared_component_propagate_modal/$', _auth(shared_component_propagate), name='shared_component_propagate'),
    url(r'^object/shared_component_reload_modal/$', _auth(shared_component_reload), name='shared_component_reload'),

    #Instance
    url(r'^instance/create/object:(?P<uuid_object_template>[0-9a-f\-]{32,})/session:(?P<uuid_current_session>[0-9a-f\-]{32,})$', _auth(workflow_object_instance_create_modal), name='workflow_object_instance_create_modal'),
    url(r'^instance/update/object:(?P<uuid_object_instance>[0-9a-f\-]{32,})/$', _auth(workflow_object_instance_update_modal), name='workflow_object_instance_update_modal'),
    url(r'^instance/delete/object:(?P<uuid_object_instance>[0-9a-f\-]{32,})/$', _auth(workflow_object_instance_delete_modal), name='workflow_object_instance_delete_modal'),
    url(r'^instance/create/next_tab/$', _auth(workflow_object_instance_next_tab), name='workflow_object_instance_next_tab'),
    url(r'^instance/create/breadcrumb_tab_selection/$', _auth(workflow_object_select_tab), name='workflow_object_select_tab'),


    #Instruction
    url(r'^instruction/(?P<uuid_instruction>[0-9a-f\-]{32,})/update/$', _auth(workflow_instruction_update_modal), name='workflow_instruction_update_modal'),

    #Stage Action Execution Override Parameters
    url(r'^action_stage/execute/$', _auth(workflow_stage_action_execute_modal), name='workflow_stage_action_execute_modal'),    

    #Stage Action Execution Select Instance from required object
    #url(r'^action_stage/execute/$', workflow_stage_action_select_instance, name='workflow_stage_action_select_instance'),    

    #Object Action Execution Override Parameters
    url(r'^action_object/execute/$', _auth(workflow_object_action_execute_modal), name='workflow_object_action_execute_modal'), 

    #DotNet library
   # url(r'^database/shared_component/create/$', _auth(dotnet_library_create_modal), name='dotnet_library_create_modal'),

]