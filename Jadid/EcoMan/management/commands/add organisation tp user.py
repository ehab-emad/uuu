from NormMan.models import Component_Group_Level
import json
from tkinter import filedialog as fd
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.fields.files import ImageFieldFile
from django.core.management.base import BaseCommand
from website.models import ProjectUser, Project
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
        query = ProjectUser.objects.all()
        organisation_project = Project.objects.filter(name = "Organisation_LCA_Project" ).get()
        for object in query:
            object.authorised_projects.add(organisation_project)
            object.save()
        return