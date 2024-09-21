
import  json
from django.contrib.staticfiles.storage import staticfiles_storage
from CatiaFramework.models import DotNet_ProjectFolder, DotNet_Component, Project_CatiaFramework_Ref, ProjectUser_CatiaFramework_Ref
import os, json, uuid
from django.shortcuts import redirect
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.fields.files import ImageFieldFile, FieldFile
from django.db.models.fields.related import ForeignKey
from CatiaFramework.scripts.validate_uuid import is_valid_uuid
class ExtendedEncoder(DjangoJSONEncoder):
    def default(self, check_field):
        if isinstance(check_field, ImageFieldFile) or isinstance(check_field, FieldFile):
            return str(check_field)
        elif isinstance(check_field, ForeignKey):
            return str(check_field)
        else:
            return super().default(check_field)
def vb_project_import(request):
    '''
    Run through static database and create a corresponding replica in SQL database.
    Operation just modifies current database and does not produce any value.
    :return: None
    '''
    result={}
    data={}
    path_to_json_template = staticfiles_storage.path('CatiaFramework/Framework_Listing_1.json')
    f = open(path_to_json_template)
    data = json.load(f)


    #in testing we will remove all objects before creation of new ones

    query = DotNet_Component.objects.all()
    for object in query:
        object.delete()
    query = DotNet_ProjectFolder.objects.all()
    for object in query:
        object.delete()

    projectuser = ProjectUser_CatiaFramework_Ref.objects.filter(nickname = 'admin').get()
    projectmodel = projectuser.reference_projectuser.sandbox_project
    def process_json_data(data, i_projectfolder):
        if isinstance(data, dict):
            for key, value in data.items():
                
                if ".vb" in key and "\\" in key:   #handling vb files
                    o_projectfolder = DotNet_ProjectFolder.objects.create(UUID = uuid.uuid4(), 
                                                                                name = key, 
                                                                                parent_folder = i_projectfolder,
                                                                                group_depth_level = i_projectfolder.group_depth_level +1,
                                                                                owner = projectuser
                                                                                )
                    o_projectfolder = i_projectfolder
                    process_json_data(value, o_projectfolder)  # Recursive call for nested objects                   
                if "\\" in key and not ".vb" in key:              #handling of folders  files
                    o_projectfolder = DotNet_ProjectFolder.objects.create(UUID = uuid.uuid4(), 
                                                                                name = key, 
                                                                                parent_folder = i_projectfolder,
                                                                                group_depth_level = i_projectfolder.group_depth_level +1,
                                                                                owner = projectuser)
                    process_json_data(value, o_projectfolder)  # Recursive call for nested objects
                if is_valid_uuid(key):       #handling of vbdotnet components

                    
                    if value['blockType'] == "Module":
                        type = "VBDOTNET_MODULE"
                    if value['blockType'] == "Class":
                        type = "VBDOTNET_CLASS"
                    if value['blockType'] == "Sub":
                        type = "VBDOTNET_SUB"                      #standalone Sub   
                    if value['blockType'] == "Function":
                        type = "VBDOTNET_FUNCION"                   #STANDALONE FUNCTION'


                    o_vbdotnetcomponent = DotNet_Component.objects.create(UUID = key, 
                                                                                name = value['blockName'], 
                                                                                content_section = value['blockContent'], 
                                                                                comment_section = value['blockComment'],  
                                                                                summary_section = value['summary'],     
                                                                                access_modifier = value['accessModifier'],
                                                                                owner = projectuser, 
                                                                                type = type, 
                                                                                project_model = Project_CatiaFramework_Ref.objects.filter(UUID = projectmodel.UUID).get()
                                                                                )       
                    print('-------------------------------------------')
                    print(value['blockComment'])             
                    i_projectfolder.dotnet_components.add(o_vbdotnetcomponent)

                    if 'children' in value:
                        for mkey, mvalue in value['children'].items():
                            if mvalue['blockType'] == "Sub":
                                type = "VBDOTNET_SUB"
                            if mvalue['blockType'] == "Property":
                                type = "VBDOTNET_PROPERTY"
                            o_vbdotnetcomponent = DotNet_Component.objects.create(UUID = mkey, 
                                                                                        name = mvalue['blockName'], 
                                                                                        content_section = mvalue['blockContent'], 
                                                                                        comment_section = value['blockComment'], 
                                                                                        summary_section = value['summary'],         
                                                                                        access_modifier = mvalue['accessModifier'],
                                                                                        owner = projectuser, 
                                                                                        type = type, 
                                                                                        project_model = Project_CatiaFramework_Ref.objects.filter(UUID = projectmodel.UUID).get()
                                                                                        )  
                     
                            print('--------------CHILD_ITEM----------------------')
                            print(value['blockComment'])                           
                            i_projectfolder.dotnet_components.add(o_vbdotnetcomponent)
                    i_projectfolder.save()
                    #include shared components in all parent Component_groups
                    if i_projectfolder.parent_folder:
                        parent_project_folder = i_projectfolder.parent_folder
                        i=1
                        while i>0:
                            parent_project_folder.dotnet_components.add(o_vbdotnetcomponent)
                            parent_project_folder.save()
                            if parent_project_folder.parent_folder: 
                                parent_project_folder = parent_project_folder.parent_folder
                            else:
                                break

        elif isinstance(data, list):
            for item in data:
                process_json_data(item) 

    #check if root object exists when not create one
    root_projectfolder = DotNet_ProjectFolder.objects.filter(UUID = 'fd9cea85-83d8-4a79-a1f1-22d1dd578516')
    if root_projectfolder:
        root_projectfolder = root_projectfolder.first()
    else:
        #create root object and pass it to recursive function
        root_projectfolder = DotNet_ProjectFolder.objects.create(UUID = 'fd9cea85-83d8-4a79-a1f1-22d1dd578516', 
                                                                    name = 'FRAMEWORK:ROOT', 
                                                                    parent_folder = None,
                                                                    group_depth_level = 0)
        root_projectfolder.save()


    root_projectfolder.save()           
    process_json_data(data['\\Framework'], root_projectfolder)


    f.close()
    return redirect(request.META.get('HTTP_REFERER'))