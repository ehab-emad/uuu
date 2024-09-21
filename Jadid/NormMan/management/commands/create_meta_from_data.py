import os, json
from django.core.management.base import BaseCommand
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.fields.files import ImageFieldFile, FieldFile
from django.db.models.fields.related import ForeignKey
from NormMan.models import NormParts_Shared_Component, Component_Group_Level
from NormMan.scripts.validate_uuid import is_valid_uuid
from website.settings import MEDIA_ROOT


class ExtendedEncoder(DjangoJSONEncoder):
    def default(self, check_field):
        if isinstance(check_field, ImageFieldFile) or isinstance(check_field, FieldFile):
            return str(check_field)
        elif isinstance(check_field, ForeignKey):
            return str(check_field)
        else:
            return super().default(check_field)
        

class Command(BaseCommand):

    def handle(self, *args, **options) -> None:
        # go through all the NormPart_components     
        # -> Make it recursive and with input argument   
        path_db_structure = os.path.join(MEDIA_ROOT, "norm_parts\\db_structure\\ROOT_UUID_fd9cea85-83d8-4a79-a1f1-22d1dd578516\\Norm_parts_UUID_96540593-2cc7-460b-b453-6438078313a4\\Clips_UUID_c332539b-bb8d-4222-883c-c620bfad6930\\Shared_Components")
        exists = lambda x: os.path.exists(os.path.join(x, "meta.json").replace("\\", "/"))
        for root, dirs, _ in os.walk(path_db_structure.replace("\\", "/")): 
            for comp_dir in dirs:
                full_path = os.path.join(root, comp_dir).replace("\\", "/")
                if len(comp_dir) < 40:
                    continue
                obj_uuid = comp_dir[-36:]
                obj_type = comp_dir[:-37].split("_")[1]
                if not is_valid_uuid(obj_uuid):
                    print(" - Invalid object, skipping")
                    continue
                print(f'Checking {obj_type} object with UUID {obj_uuid}')
                if exists(full_path):
                    print(' - Meta object exists, skipping')
                    continue
                new_dict, db_structure, where_to_add = dict(), dict(), None
                data = {
                            "UUID": obj_uuid,
                            "data_path": full_path,
                            "name": None,
                            "name_de": None,
                            "owner": None,
                            "project_model": "207e04c4-d01a-48e3-9cc7-6dd09c42b326",
                            "thumbnail": os.path.join(full_path, "thumbnail.png").replace("\\", "/"),
                            "stl_thumbnail": os.path.join(full_path, "stl_thumbnail.png").replace("\\", "/"),
                            "file_catia_part": os.path.join(full_path, "catia_part.png").replace("\\", "/"),
                            "file_configuration": None,
                            "file_workflow_json": None,
                            "counter": 0,
                            "supplier_name": None,
                            "supplier_part_number": None,
                            "oem_reference_name": None,
                            "oem_reference_part_number": None,
                            "accessibility": "DATABSE_USERS",
                            "type": obj_type.upper(),
                            "parameters": None,
                            "material": None,
                            "source": None,
                            "weight": None,
                            "density": None
                    }
                folders = [(obj[:-37], obj[-36:]) for obj in full_path.replace("\\", "/").split("/")[-2::-1] if is_valid_uuid(obj[-36:])]                
                for _, uuid in folders:
                    category_group = Component_Group_Level.objects.filter(UUID = uuid)
                    if category_group:
                        category_group = category_group.get()
                        level_info = dict()
                        level_info.update({"category_group_uuid":uuid})
                        level_info.update({"category_group_name":category_group.name})
                        level_info.update({"parent":dict()})
                        print(category_group.name)
                        if where_to_add is None:
                            db_structure.update({"db_structure":level_info})                            
                        else:
                            where_to_add.update({"parent":level_info})
                        where_to_add = level_info
                    pass
                new_dict.update({"NormParts_Shared_Component":data})    
                new_dict.update({"db_structure":db_structure["db_structure"]})
                with open(os.path.join(full_path, "meta.json").replace("\\", "/"), "w") as file:
                    json.dump(new_dict, file,  indent = 6, cls=ExtendedEncoder)

        pass