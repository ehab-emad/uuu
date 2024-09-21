from NormMan.models import Component_Group_Level
import json
from tkinter import filedialog as fd
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.fields.files import ImageFieldFile
from django.core.management.base import BaseCommand
from django.db.models import Q
import os
import uuid
import website.settings as settings
class ExtendedEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, ImageFieldFile):
            return str(o)
        else:
            return super().default(o)


class Command(BaseCommand):
    def handle(self, *args, **options):
        root_component = Component_Group_Level.objects.filter(group_depth_level = 0).get() 
        #Component_Group_Level.objects.create( name = 'ROOT', parent_group = None, group_depth_level = 0)
        #Component_Group_Level.objects.filter(name='Body').delete()
        #query = Component_Group_Level.objects.filter(group_depth_level = 1)
 
        #setting variables
        start_level = 1
        start_name = "Body"
        o_dict = {}
        global l_index
        component_parent = Component_Group_Level.__new__
        l_index = 1
        #open and read json file
        ins = fd.askopenfile()
        file_to_read = open(ins.name, "r")
        d= json.load (file_to_read)


        def walk(e, o, level=1,  name= "Nothing", parent = None):
            ''' this function will search recursive a dictionary and prepare input json for import
            '''   
            component_name = name.strip()  
            component = Component_Group_Level.objects.create( name = component_name, parent_group = parent, group_depth_level = level)

            o[component.name] = {}
            o[component.name].update({'Component_Group_Level': component})
            o[component.name].update({'Children': {}})  
            
            component_parent = component
            for key in e:
                if key!="id" and key!="text":
                    walk(e[key], o[component.name]['Children'], level + 1, key, parent = component_parent, )

        walk(d[start_name], o_dict ,  level=1, name = start_name,  parent = root_component)

        # #dump result to a file
        # with open(ins.name + "id", "w") as outfile:
        #     default = lambda o: f"<<non-serializable: {type(o).__qualname__}>>"
        #     return json.dumps(o_dict, outfile, indent=4, default=default)           

        return