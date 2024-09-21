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
from .Views import *
from .Views.modal import *
from website.views.rooms import *
from django_keycloak.decorators import group_required, check_keycloak_status
from website.security.url_decorators_for_database_content import *
from NormMan.Views.modal.shared_component_modal import shared_component_create_modal, shared_component_modify_modal
from NormMan.Views.modal.norm_part_select_configuration_modal import load_configurations, norm_part_send_to_cad, norm_part_select_modal, norm_part_select_modal_config
from NormMan.Views.modal.norm_part_select_configuration_modal import propagate, load_content_shared_component_norm_parts_modal, norm_part_quick_position
from NormMan.Views.modal.shared_component_workflow import workflow_session_delete, workflow_session_update
from NormMan.Views.modal.shared_component_quick_position_modal import shared_component_quick_position_modal, shared_component_quick_position_callback, shared_component_quick_position_submit
from NormMan.scripts import user_required

app_name = "NormMan"
group_name ="/be_paramount/app-normman"

_auth = lambda f,required_groups = None, required_roles = None: group_required(check_keycloak_status(f), app_group=group_name,  group_names = required_groups, role_names = required_roles)
_project = lambda f, a=None, m=None, fi=None: _auth(project_security_check(f, app_name=a, model_name=m, field=fi))
_object = lambda f, a=None, m=None, fi=None: _auth(object_security_check(f, app_name=a, model_name=m, field=fi))
_owner = lambda f, a=None, m=None, fi=None: _auth(owner_security_check(f, app_name=a, model_name=m, field=fi))


