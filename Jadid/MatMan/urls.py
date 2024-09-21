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
from django_keycloak.decorators import group_required, check_keycloak_status
from website.security.url_decorators_for_database_content import *
from .Views import *
from .Views.modal import *

app_name = "MatMan"
group_name ="/be_paramount/app-matman"
_auth = lambda f,required_groups = None, required_roles = None: group_required(check_keycloak_status(f), app_group=group_name,  group_names = required_groups, role_names = required_roles)
_project = lambda f, a=None, m=None, fi=None: _auth(project_security_check(f, app_name=a, model_name=m, field=fi))
_object = lambda f, a=None, m=None, fi=None: _auth(object_security_check(f, app_name=a, model_name=m, field=fi))
_owner = lambda f, a=None, m=None, fi=None: _auth(owner_security_check(f, app_name=a, model_name=m, field=fi))

_auth = lambda f: group_required(f, group_name = "/be_paramount/app-matman")

urlpatterns = [


url(r'index/$', _auth(index.as_view()), name ='index_materialgroups'),
url(r'index/materialgroups/metals$', _auth(index_metals.as_view()), name ='index_metals'),

url(r'index/materialgroups/metals/ferrous/$', _auth(MetalFerrousListView.as_view()), name ='list_metalferrous'),   
url(r'index/materialgroups/metals/nonferrous/$', _auth(MetalNonFerrousListView.as_view()), name ='list_metalnonferrous'),   
url(r'index/materialgroups/plastic/$', _auth(PlasticListView.as_view()), name ='list_plastic'),  
url(r'index/materialgroups/ceramic/$', _auth(CeramicListView.as_view()), name ='list_ceramic'),  
url(r'index/materialgroups/composite/$', _auth(CompositeListView.as_view()), name ='list_composite'),  
url(r'index/materialgroups/special/$', _auth(SpecialListView.as_view()), name ='list_special'),  

#engineering_material
url(r'^engineering_material/create/$', _auth(EngineeringMaterial_create), name='engineeringmaterial_create'),
url(r'^engineering_material/(?P<pk>[0-9]+)/update/$', _auth(EngineeringMaterial_update), name='engineeringmaterial_update'),
url(r'^engineering_material/(?P<pk>[0-9]+)/delete/$', _auth(EngineeringMaterial_delete), name='engineeringmaterial_delete'),



url(r'^engineering_material/(?P<pk>[0-9]+)/detail/$', _auth(EngineeringMaterialDetailView.as_view()), name ='engineeringmaterial_detailview'),

]
