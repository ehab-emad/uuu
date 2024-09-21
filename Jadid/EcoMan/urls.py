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
from django.urls import *
from django.urls import re_path as url
from django_keycloak.decorators import group_required_account_not_expired, check_keycloak_status, group_required
from website.security.url_decorators_for_database_content import *
from .Views import *
app_name = "EcoMan"
group_name ="/be_paramount/app-ecoman"
_auth = lambda f,required_groups = None, required_roles = None: group_required(check_keycloak_status(f), app_group=group_name,  group_names = required_groups, role_names = required_roles)
_project = lambda f, a=None, m=None, fi=None: _auth(project_security_check(f, app_name=a, model_name=m, field=fi))
_object = lambda f, a=None, m=None, fi=None: _auth(object_security_check(f, app_name=a, model_name=m, field=fi))
_owner = lambda f, a=None, m=None, fi=None: _auth(owner_security_check(f, app_name=a, model_name=m, field=fi))

urlpatterns = [


    url(r'index/$', _auth(index.as_view()), name ='index'),

    url(r'analysis_playground/welcome_screen/$', _auth(qlca_welcome_screen.as_view()), name ='qlca_welcome_screen'),
    url(r'analysis/welcome_screen$', _auth(qlca_analysis_welcome_screen.as_view()), name ='qlca_analysis_welcome_screen'),
    #lca part
    #url(r'^lcapart/create/$', _auth(lca_part_create_modal), name='lca_part_create_modal'),
    url(r'^lcapart/create/pk_analysis:(?P<pk_analysis>[0-9]*)/is_automotive:(?P<is_automotive>True|False)/weight_unit:(?P<weight_unit>[a-zA-Z]+)$', _auth(lca_part_create_modal), name='lca_part_create_modal'),
    url(r'^lcapart/(?P<pk>[0-9]+)/update/is_automotive:(?P<is_automotive>True|False)/weight_unit:(?P<weight_unit>[a-zA-Z]+)$', _auth(lca_part_update), name='lca_part_update'),
    url(r'^lcapart/(?P<pk>[0-9]+)/delete/$', _auth(lca_part_delete, required_roles = ['edag_worker'],), name='lca_part_delete'),

    #lca parts operations playground
    url(r'^lca_part_switch_analysis/source_analysis/(?P<pk_source_analysis>[0-9]+)/target_analysis/(?P<pk_target_analysis>[0-9]+)/lca_part/(?P<pk_lca_part>[0-9]+)$', _auth(lca_part_move), name='lca_part_move'),
    url(r'^lca_part_add_mirror/source_analysis/(?P<pk_source_analysis>[0-9]+)/target_analysis/(?P<pk_target_analysis>[0-9]+)/lca_part/(?P<pk_lca_part>[0-9]+)$', _auth(lca_part_add_mirror), name='lca_part_add_mirror'),
    url(r'^lca_part_remove_mirror/target_analysis/(?P<pk_target_analysis>[0-9]+)/lca_part/(?P<pk_lca_part>[0-9]+)$', _auth(lca_part_remove_mirror), name='lca_part_remove_mirror'),
    url(r'^(?P<pk_analysis>[0-9]+)/clone_lca_part/(?P<pk_lca_part>[0-9]+)$', _auth(quick_part_clone), name='quick_part_clone'),


    #analysis_comparison_playgroud
    url(r'^analysis_comparison/(?P<pk>[0-9]+)/playgrounddetail/$', _auth(analysis_comparison_detail_view.as_view()), name ='analysis_comparison_detail_view'),
    url(r'^current/playgrounddetail/$', _auth(continue_analysis_comparison_detail_view), name ='continue_analysis_comparison_detail_view'),
    url(r'index/qlcaplayground/$', _auth(analysis_comparison_index_view.as_view()), name ='analysis_comparison_index_view'),
    #analysis_comparison #modal windows
    url(r'^analysis_playground/createandedit/$', _auth(analysis_comparison_create_and_edit), name='analysis_comparison_create_and_edit'),
    url(r'^analysis_playground/create/$', _auth(analysis_comparison_create), name='analysis_comparison_create'),
    url(r'^analysis_playground/(?P<pk>[0-9]+)/update/$', _auth(analysis_comparison_update), name='analysis_comparison_update'),
    url(r'^analysis_playground/(?P<pk>[0-9]+)/update_report_settings/$', _auth(analysis_comparison_report_update), name='analysis_comparison_report_update'),
    url(r'^(?P<pk>[0-9]+)/delete/$', _auth(analysis_comparison_delete, required_roles = ['edag_worker'],), name='analysis_comparison_delete'),

    # analysis
    url(r'index/analysis/$', _auth(analysis_index_view.as_view()), name='analysis_index_view'),
    url(r'^analysis/current/detail/$', _auth(continue_analysis_detail_view), name ='continue_analysis_detail_view'),

    url(r'^analysis/(?P<pk>[0-9]+)/playgroundonecolumn/$', _owner(analysis_detail_view.as_view(), a='EcoMan', m='Analysis'), name='analysis_detail_view'),

    #analysis #modal windows   
    url(r'^analysis/createandedit/$', _auth(analysis_create_and_edit), name='analysis_create_and_edit'),
    url(r'^analysis/(?P<pk>[0-9]+)/update/$', _auth(analysis_update), name='analysis_update'),
    url(r'^analysis/(?P<pk>[0-9]+)/delete/$', _auth(analysis_delete, required_roles = ['edag_worker'],), name='analysis_delete'),
    url(r'^analysis/(?P<pk>[0-9]+)/update_report_settings/$', _auth(analysis_settings_update), name='analysis_settings_update'),

    #analysis_comparison
    url(r'index/qlcacompare/$', _auth(analysis_index_view_compare.as_view()), name ='qlca_compare'),
    url(r'index/qlcacompare/create$', _auth(analysis_comparison_create_compare), name ='analysis_comparison_create_compare'),

    #support ticket
    url(r'^supportticket/create/$', _auth(lca_support_ticket_create_modal, required_roles = ['edag_worker'],), name='lca_support_ticket_create_modal'),

    #print playground report
    url(r'^(?P<pk>[0-9]+)/print/$', _auth(lca_comparison_print_reportlab), name='lca_comparison_print_reportlab'),
    
    #print playground report
    url(r'^analysis/(?P<pk>[0-9]+)/print/$', _auth(lca_analysis_print_reportlab), name='lca_analysis_print_reportlab'),

    #LCA Part lca_part_add_process
    url(r'^lca_part/(?P<pk_lca_part>[0-9]*)/addnewlcaprocess/lca_step/(?P<lca_step>[\w\-]+)/weight_unit:(?P<weight_unit>[a-zA-Z]+)$', _auth(lca_part_add_process_instance), name='lca_part_add_process_instance'),

    url(r'^lca_part/(?P<pk>[0-9]*)/addnew:process_circularity/$', _auth(step1upstream_add_process_circularity), name='step1upstream_add_process_circularity'),
    url(r'^lca_part/(?P<pk>[0-9]*)/addnew:transport_circularity/$', _auth(step1upstream_add_transport_circularity), name='step1upstream_add_transport_circularity'),
    url(r'^lca_part/(?P<pk_lca_part>[0-9]*)/toggle_ispartreused/$', _auth(lcastep_ispartreused_status), name='lcastep_ispartreused_status'),

    #analysis modal
    url(r'^analysis_comparison/(?P<pk>[0-9]*)/addnew:utilisation/$', _auth(analysis_comparison_add_utilisation), name='analysis_comparison_add_utilisation'),
    url(r'^analysis/(?P<pk>[0-9]*)/addnew:utilisation/$', _auth(analysis_add_utilisation), name='analysis_add_utilisation'),
    #instance process
    url(r'^material_instance_lca_process/(?P<pk_instance>[0-9]*)/update/weight_unit:(?P<weight_unit>[a-zA-Z]+)/weight_decimals:(?P<weight_decimals>[0-9]*)$', _auth(material_process_instance_update), name='material_process_instance_update'),
    url(r'^processing_instance_lca_process/(?P<pk_instance>[0-9]*)/update/weight_unit:(?P<weight_unit>[a-zA-Z]+)/weight_decimals:(?P<weight_decimals>[0-9]*)/update/$', _auth(processing_process_instance_update), name='processing_process_instance_update'),
    url(r'^transport_instance_lca_process/(?P<pk_instance>[0-9]*)/update/weight_unit:(?P<weight_unit>[a-zA-Z]+)/weight_decimals:(?P<weight_decimals>[0-9]*)$', _auth(transport_process_instance_update), name='transport_process_instance_update'),
    url(r'^instance_lca_process/(?P<pk>[0-9]+)/delete/$', _auth(instance_idemat_process_delete), name='instance_idemat_process_delete'),
    url(r'^lca_part/(?P<pk_process_instance>[0-9]*)/process_instance_is_active/$', _auth(process_instance_is_active), name='process_instance_is_active'),

    #instance_utilisation_process   (word instance should be removed - it is not the same as with idemate process and instance idemat process)

    url(r'^utilisation_process/create/analysis:(?P<pk_analysis>[0-9]*)$', _auth(utilisation_instance_process_create), name='utilisation_instance_process_create'),
    url(r'^utilisation_process/create/$', _auth(utilisation_instance_process_create), name='utilisation_instance_process_create'),
    url(r'^utilisation_process/(?P<pk>[0-9]+)/delete/$', _auth(utilisation_instance_process_delete), name='utilisation_instance_process_delete'),
    url(r'^utilistaion_process/(?P<pk_instance>[0-9]*)/update/$', _auth(utilisation_instance_process_update), name='utilisation_instance_process_update'),

    #instance_circularity_process
    url(r'^circularity_process/(?P<pk_circularity_process>[0-9]*)/update/$', _auth(circularity_process_update), name='circularity_process_update'),

    #LCA Database
    url(r'^lca_db/(?P<pk>[0-9]+)/processlist/$', _auth(LcaProcessListView.as_view()), name='lca_process_list'),
    
    url(r'^lca_db/open/list/$', _auth(open_database_index_view.as_view()), name='open_database_index_view'),
    url(r'^lca_db/organisation/list/$', _auth(edag_database_index_view.as_view()), name='edag_database_index_view'),
    url(r'^lca_db/project/list/$', _auth(project_database_index_view.as_view()), name='project_database_index_view'),
    
    url(r'^lca_db/create/$', _auth(lca_db_create), name='lca_db_create'),
    url(r'^lca_db/(?P<pk>[0-9]+)/update/$', _auth(lca_db_update), name='lca_db_update'),
    url(r'^lca_db/(?P<pk>[0-9]+)/importexcel/$', _auth(lca_db_import_excel, required_roles = ['edag_worker']), name='lca_db_import_excel'),
    url(r'^lca_db/(?P<pk>[0-9]+)/exportexcel/$', _auth(lca_db_export_excel, required_roles = ['edag_worker']), name='lca_db_export_excel'),

    url(r'^lca_db/(?P<pk>[0-9]+)/delete/$', _auth(lca_db_delete, required_roles = ['edag_worker'], required_groups=[group_name + 'user-professional']), name='lca_db_delete'),
    url(r'^lca_db/(?P<pk>[0-9]+)/restore/$', _auth(lca_db_restore, required_roles = ['edag_worker'], required_groups=[group_name + 'user-professional']), name='lca_db_restore'),
    url(r'^lca_db/create/excel_import$', _auth(lca_db_create, required_roles = ['edag_worker']), name='lca_db_create'),
    url(r'^lca_db/download_lca_template/$', _auth(lca_database_template_download), name='lca_database_template_download'),

    #lca_process
    url(r'^lca_db/(?P<lca_database_pk>[0-9]+)/lca_process/create/$', _auth(lca_process_create), name='lca_process_create'),
    url(r'^lca_process/create/$', _auth(lca_process_create), name='lca_process_create'),

    url(r'^lca_process/(?P<pk>[0-9]+)/update/$', _auth(lca_process_update, required_groups=[group_name + 'user-professional']), name='lca_process_update'),
    url(r'^lca_process/(?P<pk>[0-9]+)/review/$', _auth(lca_process_review), name='lca_process_review'),
    url(r'^lca_process/(?P<pk>[0-9]+)/delete/$', _auth(lca_process_delete, required_groups=[group_name + 'user-professional']), name='lca_process_delete'),
    url(r'^lca_process/(?P<pk>[0-9]+)/restore/$', _auth(lca_process_restore), name='lca_process_restore'),
    #this view will refresh the list of available materials after selected filter
    url(r'load-idemat-processes/$', _auth(load_lca_database_processes), name='load_lca_database_processes'),

    #energysource
    url(r'^energysource/(?P<pk_energysource>[0-9]+)/update/$', _auth(energysource_update), name='energysource_update'),

    #playgraound import/export
    url(r'^analysis_comparison/(?P<pk_analysis_comparison>[0-9]*)/export_to_json/$', _auth(analysis_comparison_to_json, required_roles = ['edag_worker'],), name='analysis_comparison_to_json'),
    url(r'^analysis/(?P<pk_analysis>[0-9]*)/export_to_json/$', _auth(analysis_to_json, required_roles = ['edag_worker'],), name='analysis_to_json'),
    url(r'^analysis_comparison/(?P<pk_analysis_comparison>[0-9]*)/show_diagram/$', _auth(analysis_comparison_to_diagram, required_roles = ['edag_worker'],), name='analysis_comparison_show_diagram'),

    url(r'^lca_properties/export_to_json/$', _auth(lca_properties_to_json, required_roles = ['edag_worker'],), name='lca_properties_to_json'),
    url(r'^lca_properties/import_from_json/$', _auth(lca_properties_from_json, required_roles = ['edag_worker'],), name='lca_properties_from_json'),

    url(r'^analysis_comparison/(?P<pk_analysis_comparison>[0-9]*)/update/json_import/$', _auth(json_import_analysis_comparison_append, required_roles = ['edag_worker'],), name='json_import_analysis_comparison_append'),
    url(r'^analysis_comparison/create/json_import/$', _auth(json_import_analysis_comparison_create_new, required_roles = ['edag_worker'],), name='json_import_analysis_comparison_create_new'),

    url(r'^analysis/(?P<pk_analysis>[0-9]*)/update/json_import/$', _auth(json_import_analysis_append, required_roles = ['edag_worker'],), name='json_import_analysis_append'),

    url(r'^analysis/create/json_import/$', _auth(json_import_analysis_comparison_create_new, required_roles = ['edag_worker'],), name='json_import_analysis_comparison_create_new'),
    url(r'^analysis_comparison/create/json_import/preview$', _auth(load_json_preview, required_roles = ['edag_worker'],), name='load_json_preview'),

    #Catia import entry view
    url(r'^analysis_comparison/create/json_import/catia_import/(?P<uuid_session>[0-9a-f\-]{32,})/$', _auth(catia_import, required_roles = ['edag_worker'],), name='catia_import'),

    #this view will refresh the list of available categories after selected filter
    url(r'load-idemat-categories/$', _auth(load_idemat_categories), name='load_idemat_categories'),


    url(r'^lca_analysis/(?P<pk_analysis>[0-9]*)/addnewpartfromtemplate/$', _auth(lca_part_add_from_template), name='lca_part_add_from_template'),
    url(r'load-templates/$', _auth(load_templates), name='load_templates'),
    url(r'^download_documentation/$', _auth(qlca_documentation_download), name='qlca_documentation_download'),



]
