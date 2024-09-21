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
        exists = lambda x: os.path.exists(os.path.join(x, "meta.json").replace("\\", "/"))
        components = NormParts_Shared_Component.objects.all()
        for component in components:
            full_path = os.path.join(MEDIA_ROOT, component.data_path)
            print(f'Checking component {component} with data path: {full_path}')
            if not exists(full_path):
                print(" - Meta does not exist!")
                if not os.path.exists(full_path):
                    print(" - Object is not created, skipping!")
                    continue
                print(" - Creating meta")
                new_dict, db_structure, where_to_add = dict(), dict(), None
                new_dict.update({"NormParts_Shared_Component":component.as_dict()})
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
                new_dict.update({"db_structure":db_structure["db_structure"]})                                    
                with open(os.path.join(full_path, "meta.json").replace("\\", "/"), "w") as file:
                    json.dump(new_dict, file,  indent = 6, cls=ExtendedEncoder)
            else:
                print(" - Meta does exist, skipping!")
        return