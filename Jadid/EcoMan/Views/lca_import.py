
from django.shortcuts import get_object_or_404
from EcoMan.models import Analysis_Comparison, Lca_Property
from django.shortcuts import redirect
from django.conf import settings
from django.views import generic
import pathlib
import os, json
from datetime import date
from django.http import HttpResponse
from django.contrib.staticfiles.storage import staticfiles_storage
from django.db.models import Q




def lca_properties_from_json(request):
    '''this function returns a dictionary of dictionaries requsted as tuple of names of constants'''
    result={}
    data={}
    path_to_json_template = staticfiles_storage.path('EcoMan/lca_properties.json')
    f = open(path_to_json_template)
    data = json.load(f)

    for i, j in data['lca_property'].items():
        #check if property exists in a database
        if isinstance(j, dict):
            query =Lca_Property.objects.filter(Q( name = j['name']) & Q(unit = j['unit'])) 
            if not query:
                new_lca_property = Lca_Property(**j)
                new_lca_property.save()

    f.close()
    return redirect(request.META.get('HTTP_REFERER'))