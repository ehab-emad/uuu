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
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django_keycloak.decorators import group_required, check_keycloak_status
from django_keycloak.keycloak_manager import keycloak_manager
from django.urls import path, include
from django.urls import re_path as url
from django.views.generic import TemplateView
from website.views import *
from website.views.modal import *
from CatiaFramework.urls.urls_main import urls_modal

from website.security.url_decorators_for_database_content import *

admin.site.site_header = 'BE PARAMOUNT admin page'                    # default: "Django Administration"
admin.site.index_title = 'Features area'                 # default: "Site administration"
admin.site.site_title = 'HTML title from adminsitration' # default: "Django site admin"


# group_name_professional ="/be_paramount/user-professional"
group_name ="/be_paramount"
app_name = 'website'
_auth = lambda f,required_groups = None, required_roles = None: group_required(check_keycloak_status(f), app_group=group_name,  group_names = required_groups, role_names = required_roles)
_project = lambda f, a=None, m=None: _auth(project_security_check(f, app_name=a, model_name=m))
_object = lambda f, a=None, m=None: _auth(object_security_check(f, app_name=a, model_name=m))
_owner = lambda f, a=None, m=None: _auth(owner_security_check(f, app_name=a, model_name=m))





'''
LOAD appurlspatterns based on configured system (env file)
'''

app_url_patterns = list()

for app in settings.GROUPS.values():
    match app:
        case 'boltman':
            app_url_patterns.append(path('bolt/', include('BoltMan.urls')))
        case 'matman':
            app_url_patterns.append(path('material/', include('MatMan.urls')))
        case 'conceptman':
            app_url_patterns.append(path('concept/', include('ConceptMan.urls')))            
        case 'ecoman':
            app_url_patterns.append(path('qlca/', include('EcoMan.urls')))
        case 'catfrm':
            app_url_patterns.append(path('catiaframework/', include('CatiaFramework.urls')),)
        case 'normman':
            app_url_patterns.append(path('shared_components/', include('NormMan.urls')))


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', redirect_to_home, name='redirect_to_home'),
    url(r'home/$', _auth(index.as_view()), name ='home'),
    url(r'err/not_in_group$', TemplateView.as_view(template_name='website/not_in_group_err.html'), name ='not_in_group'),
    url(r'err/account_expired$', TemplateView.as_view(template_name='website/account_expired_err.html'), name ='account_expired'),

    # Application views
    # ToDo: Separate for future

    # Project
    url(r'^project/create/$', _auth(project_create, required_roles=["edag_worker"], ), name='project_create'),
    url(r'^project/(?P<uuid>[0-9a-t\-]{32,})/update/$', _auth(project_update), name='project_update'),
    url(r'^project/(?P<uuid>[0-9a-t\-]{32,})/delete/$', _auth(project_delete), name='project_delete'),
    # Vehicle
    url(r'^vehicles/create/$', _auth(vehicle_create), name='vehicle_create'),
    url(r'^vehicles/(?P<uuid>[0-9a-t\-]{32,})/update/$', _auth(vehicle_update), name='vehicle_update'),
    url(r'^vehicles/(?P<uuid>[0-9a-t\-]{32,})/delete/$', _auth(vehicle_delete), name='vehicle_delete'),
    # Production rate
    url(r'^production_rate/(?P<pk>[0-9]+)/update/$', _auth(production_rate_update), name='production_rate_update'),
    # Userproject
    url(r'^project_user_update/(?P<uuid>[0-9a-t\-]{32,})/update/$', _auth(project_user_update), name='project_user_update'),
    url(r'^project_user_select_current_project/(?P<uuid>[0-9a-t\-]{32,})/update/$', _auth(project_user_select_current_project, required_roles=["edag_worker"]), name='project_user_select_current_project'),
    url(r'^project_update_authorised_users/(?P<uuid>[0-9a-t\-]{32,})/update/$', _auth(project_update_authorised_users, required_roles=["edag_worker"]), name='project_update_authorised_users'),
    # Info modal
    url(r'^info/concept/$', _auth(info_concept), name='info_concept'),
    url(r'load-project-users/$', _auth(load_project_users), name='load_project_users'),
    
    #Token
    url(r'^tokens/create/component_uuid:(?P<uuid_component>[0-9a-t\-]{32,})$', _auth(token_create_modal), name='token_create_modal'),


    # Websocket
    path('rooms/', index_view, name='chat-index'),
    path('rooms/<str:room_name>/', room_view, name='chat-room'),
    # Keycloak redirect from all application endpoints
    path('user/login/', lambda request: redirect(f"{request.scheme}://{request.headers['Host']}/keycloak/login"), name='login_redirect'),
    path('keycloak/login/', keycloak_manager.keycloak_admin_redirect, name='keycloak_admin_redirect'),
    # Keycloak login
    path('home/keycloak/expired_login/', keycloak_manager.expired_login, name='expired_login'),    
    path('keycloak/login/callback/', keycloak_manager.keycloak_login, name='keycloak_login'),
    path('keycloak/logout/', keycloak_manager.keycloak_logout, name='keycloak_logout'),    

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  +static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + app_url_patterns
