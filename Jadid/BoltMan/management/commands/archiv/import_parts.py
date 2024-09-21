import os, uuid, sys, click, scripts, json
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.fields.files import ImageFieldFile
from django.core.management.base import BaseCommand
from django.db.models import Q


def is_valid_uuid(uuid_to_test, version=4) -> bool:
    """
    Check if uuid_to_test is a valid UUID.

     Parameters
    ----------
    uuid_to_test : str
    version : {1, 2, 3, 4}

     Returns
    -------
    `True` if uuid_to_test is a valid UUID, otherwise `False`.

     Examples
    --------
    >>> is_valid_uuid('c9bf9e57-1685-4c89-bafb-ff5af830be8a')
    True
    >>> is_valid_uuid('c9bf9e58')
    False
    """

    try:
        uuid_obj = uuid.UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test



class Command(BaseCommand):

    def handle(self, *args, **options):

        object_directory_list = [x[0] for x in os.walk(os.path.join("media", "norm_parts"))]
        #remove root directory from the list
        object_directory_list.pop(0)
        for directoryy in object_directory_list:
            dataa = [filenames[2] for filenames in os.walk(directoryy)][0]
            #here postgre will be filled with information

            #get object uuid
            is_object_uuid_valid = is_valid_uuid(directoryy[-36:], 4)
            object_uuid = directoryy[-36:]
            print("Importing Object: " + object_uuid)
            if is_object_uuid_valid :
                print("- UUID is valid")
            else:
                print("- UUID is invalid. Check definition of UUID 4")
                continue
            #check if uuid already exists in a database
            part_query = None #NormParts_Database_Part.objects.filter(UUID = object_uuid)

            if part_query:
               print("- already exists in a database, object uuid must be unique. Ignore if expected")
               continue
            #find json speecific meta file and check it
            if any([is_object_uuid_valid]):
                if "meta.json" in dataa:
                    with open(os.path.join(directoryy, "meta.json" )) as json_file:
                        meta = json.load(json_file)
                        if 'NormParts_Database_Part' in meta:
                            #find foreignkey objects if they not exists add them

                            category_dictionary ={}
                            category_dictionary = meta['db_structure']
                            subgroup_object = CreateOrGetCategory(category_dictionary)
                            if subgroup_object == None:
                                continue

                                #remove fields which are not used directly in 'NormParts_Database_Part'
                            meta['NormParts_Database_Part']['subgroup_model'] = subgroup_object
                            meta['NormParts_Database_Part']['UUID'] = object_uuid

                            # here objects wil generated and imported to the database
                            new_object = None #NormParts_Database_Part.objects.create(**meta['NormParts_Database_Part'])
                            new_object.save()
                            print("- import success")
                        else:
                            print("- has correct UUID but meta.json seems to be not correct. Please import object manually")
                            continue






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
        print("- requsted database structure: fully matching")
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
                attr_dict={'id': object_dict['subgroup_id'] , 'name': object_dict['subgroup_name'], 'name_de': object_dict['subgroup_name_de'], 'group_model': query_group_id.get()}
                subgroup = None #NormParts_Database_Subgroup(**attr_dict)
                subgroup.save()
                return subgroup
        else:
            #subgroup and group in request does not exist -> create a new group and subgroup
            attr_dict={'id': object_dict['group_id'] , 'name': object_dict['group_name'], 'name_de': object_dict['group_name_de'], 'category_model': query_category_id.get()}
            group = None #NormParts_Database_Group(**attr_dict)
            group.save()

            attr_dict={'id': object_dict['subgroup_id'] , 'name': object_dict['subgroup_name'], 'name_de': object_dict['subgroup_name_de'], 'group_model': group}
            subgroup = None #NormParts_Database_Subgroup(**attr_dict)
            subgroup.save()
            return subgroup

    else:
        #subgroup group and category in request does not exist -> create a new group and subgroup
        attr_dict={'id': object_dict['category_id'] , 'name': object_dict['category_name'], 'name_de': object_dict['category_name_de']}
        category = Component_Group_Level(**attr_dict)
        category.save()

        attr_dict={'id': object_dict['group_id'] , 'name': object_dict['group_name'], 'name_de': object_dict['group_name_de'], 'category_model': category}
        group = None #NormParts_Database_Group(**attr_dict)
        group.save()

        attr_dict={'id': object_dict['subgroup_id'] , 'name': object_dict['subgroup_name'], 'name_de': object_dict['subgroup_name_de'], 'group_model': group}
        subgroup = None #NormParts_Database_Subgroup(**attr_dict)
        subgroup.save()
        return subgroup

    return None


