import json
from django.contrib.staticfiles.storage import staticfiles_storage

def import_lca_constant(*args):
    '''this function returns a dictionary of dictionaries requsted as tuple of names of constants'''
    result={}
    data={}
    path_to_json_template = staticfiles_storage.path('EcoMan/ECO_constants.json')
    f = open(path_to_json_template)
    data = json.load(f)

    for i in data['ENERGY_SOURCE']:
        for j in args:
            if i['TYPE']==str(j).upper():
                result[i['TYPE']]=i

    f.close()
    return result