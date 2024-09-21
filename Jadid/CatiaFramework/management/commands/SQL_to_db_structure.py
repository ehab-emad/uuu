from NormMan.models import Component_Group_Level
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.fields.files import ImageFieldFile, FieldFile
from django.db.models.fields.related import ForeignKey
from django.core.management.base import BaseCommand
from django.db.models import Q
import os, glob
import uuid
import unicodedata
import re
import website.settings as settings


class Command(BaseCommand):

    def handle(self, *args, **options):
        path_db_structure = os.path.join( settings.MEDIA_ROOT, "norm_parts\\db_structure\\")
        relative_path = os.path.join( settings.MEDIA_ROOT)


        root_object = Component_Group_Level.objects.filter(group_depth_level = 0).first()

        def walk(o, path):
            ''' this function will create folder structure and generate meta data
            '''     
            #get all children friom parent object
            directory = o.name + '_UUID_'+ o.UUID
            directory = re.sub('\s+', '_', directory)
            directory = re.sub('[^\w.-]', '', directory)
            path = os.path.join( path, directory )

            if not os.path.exists(path):
                os.mkdir(path)

            o.data_path = os.path.relpath(path, relative_path)
            o.save()
    
            query =  Component_Group_Level.objects.filter(parent_group__UUID = o.UUID)
            
            for object in query:
                print(object.name)
                walk(object, path)

        walk(root_object, path_db_structure)


        return