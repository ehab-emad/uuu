from NormMan.models import Component_Group_Level
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.fields.files import ImageFieldFile
from django.core.management.base import BaseCommand
from NormMan.scripts.validate_uuid import is_valid_uuid
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
        path_db_structure = os.path.join( settings.MEDIA_ROOT, "norm_parts\\db_structure\\")
        object_file_list = [x for x in os.walk(path_db_structure)]

        if len(object_file_list)>0: object_file_list.pop(0)     

        for directoryy in object_file_list:
            #open meta file if exists
            file_path = os.path.join(directoryy[0], "meta.json")
    
            f = open(file_path)
            data = json.load(f)
            #check if uuid already exists in a database
            part_query = Component_Group_Level.objects.filter(id = data["Component_Group_Level"]["id"])
            difference = False
            if part_query:
                print(f'Category with id={data["Component_Group_Level"]["id"]} "{data["Component_Group_Level"]["name"]}" already exists in a database') 
                for name, value in data["Component_Group_Level"].items():
                    if getattr(part_query.first(), name) == value:
                       print(f'{name}:{value} (Old) = (New) ==> OK')
                    else:
                        difference = True
                        print(f'{name}: (Old) {getattr(part_query.first(), name)} (New) {value} ==> dissimilarity ')       

                if difference:
                    while True:
                        user_input = input('Update the element? yes/no: ')

                        if user_input.lower() == 'yes':
                            part_query.update(**data["Component_Group_Level"])
                            break
                        elif user_input.lower() == 'no':
                            break
                        else:
                            print('Type yes/no')                                        
            else:
                print(f'Category with id={data["Component_Group_Level"]["id"]} "{data["Component_Group_Level"]["name"]}" does not exists in a database')                
                while True:
                    user_input = input('Craete the element? yes/no: ')

                    if user_input.lower() == 'yes':
                        new_object = Component_Group_Level.objects.create(**data["Component_Group_Level"])
                        new_object.save()
                        break
                    elif user_input.lower() == 'no':
                        break
                    else:
                        print('Type yes/no')   






