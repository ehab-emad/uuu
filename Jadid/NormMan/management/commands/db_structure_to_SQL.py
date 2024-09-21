from NormMan.models import Component_Group_Level
import os, json, sys
from django  import apps
from django.core.serializers.json import DjangoJSONEncoder
from django.core.management.base import BaseCommand
from django.db.models.fields.files import ImageFieldFile, FieldFile
from django.db.models.fields.related import ForeignKey
from NormMan.models import Component_Group_Level, Project_NormMan_Ref, ProjectUser_NormMan_Ref
from NormMan.scripts.validate_uuid import is_valid_uuid
import website.settings as settings
from django.shortcuts import  get_object_or_404
from NormMan.models import NormParts_Shared_Component

class ExtendedEncoder(DjangoJSONEncoder):
    def default(self, check_field):
        if isinstance(check_field, ImageFieldFile) or isinstance(check_field, FieldFile):
            return str(check_field)
        elif isinstance(check_field, ForeignKey):
            return str(check_field)
        else:
            return super().default(check_field)

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('input_path', type=str, nargs='?', help='Input path to start at.', default=None)

    def handle(self, *args, **options):
        input_path = options['input_path']
        '''
        Run through static database and create a corresponding replica in SQL database.
        Operation just modifies current database and does not produce any value.
        :return: None
        '''  
        input_path = input_path if input_path is not None else "norm_parts\\db_structure\\ROOT_UUID_fd9cea85-83d8-4a79-a1f1-22d1dd578516"   
        path_db_structure = os.path.join(input_path)
        system_path = os.path.join(settings.MEDIA_ROOT)
        projectuser = ProjectUser_NormMan_Ref.objects.filter(nickname = 'admin').get()

        #check if root object exists when not create one
        root_component_group = Component_Group_Level.objects.filter(UUID = 'fd9cea85-83d8-4a79-a1f1-22d1dd578516')
        if root_component_group:
            root_component_group = root_component_group.first()
        else:
            root_component_group = Component_Group_Level.objects.create(UUID = 'fd9cea85-83d8-4a79-a1f1-22d1dd578516', 
                                                                        name = 'ROOT', 
                                                                        data_path = input_path,
                                                                        parent_group = None,
                                                                        group_depth_level = 0)
            root_component_group.save()

        counter = 0 
        for root, dirs, _ in os.walk(os.path.join(system_path, path_db_structure).replace("\\", "/")):
            folder_to_check = os.path.join(root , "Shared_Components").replace("\\", "/")
            if not os.path.exists(folder_to_check):
                if os.path.basename(root) != "Shared_Components":
                    os.mkdir(folder_to_check)  
      
            for dirname in dirs:
                if dirname != "Shared_Components" and root.replace("\\", "/").split("/")[-1] != "Shared_Components":
                    #here the Component_Group_Level will be verified
                        counter+=1
                        print('[' + str(counter) + ']:Checking Component_Group_Level:' + dirname)
                        is_object_uuid_valid = is_valid_uuid(dirname[-36:], 4)                   
                        if is_object_uuid_valid:
                                object_uuid = dirname[-36:]
                                object_name = dirname[:-42]
                                print("- UUID is valid:" + object_uuid ) 
                        else:                               
                            print("- Invalid object skipping")       
                            continue 

                        sought_uuid = root.replace("\\", "/").split("/")[-1][-36:]
                        parent_component_group =Component_Group_Level.objects.filter(UUID = sought_uuid)
                        if parent_component_group:
                            parent_component_group=parent_component_group.first()
                        else:
                            parent_component_group = None
                         
                        new_object = Component_Group_Level.objects.filter(UUID = object_uuid)
                        group_depth_level = parent_component_group.group_depth_level + 1
                        if new_object:
                            new_object = new_object.get()
                            print("- Object exists in database: Updating") 
                            if parent_component_group:
                                new_object.parent_group = parent_component_group
                                new_object.data_path.name = new_object.data_path.name.replace("\\", "/")
                                new_object.save()
                        else:
                            print("- Object does not exists in database: Creating")
                            new_object = Component_Group_Level.objects.create(UUID = object_uuid, 
                                                                              name = object_name, 
                                                                              data_path = os.path.relpath(os.path.join(root , dirname).replace("\\", "/"), system_path),
                                                                              parent_group = parent_component_group,
                                                                              group_depth_level = group_depth_level )
                            new_object.save()
                            print("- import success")

                if dirname == "Shared_Components":
                    for root_2, dirs_2, _ in os.walk(os.path.join(root , dirname).replace("\\", "/")):
                        for dirname_2 in dirs_2:                       
                            if dirname_2 != "Shared_Components":
                                print('Checking Shared_Component:' + dirname_2)
                                is_object_uuid_valid = is_valid_uuid(dirname_2[-36:], 4)
                                if is_object_uuid_valid:
                                        object_uuid = dirname_2[-36:]
                                        print("- UUID is valid:" + object_uuid ) 
                                else:                               
                                    print("- Invalid object skipping")       
                                    continue     

                                # Path operators
                                base_path = os.path.join(system_path, root_2 , dirname_2).replace("\\", "/")
                                rel_path = lambda x: os.path.relpath(os.path.join(root_2 , dirname_2, x).replace("\\", "/"), system_path).replace("\\", "/")
                                exists = lambda x: os.path.exists(os.path.join(base_path, x).replace("\\", "/"))

                                #open meta.json
                                if not exists("meta.json"):
                                    continue
                                with open(os.path.join(root_2 , dirname_2, "meta.json").replace("\\", "/"))  as meta_file:
                                    meta_dict = json.load(meta_file)    

                                # Here we do not need to find specific object, as it is one and only object now                                
                                # We do not need shared object name anymore, as there is only one name - NormParts_Shared_Component
                                shared_object_name = "NormParts_Shared_Component"
                                shared_model = apps.apps.get_model('NormMan', shared_object_name)

                                # in comparison to previous version, we do not need to search through meta.json, because it will still stop 
                                # after a component is found. But, there might be more component, which are to be seen as well. So here we can
                                # run through all of them and modify it as well.
                                # But it is to be expected, there is always just only one object
                                new_dict = dict() # -> modification of elemets to update database
                                new_object = dict()
                                for object in meta_dict:
                                    if object == shared_object_name:
                                        new_object = meta_dict[object]
                                        new_object.update({'type': meta_dict[object]['type']}) if 'type' in new_object else new_object.update({'type': object})
                                        if 'file_configuration_xlsx' in new_object:
                                            del new_object['file_configuration_xlsx'] 
                                        new_dict.update({shared_object_name: new_object})
                                        pass
                                new_dict.update({'db_structure': meta_dict['db_structure']}) # -> don't know whether this is needed and makes sense    
                                meta_dict = new_dict                                                           
                                
                                # We update information here to (temporary) new file
                                if True: # -> defaults to false after one run                         
                                    with open(os.path.join(root_2 , dirname_2, "meta.json").replace("\\", "/"), "w") as meta_file:
                                        meta_file.write(json.dumps(new_dict, indent=4))
                                        pass
                                match meta_dict[shared_object_name]['type']:
                                    case "Component":
                                        meta_dict[shared_object_name].update({'type': "COMPONENT"})
                                    case "Part":
                                        meta_dict[shared_object_name].update({'type': "PART"})
                                    case "Section":
                                        meta_dict[shared_object_name].update({'type': "SECTION"})
                                    case "Template":
                                        meta_dict[shared_object_name].update({'type': "TEMPLATE"})
                                    case "Workflow":
                                        meta_dict[shared_object_name].update({'type': "WORKFLOW"})
                                    case _:
                                        pass                            
                                    
                                new_object = shared_model.objects.filter(UUID = object_uuid)
                                if new_object:
                                    new_object = new_object.get()
                                    print("- Object exists in database: Updating") 


                                else:
                                    print("- Object does not exists in database: Creating")                                                                        
                                    if 'project_model' in meta_dict[shared_object_name]:
                                        try:                                           
                                            meta_dict[shared_object_name].update({'project_model': Project_NormMan_Ref.objects.filter(UUID=meta_dict[shared_object_name]['project_model']).get() })
                                            valid = True                                            
                                        except:
                                            del meta_dict[shared_object_name]['project_model']
                                            valid = False
                                        meta_dict[shared_object_name].update({'data_path': rel_path('')})

                                        Project_NormMan_Ref_Object = Project_NormMan_Ref.objects.filter(UUID =  str(projectuser.reference_projectuser.current_project.UUID)).get()
                                        try:
                                            if 'UUID' not in meta_dict[shared_object_name]:
                                                new_object = shared_model.objects.create(UUID = object_uuid, **meta_dict[shared_object_name]) if valid else shared_model.objects.create(UUID = object_uuid, project_model=Project_NormMan_Ref_Object , **meta_dict[shared_object_name])
                                            else:
                                                new_object = shared_model.objects.create(**meta_dict[shared_object_name]) if valid else shared_model.objects.create(project_model=Project_NormMan_Ref_Object , **meta_dict[shared_object_name])
                                        except:
                                            pass
                                    else:                                   
                                        new_object = shared_model.objects.create(UUID = object_uuid, project_model=Project_NormMan_Ref_Object , **meta_dict[shared_object_name], data_path = rel_path(''))
                                    if new_object:
                                        new_object.data_path = new_object.data_path.replace("\\", "/")
                                        new_object.save()
                                        print("- import success")
                                    else:
                                        continue
                                
                                new_object.data_path = rel_path('')
                                new_object.stl_thumbnail = rel_path("stl_thumbnail.stl")
                                new_object.thumbnail =  rel_path("thumbnail.jpg") if exists("thumbnail.jpg") else rel_path("thumbnail.png")
                                new_object.file_workflow_json = rel_path("workflow.json") if exists("workflow.json") else None
                                new_object.file_catia_part = rel_path("catia_part.CATPart") if exists("catia_part.CATPart") else None
                                new_object.file_configuration = rel_path("configuration.xlsx")if exists("configuration.xlsx") else None
                                uuid_parent_group = root_2.split("/")[-2][-36:]              
                                parent_group_object = Component_Group_Level.objects.filter(UUID = uuid_parent_group)
                                if parent_group_object:
                                    parent_group_object= parent_group_object.get()
                                else:
                                    further_group_object = parent_group_object
                                    i=1
                                    while i>0:
                                        new_component_group = Component_Group_Level.objects.create(UUID = uuid_parent_group, name = root_2.split("/")[-2][-36:] )
                                        new_component_group.save() 

                                        if further_group_object.parent_group: 
                                            further_group_object = further_group_object.parent_group
                                            if further_group_object == root_component_group:
                                                break
                                        else:
                                            break

                                #find corresponding models and fields based on Shared Compinents meta.json

                                my_filter = {}
                                my_filter[str(shared_object_name.lower() + 's__UUID')] = object_uuid

                                #search categories including new_object to remove duplicates
                                query_old_categories = Component_Group_Level.objects.filter(**my_filter)
                                for object in query_old_categories:
                                    shared_component_field = getattr(object, shared_object_name.lower() + 's')
                                    shared_component_field.remove(new_object)
                                    object.save()

                                #include shared components in all parent Component_groups
                                further_group_object = parent_group_object
                                i=1
                                while i>0:
                                    shared_component_field = getattr(further_group_object, shared_object_name.lower() + 's')
                                    shared_component_field.add(new_object)
                                    further_group_object.save()
                                    if further_group_object.parent_group:
                                        if further_group_object == root_component_group:
                                            break
                                        further_group_object = further_group_object.parent_group
                                    else:
                                        break

                                #shared_component_field.add(new_object)
                                #parent_group_object.save()
                                new_object.data_path = new_object.data_path.replace("\\", "/")
                                new_object.save()    
        return