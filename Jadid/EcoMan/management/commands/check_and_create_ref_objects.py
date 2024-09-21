from NormMan.models import Component_Group_Level
import os, json
from django  import apps
from django.core.serializers.json import DjangoJSONEncoder
from django.core.management.base import BaseCommand
from django.db.models.fields.files import ImageFieldFile, FieldFile
from django.db.models.fields.related import ForeignKey
from NormMan.models import Component_Group_Level, Project_NormMan_Ref, ProjectUser_NormMan_Ref
from NormMan.scripts.validate_uuid import is_valid_uuid
import website.settings as settings
from django.shortcuts import  get_object_or_404

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
        '''
        This script is checking if based on the main website app all ref objects are existing
        '''
        from EcoMan.models import Project_EcoMan_Ref
        from EcoMan.models import ProjectUser_EcoMan_Ref
        from EcoMan.models import Vehicle_EcoMan_Ref        

        from website.models import Project
        from website.models import ProjectUser
        from website.models import Vehicle


        query_projects = Project.objects.all()
        query_projectsusers = ProjectUser.objects.all()
        query_vehicle = Vehicle.objects.all()

        for object in query_projects:
            project_ref = Project_EcoMan_Ref.objects.filter(UUID = str(object.UUID))
            if not project_ref:
                        Project_EcoMan_Ref.objects.create(UUID = str(object.UUID))                                                    

        for object in query_projectsusers:
            projectuser_ref = ProjectUser_EcoMan_Ref.objects.filter(UUID = str(object.UUID))
            if not projectuser_ref:
                        ProjectUser_EcoMan_Ref.objects.create(UUID = str(object.UUID))     

        for object in query_vehicle:
            vehicle_ref = Vehicle_EcoMan_Ref.objects.filter(UUID = str(object.UUID))
            if not projectuser_ref:
                        Vehicle_EcoMan_Ref.objects.create(UUID = str(object.UUID))     

        return