def CreateOrGetCategory(object_dict):
    '''this function creates category, group and subgroup id category was not found, this function will alway return a subgroup''' 
    from NormMan.models import Component_Group_Level


    #status to define a path of import
    query_status = {
                        "subgroup_id" : False, 
                        "subgroup_name" : False,
                        "group_id" : False, 
                        "group_name" : False ,
                        "category_id" : False, 
                        "category_name" : False,
                        "group__category_model": False,
                        "subgroup__group_model": False,                
    }

    #fill query status

    query_category_id = Component_Group_Level.objects.filter(Q(id = object_dict["category_id"]))
                                                      
    if query_category_id:
        query_status['category_id'] = True           

    query_category_name = Component_Group_Level.objects.filter(Q(name = object_dict["category_name"]) )
                                                           
    if query_category_name:
        query_status['category_name']  = True    

    query_group_id = None #NormParts_Database_Group.objects.filter(Q(id = object_dict["group_id"]))
                                                      
    if query_group_id:
        query_status['group_id'] = True             
        
    query_group_name = None #NormParts_Database_Group.objects.filter(Q(name = object_dict["group_name"]) )
                                                           
    if query_group_name:
        query_status['group_name'] = True     

    query_subgroup_id = None #NormParts_Database_Subgroup.objects.filter(Q(id = object_dict["subgroup_id"]))
                                                      
    if query_subgroup_id:
        query_status['subgroup_id'] = True             
        
    query_subgroup_name = None #NormParts_Database_Subgroup.objects.filter(Q(name = object_dict["subgroup_name"]) )
                                                           
    if query_subgroup_name:
        query_status['subgroup_name'] = True  


    #id is deciding
    try:
        category_model_id = None #NormParts_Database_Group.objects.filter(Q(id = object_dict["group_id"]) ).get().category_model.id
        if category_model_id == object_dict["category_id"]:
            query_status['group__category_model'] = True  
        else:
            #id of requsted group are not matching this in database -> skip element potential risk of creation of duplcate categories or subgroups --> request will be ignored
            print("- requsted database structure: Category id not matching one requested  in meta.json, skipping object")  
            return None         
    except:     
        query_status['group__category_model'] = False 

    try:
        group_model_id = None #NormParts_Database_Subgroup.objects.filter(Q(id = object_dict["subgroup_id"]) ).get().group_model.id
        if group_model_id == object_dict["group_id"]:
            query_status['subgroup__group_model'] = True  
        else:
            #id of requsted group are not matching this in database -> skip element potential risk of creation of duplcate categories or subgroups --> request will be ignored 
            print("- requsted database structure: Group id not matching one requested in meta.json, skipping object")              
            return None 
    except:
        query_status['subgroup__group_model'] = True
     
    



    # everything was identified properly
    if all(v == True for v in query_status.values()):
        print(" - requsted database structure: fully matching")
        return  query_subgroup_id.get() 

    #when not

    #check if identified element could mess up the database like correct group but wrong category or correct subgroup but wrong group

    # if not query_status['group__category_model'] :
    #     if query_status['category_id']:
    #         #ids of group and subgroup are not matching those in request -> skip element potential risk of creation of duplcate categories or subgroups --> request will be ignored
    #         print("- requsted database structure: Total Mess skipping object")          
    #         return None 

    # if not query_status['subgroup__group_model']:
    #     if query_status['group_id']:
    #         #ids of group and subgroup are not matching those in request -> skip element potential risk of creation of duplcate categories or subgroups --> request will be ignored
    #         print("- requsted database structure: Total Mess skipping object")          
    #         return None 


    if query_status['category_id']:
        if  not query_status['category_name']:
            #name of the cateegory is different -> create new or use with database name
            print("- requsted database structure: category_name not matching. Keeping original")            


        if query_status['group_id'] and query_status['group__category_model'] :
            if  not query_status['group_name']:
                #name of the group is different -> create new or use with database name
                print("- requsted database structure: group_name not matching. Keeping original")  

            if query_status['subgroup_id'] and query_status['subgroup__group_model']:
                if  not query_status['subgroup_name']:
                    #name of the subgroup is different -> decide if new subgroup should be created
                    print("- requsted database structure: subgroup_name not matching. Keeping original")  
                return  query_subgroup_id.get()
            else:
                #subgroup of given id does not exists -> create a new one
                attr_dict={'id': object_dict['subgroup_id'] , 'name': object_dict['subgroup_name'], 'group_model': query_group_id.get()}                  
                subgroup = None #NormParts_Database_Subgroup(**attr_dict)
                subgroup.save() 
                return subgroup       
        else:
            #subgroup and group in request does not exist -> create a new group and subgroup
            attr_dict={'id': object_dict['group_id'] , 'name': object_dict['group_name'], 'category_model': query_category_id.get()}        
            group = None #NormParts_Database_Group(**attr_dict)
            group.save()

            attr_dict={'id': object_dict['subgroup_id'] , 'name': object_dict['subgroup_name'], 'group_model': group}                  
            subgroup = None #NormParts_Database_Subgroup(**attr_dict)
            subgroup.save()            
            return subgroup 

    else:
        #subgroup group and category in request does not exist -> create a new group and subgroup
        attr_dict={'id': object_dict['category_id'] , 'name': object_dict['category_name']}                   
        category = Component_Group_Level(**attr_dict) 
        category.save()

        attr_dict={'id': object_dict['group_id'] , 'name': object_dict['group_name'], 'category_model': category}        
        group = None #NormParts_Database_Group(**attr_dict)
        group.save()

        attr_dict={'id': object_dict['subgroup_id'] , 'name': object_dict['subgroup_name'], 'group_model': group}                  
        subgroup = None #NormParts_Database_Subgroup(**attr_dict)
        subgroup.save()  
        return subgroup 

    return None