urlpatterns = [

#Dashboard Shared_components
url(r'database/dashboard/(?P<uuid>[0-9a-f\-]{32,})$', _auth(shared_components_dashboard.as_view()), name ='shared_components_dashboard'), 
url(r'database/dashboard/$', _auth(shared_components_dashboard.as_view()), name ='shared_components_dashboard'), 
url(r'database/dashboard/filter$', _auth(filter_shared_component), name ='filter_shared_component'), 

#Dashboard Shared_components:Workflow
url(r'database/workflow/dashboard_redirect/(?P<uuid>[0-9a-f\-]{32,})&continue=(?P<continue>[^/]+) $', _auth(shared_component_workflow_redirect.as_view()), name ='shared_component_workflow'),
url(r'database/workflow/dashboard/(?P<uuid>[0-9a-f\-]{32,}) $', _auth(shared_component_workflow_session.as_view()), name ='shared_component_workflow_session'),  
url(r'database/workflow/index/(?P<uuid>[0-9a-f\-]{32,}) $', _auth(shared_component_workflow_index.as_view()), name ='shared_component_workflow_index'),  
url(r'database/workflow/index/update/(?P<uuid>[0-9a-f\-]{32,}) $', _auth(workflow_session_update), name ='shared_component_workflow_index_update'),  
url(r'database/workflow/index/delete/(?P<uuid>[0-9a-f\-]{32,}) $', _auth(workflow_session_delete), name ='shared_component_workflow_index_delete'),  
url(r'database/workflow/load-details/$', _auth(load_workflow_details), name='load_workflow_details'),
url(r'database/workflow/load_framework_status/$', _auth(load_framework_status), name='load_framework_status'),
url(r'^database/workflow/method/remove_object/$', _auth(RemoveObject), name='RemoveObject'),



url(r'^database/send_to_cad/method/$', _auth(MethodSendToFramework), name='MethodSendToFramework'),
url(r'testview/$', get_csrf_token, name='get_csrf_token'),
# url(r'testview/$', _auth(get_csrf_token), name='get_csrf_token'),


# url(r'index/shared_component/download_specific/(?P<uuid>[0-9a-t\-]{32,})$', _auth(NormPartDownloadSpecificView), name ='NormPartDownloadSpecificView'), 
# url(r'index/shared_component/download_specific/meta/(?P<uuid>[0-9a-t\-]{32,})$', _auth(NormPartDownloadSpecificMeta), name ='NormPartDownloadSpecificMeta'), 
# url(r'index/shared_component/download_specific/workflow/(?P<uuid>[0-9a-t\-]{32,})$', _auth(NormPartDownloadSpecificMeta), name ='NormPartDownloadSpecificMeta'), 
url(r'index/shared_component/download_specific/(?P<uuid>[0-9a-t\-]{32,})$', NormPartDownloadSpecificView, name ='NormPartDownloadSpecificView'), 
url(r'index/shared_component/download_specific/meta/(?P<uuid>[0-9a-t\-]{32,})$', NormPartDownloadSpecificMeta, name ='NormPartDownloadSpecificMeta'), 
url(r'index/shared_component/download_specific/workflow/(?P<uuid>[0-9a-t\-]{32,})$', NormPartDownloadSpecificMeta, name ='NormPartDownloadSpecificMeta'), 
url(r'index/shared_component/download_specific/framework_download/$', _auth(FrameworkDownload), name ='FrameworkDownload'),
url(r'^index/shared_component/configure_framework_download$', _auth(framework_download_modal), name='framework_download_modal'),


# url(r'index/shared_component/download_catia_part/(?P<uuid>[0-9a-f\-]{32,})$', _auth(NormPartDownloadView), name ='NormPartDownloadView'), 
url(r'index/shared_component/download_catia_part/(?P<uuid>[0-9a-f\-]{32,})$', NormPartDownloadView, name ='NormPartDownloadView'), 
# url(r'index/shared_component/download/(?P<uuid>[0-9a-f\-]{32,})$', NormPartSendToCAD, name ='NormPartSendToCAD'), 



url(r'^normpart/shared_component_quick_position/(?P<uuid>[0-9a-f\-]{32,})$', _auth(shared_component_quick_position_modal), name='shared_component_quick_position_modal'),
url(r'^normpart/shared_component_quick_position_callback/$', _auth(shared_component_quick_position_callback), name='shared_component_quick_position_callback'),
url(r'^normpart/shared_component_quick_position_submit/$', _auth(shared_component_quick_position_submit), name='shared_component_quick_position_submit'),


url(r'^normpart/select_modal/(?P<id>[0-9a-f\-]{32,})&(?P<uid>[0-9a-f\-]{32,})&(?P<wid>[0-9a-f\-]{32,})$', _auth(norm_part_select_modal), name='norm_part_select_modal'),
url(r'^normpart/select_modal_config/$', _auth(norm_part_select_modal_config), name='norm_part_select_modal_config'),
url(r'normpart/load-configurations/$', _auth(load_configurations), name='load_configurations'),
url(r'normpart/propagate/(?P<id>[0-9a-f\-]{32,})&(?P<uid>[0-9a-f\-]{32,})&(?P<wid>[0-9a-f\-]{32,})$', _auth(propagate), name='propagate'),
url(r'load-contents/$', _auth(load_content), name='load_content'),


#shared component model windows
url(r'^database/shared_component/create/$', _auth(shared_component_create_modal), name='shared_component_create_modal'),
url(r'^database/shared_component/modify/parent=(?P<parent>[0-9a-f\-]{32,})&uuid=(?P<uuid>[0-9a-f\-]{32,})$', _auth(shared_component_modify_modal), name='shared_component_modify_modal'),
url(r'^database/shared_component/(?P<uuid>[0-9a-f\-]{32,})$', _auth(shared_component_delete_modal), name='shared_component_delete_modal'),
url(r'database/shared_component/load-contents/$', _auth(load_content_shared_component_create_modal), name='load_content_shared_component_create_modal'),
url(r'database/shared_component/load-norm-parts/$', _auth(load_content_shared_component_norm_parts_modal), name='load_content_shared_component_norm_parts_modal'),
url(r'database/shared_component/load-norm-parts-on-demand/$', _auth(load_content_on_demand), name='load_content_on_demand'),
url(r'database/shared_component/apply-norm-part-position/$', _auth(norm_part_quick_position), name='norm_part_quick_position'),

]
