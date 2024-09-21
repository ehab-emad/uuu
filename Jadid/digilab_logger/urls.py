from django.conf.urls import url
from . import views
from django.urls import path

app_name = 'logger'

urlpatterns = [
    path('testing/create-info-logs', views.testing_create_info_logs , name="testing_create_info_logs"), 
    path('testing/raise-exception', views.testing_raise_exception , name="testing_raise_exception"), 
]