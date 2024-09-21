from NormMan.models import Component_Group_Level
from django.core.management.base import BaseCommand
from NormMan.scripts import *
import json, os
from website import settings
class Command(BaseCommand):

    def handle(self, *args, **options):
        '''this procedure will generate metadata according to three js for filters for all objects of Component_Group_Level
        '''

        root_object = Component_Group_Level.objects.filter(group_depth_level = 0).first()
        o_array = []
        full_array = []
        full_array = component_group_to_tree_json(root_object.UUID)
        full_dict = {}


        def walk(o):
            children_array =[]
            for object_2 in full_array:
                if object_2['parent'] == o['id']:
                    full_dict[object['id']].append(object_2)
                    children_array.append(object_2)
            
            for children in children_array:
                walk(children)

        for object in full_array:
            full_dict[object['id']] = []
            full_dict[object['id']].append(object)
            walk(object)

        for object in full_dict.items():
            out_file = open(os.path.join( settings.MEDIA_ROOT, object[1][0]['data_path'].name, "meta_threejs.json" ), "w")
            json.dump(object[1], out_file, indent = 4, cls=ExtendedEncoder)
            out_file.close()     
        pass   




