    

from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.fields.files import ImageFieldFile, FieldFile
from django.db.models.fields.related import ForeignKey
import ctypes
from NormMan.scripts.validate_uuid import is_valid_uuid

def component_group_to_tree_json(i_uuid) ->  ctypes.Array:
    if not is_valid_uuid(i_uuid):
        return []
    from NormMan.models import Component_Group_Level
    root_object = Component_Group_Level.objects.filter(UUID = i_uuid).get()
    o_array = []
    def walk(o):
        ''' this function will search recursive a database structure and prepare input json for import
        '''   
        o_dict = {}
        o_dict['id'] = o.UUID
        if  o.parent_group is not None:
            o_dict['parent'] = o.parent_group.UUID
        else:
            o_dict['parent'] = "#"
        o_dict['text'] = o.name 
        o_dict.update(o.as_dict())
        o_dict.pop("normparts_database_parts")
        o_dict.pop("normparts_database_components")
        o_dict.pop("normparts_database_sections")
        o_dict.pop("normparts_database_workflows")
        o_dict.pop("normparts_database_tools")
        o_dict.pop("parent_group")
        o_array.append(o_dict)

        query = Component_Group_Level.objects.filter(parent_group__UUID = o.UUID)
        
        for object in query:
            print(object.name)
            walk(object)

    if root_object: 
        walk(root_object)
        return o_array
    else:
        return []    
    