from website.settings import STATIC_URL

from django.urls import re_path as url
from django.conf import settings
from django.urls import re_path
from django.views.static import serve
from BoltMan.views import *
from BoltMan.views import database
from django_keycloak.decorators import group_required,  check_keycloak_status
from website.security.url_decorators_for_database_content import *

app_name = 'BoltMan'
group_name ="/be_paramount/app-boltman"
_auth = lambda f,required_groups = None, required_roles = None: group_required(check_keycloak_status(f), app_group=group_name,  group_names = required_groups, role_names = required_roles)
_project = lambda f, a=None, m=None, fi=None: _auth(project_security_check(f, app_name=a, model_name=m, field=fi))
_object = lambda f, a=None, m=None, fi=None: _auth(object_security_check(f, app_name=a, model_name=m, field=fi))
_owner = lambda f, a=None, m=None, fi=None: _auth(owner_security_check(f, app_name=a, model_name=m, field=fi))



urlpatterns = [
#Main Page
url(r'index/$', _auth(index.as_view()), name ='index'),

#Single Assessment
url(r'index/analysis/$', _auth(assessment_index_view.as_view()), name='assessment_index_view'),
url(r'assessment/welcome_screen$', _auth(assessment_welcome_screen.as_view()), name ='assessment_welcome_screen'),
url(r'^assessment/(?P<uuid>[0-9a-t\-]{32,})/$', _auth(assessment_detail_view.as_view()), name='assessment_detail_view'),
url(r'^assessment/continue/$', _auth(continue_assessment_detail_view), name ='continue_assessment_detail_view'),
url(r'^assessment/createandedit/$', _auth(single_assessment_create), name='single_assessment_create'),

#modal select object

url(r'^assessment/(?P<uuid_boltcase_instance>[0-9a-t\-]{32,})/select_friction_head_modal/$', _auth(select_friction_head_modal), name='select_friction_head_modal'),
url(r'^assessment/(?P<uuid_boltcase_instance>[0-9a-t\-]{32,})/select_friction_joint_modal/$', _auth(select_friction_joint_modal), name='select_friction_joint_modal'),
url(r'^assessment/(?P<uuid_boltcase_instance>[0-9a-t\-]{32,})/select_friction_thread_modal/$', _auth(select_friction_thread_modal), name='select_friction_thread_modal'),

#updates
url(r'^spatial_position_update/update/$', _auth(spatial_position_update), name='spatial_position_update'),



#Manager
url(r'manager/welcome_screen$', _auth(manager_welcome_screen.as_view()), name ='manager_welcome_screen'),

# /car/
#url(r'^$', _auth(views.CarIndexView.as_view()), name='carview'),
#url(r'vehicles/$', _auth(index_vehicle.as_view()), name ='index'),


# /register/    
#url(r'register/$', _auth(views.UserFormView.as_view()), name='register'),

# /cardetail/
url(r'^(?P<pk>[0-9]+)/$', _auth(CarDetailView.as_view()), name ='cardetailview'),


#db
url(r'db_partmateriallist/$', _auth(database.PartMaterialListView.as_view()), name='partmaterial_list'),
url(r'db_boltmateriallist/$', _auth(database.BoltMaterialListView.as_view()), name='boltmaterial_list'),
url(r'db_frictionhead/$', _auth(database.FrictionHeadListView.as_view()), name='frictionhead_list'),
url(r'db_frictionthread/$', _auth(database.FrictionThreadListView.as_view()), name='frictionthread_list'),

#^/BoltMan/car/add/
#url(r'partmaterial/add/$', _auth(views.PartMaterialAdd.as_view()), name='partmaterial-add'),

#^/BoltMan/boltcaseinstance/add/
url(r'boltcaseinstance/add/$', _auth(BoltCaseInstanceCreate.as_view()), name='boltcaseinstance-add'),


#boltmaterial
url(r'^boltmaterial/create/$', _auth(boltmaterial_create), name='boltmaterial_create'),
url(r'^boltmaterial/(?P<pk>[0-9]+)/update/$', _auth(boltmaterial_update), name='boltmaterial_update'),
url(r'^boltmaterial/(?P<pk>[0-9]+)/delete/$', _auth(boltmaterial_delete), name='boltmaterial_delete'),

#friction on bolt thread
url(r'^frictionthread/create/$', _auth(frictionthread_create), name='frictionthread_create'),
url(r'^frictionthread/(?P<pk>[0-9]+)/update/$', _auth(frictionthread_update), name='frictionthread_update'),
url(r'^frictionthread/(?P<pk>[0-9]+)/delete/$', _auth(frictionthread_delete), name='frictionthread_delete'),

# #friction on bolt head
url(r'^frictionhead/create/$', _auth(frictionhead_create), name='frictionhead_create'),
url(r'^frictionhead/(?P<pk>[0-9]+)/update/$', _auth(frictionhead_update), name='frictionhead_update'),
url(r'^frictionhead/(?P<pk>[0-9]+)/delete/$', _auth(frictionhead_delete), name='frictionhead_delete'),

# #friction on joint
url(r'^frictionjoint/create/$', _auth(frictionjoint_create), name='frictionjoint_create'),
url(r'^frictionjoint/(?P<pk>[0-9]+)/update/$', _auth(frictionjoint_update), name='frictionjoint_update'),
url(r'^frictionjoint/(?P<pk>[0-9]+)/delete/$', _auth(frictionjoint_delete), name='frictionjoint_delete'),


#boltgeometry
url(r'^boltgeometry/create/$', _auth(boltgeometry_create), name='boltgeometry_create'),
url(r'^boltgeometry/(?P<pk>[0-9]+)/update/$', _auth(boltgeometry_update), name='boltgeometry_update'),
url(r'^boltgeometry/(?P<pk>[0-9]+)/delete/$', _auth(boltgeometry_delete), name='boltgeometry_delete'),

#bolt case
url(r'^boltcase/create/$', _auth(boltcase_create), name='boltcase_create'),
url(r'^boltcase/(?P<pk>[0-9]+)/update/$', _auth(boltcase_update), name='boltcase_update'),
url(r'^boltcase/(?P<pk>[0-9]+)/delete/$', _auth(boltcase_delete), name='boltcase_delete'),
url(r'^boltcase/(?P<pk>[0-9]+)/detail/$', _auth(BoltCaseDetailView.as_view()), name ='boltcase-detailview'),
url(r'^boltcase/(?P<pk>[0-9]+)/detail/result/$', _auth(BoltCaseResultView.as_view()), name ='boltcase_resultview'),
url(r'^boltcase/(?P<pk>[0-9]+)/detail/select/part/$', _auth(boltcase_part), name ='boltcase_update_part'),
url(r'^boltcase/(?P<pk>[0-9]+)/detail/select/washer/$', _auth(boltcase_washer), name ='boltcase_select_washer'),
url(r'^boltcase/(?P<pk>[0-9]+)/detail/select/boltgeometry/$', _auth(boltcase_boltgeometry), name ='boltcase_select_boltgeometry'),
url(r'^boltcase/(?P<pk>[0-9]+)/detail/select/frictionthread/$', _auth(boltcase_frictionthread), name ='boltcase_select_frictionthread'),
url(r'^boltcase/(?P<pk>[0-9]+)/detail/select/frictionhead/$', _auth(boltcase_frictionhead), name ='boltcase_select_frictionhead'),
url(r'^boltcase/(?P<pk>[0-9]+)/detail/select/frictionjoint/$', _auth(boltcase_frictionjoint), name ='boltcase_select_frictionjoint'),
url(r'^boltcase/(?P<pk>[0-9]+)/detail/select/boltcaseinstance/$', _auth(boltcase_instance), name ='boltcase_select_boltcaseinstance'),

#bolt case instance
url(r'^boltcaseinstance/(?P<pk>[0-9]+)/detail/$', _auth(BoltCaseInstanceDetailView.as_view()), name ='boltcaseinstance-detailview'),
url(r'^boltcaseinstance/create/$', _auth(boltcaseinstance_create), name='boltcaseinstance_create'),


url(r'^boltcaseinstance/(?P<pk>[0-9]+)/update/$', _auth(boltcaseinstance_update), name='boltcaseinstance_update'),
url(r'^boltcaseinstance/(?P<pk>[0-9]+)/delete/$', _auth(boltcaseinstance_delete), name='boltcaseinstance_delete'),


url(r'ajax/load-parts/$', _auth(load_parts), name='ajax_load_parts'),
url(r'ajax/load-boltcaseinstances/$', _auth(load_boltcaseinstances), name='ajax_load_boltcaseinstances'),   
]


##if settings.DEBUG:
##     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_URL)
##     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_URL)

if settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]




