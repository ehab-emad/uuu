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
from .Views.views import *
from .Views import *
from .Views.modal import *

app_name = "ConceptMan"
group_name = "/be_paramount/app-conceptman"

_auth = lambda f,required_groups = None, required_roles = None: group_required(check_keycloak_status(f), app_group=group_name,  group_names = required_groups, role_names = required_roles)
_project = lambda f, a=None, m=None, fi=None: _auth(project_security_check(f, app_name=a, model_name=m, field=fi))
_object = lambda f, a=None, m=None, fi=None: _auth(object_security_check(f, app_name=a, model_name=m, field=fi))
_owner = lambda f, a=None, m=None, fi=None: _auth(owner_security_check(f, app_name=a, model_name=m, field=fi))




urlpatterns = [

    #part
    url(r'^part/create/$', _auth(part_create), name='part_create'),
    url(r'^part/(?P<pk>[0-9]+)/update/$', _auth(part_update), name='part_update'),
    url(r'^part/(?P<pk>[0-9]+)/delete/$', _auth(part_delete), name='part_delete'),

    #concept
    url(r'^concept/create/$', _auth(concept_create), name='concept_create'),
    url(r'^concept/(?P<pk>[0-9]+)/update/$', _auth(concept_update), name='concept_update'),
    url(r'^concept/(?P<pk>[0-9]+)/delete/$', _auth(concept_delete), name='concept_delete'),

    url(r'vehicles/$', _auth(index_vehicle.as_view()), name ='index_vehicle'),
    url(r'vehicle/(?P<pk>[0-9]+)/concepts/$', _auth(index_concept.as_view()), name ='index_concept'),

    #/conceptdetail/  
    url(r'conceptdetail/(?P<pk>[0-9]+)/partindex/$', _auth(ConceptDetailView_Part.as_view()), name ='conceptdetail_part'),   
    url(r'conceptdetail/(?P<pk>[0-9]+)/materialindex/$', _auth(ConceptDetailView_Engineering_Material.as_view()), name ='conceptdetail_engineering_material'),     
    url(r'conceptdetail/(?P<pk>[0-9]+)/boltcaseindex/$', _auth(ConceptDetailView_Bolt_Case.as_view()), name ='conceptdetail_bolt_case'),     

    url(r'^parts/(?P<pk>[0-9]+)/detail/$', _auth(PartDetailView.as_view()), name ='part_detailview'),
    url(r'^parts/(?P<pk>[0-9]+)/detail/select/manufacturingprocess/$', _auth(part_manufacturingprocess), name ='part_select_manufacturingprocess'),

]                                