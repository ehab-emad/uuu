import os, json, uuid
from django.conf import settings
from django.db import models
from math import *
from NormMan.models.help_functions import *
from NormMan.models.Component_Group_Level import *
from NormMan.scripts import render_allowed


def get_upload_to(instance, filename):
    '''Dynamic Upload To
    '''
    file_name, file_extension = os.path.splitext(filename)
    match file_extension:

        case ".stl":
            file_name = "stl_thumbnail"
        case ".png":
            file_name = "thumbnail"
        case ".jpg":
            file_name = "thumbnail"
        case ".pdf":
            file_name = "supplier_info"
        case ".CATPart":
            file_name = "catia_part"
        case ".xlsx":
            file_name = "configuration"
    path = os.path.relpath(f'{instance.data_path}/{file_name}{file_extension}', settings.MEDIA_ROOT).replace("\\", "/")
    return path


class NormParts_Shared_Component(models.Model):   #should be LCA_Process
    UUID = models.UUIDField(primary_key=True, verbose_name="UUID",   default=uuid.uuid4, editable=True)
    data_path = models.CharField(editable=True, blank=True,null=True, max_length=50000)

    name = models.CharField(max_length=1000,   editable=True, blank=True,null=True,)
    name_de = models.CharField(max_length=1000,   editable=True, blank=True,null=True,)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey("NormMan.ProjectUser_NormMan_Ref", models.SET_NULL, blank=True,null=True,)
    project_model=models.ForeignKey("NormMan.Project_NormMan_Ref", verbose_name="Project", on_delete=models.CASCADE, help_text ="Select a a project for Shared Component", default=None, blank=True, )



    thumbnail = models.ImageField(upload_to = get_upload_to, null=True, blank=True, verbose_name = "Part Image", max_length=50000)
    stl_thumbnail = models.FileField(upload_to = get_upload_to, blank= True, max_length=50000)
    file_catia_part = models.FileField(upload_to = get_upload_to, blank= True, max_length=50000)
    file_configuration = models.FileField(upload_to = get_upload_to, blank= True, max_length=50000)
    file_workflow_json = models.FileField(upload_to = get_upload_to, blank= True, max_length=5000)
    counter = models.IntegerField(default=0, blank=True,)
    supplier_name = models.CharField(max_length=200,   editable=True, blank=True,null=True,)
    supplier_part_number = models.CharField(max_length=200,   editable=True, blank=True,null=True,)
    oem_reference_name =  models.CharField(max_length=200,   editable=True, blank=True,null=True,)
    oem_reference_part_number =  models.CharField(max_length=200,   editable=True, blank=True,null=True,)


    ACCESSIBILITY_CHOICE= [
    ("PRIVATE", ("Private")),
    ("DATABASE_USERS", ("Database Users")),
    ("PROJECT_USERS", ("Project Users")),    
    ]

    accessibility = models.CharField(choices=ACCESSIBILITY_CHOICE, default="private",  max_length=50)


    TYPE_CHOICE= [
    ("COMPONENT", ("Component")),
    ("PART", ("Part")),
    ("SECTION", ("Section")),
    ("TEMPLATE", ("Template")),    
    ("WORKFLOW", ("Workflow")),         
    ]

    type = models.CharField(choices=TYPE_CHOICE, default="Component",  max_length=50)   

    parameters = models.JSONField(verbose_name="Catia Parameters", editable=True, null= True, blank=True)

    source=models.CharField(max_length=1000,   editable=True, blank=True, )

    material = models.CharField(max_length=70,   editable=True, blank=True, null=True,)
    source=models.CharField(max_length=1000,   editable=True, blank=True, null=True, )

    weight =models.FloatField(null=True, blank=True, )
    density = models.FloatField(null=True, blank=True, )


    @render_allowed
    def __init__(self, *args, **kwargs):
        super(NormParts_Shared_Component, self).__init__(*args, **kwargs)      

    def as_dict(self) ->dict:
        '''this function will create custom instance process dictionary
        '''
        from django.forms import model_to_dict
        entry = {}
        entry.update(model_to_dict(self))


        return entry

    def save(self, *args, **kwargs):
        super(NormParts_Shared_Component, self).save(*args, **kwargs)
        #generate json for other frameworks
        entry = {}
        entry[type(self).__name__] = self.as_dict()

        uuid_parent = self.data_path.split("/")[-3][-36:]
        root_object = Component_Group_Level.objects.filter(UUID = uuid_parent)
        o_array = []
        entry["db_structure"] ={}

        entry_actual = {}
        entry_actual = entry["db_structure"]

        def walk(o, entry_actual):
            ''' this function will search recursive a database structure and prepare input json for import
            '''   
            o_dict = {}            
            if o.parent_group is not None:
                parent_uuid = 'fd9cea85-83d8-4a79-a1f1-22d1dd578516' # Hardcoded because of problem with root!!
                if str(o.parent_group.UUID) == parent_uuid and str(o.UUID) == parent_uuid:
                    o.parent_group = None 
                    o.save()
            if  o.parent_group is not None:
                o_dict['category_group_uuid'] = o.parent_group.UUID
                o_dict['category_group_name'] = o.parent_group.name

            else:
                o_dict['parent_group_uuid'] = None
                o_dict['parent_group_name'] = None
                return
            if o.parent_group == root_object.first():
                o_dict['parent_group_uuid'] = None
                o_dict['parent_group_name'] = None
                return
            o_dict['parent'] = {} 

            entry_actual.update(o_dict)
            entry_actual = entry_actual['parent']

            query = Component_Group_Level.objects.filter(UUID = o.parent_group.UUID)
            
            for object in query:
                if query:
                    walk(object, entry_actual)

        if root_object: 
            walk(root_object.first(), entry_actual)

        out_file = open(os.path.join(settings.MEDIA_ROOT, self.data_path, "meta.json"), "w")
        json.dump(entry, out_file, indent = 6, cls=ExtendedEncoder)
        out_file.close()

    # def get_stl_thumbnail(self):
    #     '''returns path to stl_thumbnail or None when not available'''    
    #     return os.path.join(self.data_path, "stl_thumbnail.stl")


    class Meta:
        app_label = 'NormMan'
    def __str__(self):
        return str(self.name)





