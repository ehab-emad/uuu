from EcoMan.models import Lca_Database_Process
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
        query = Lca_Database_Process.objects.all()
        for object in query:
            object.unit = object.unit.strip()
            object.save()
        return