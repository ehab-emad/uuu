import os, json
from django.core.management.base import BaseCommand
from CatiaFramework.models import *


def modify_dict(in_dict: dict) -> None:
    """
    Modification of non complementary fields of dictionary
    obtained from transition from class to dictionary.
    """
    for key, value in in_dict.items():
        if isinstance(value, ImageFieldFile):
            if value:
                path = str(os.path.relpath(value.path))
                log_med = [int(obj == 'media') for obj in path.split(os.sep)]
                log_med_shifted = log_med[1:] + [log_med[0]]
                media_extra = [1 if log + log_shifted > 1 else 0 for log, log_shifted in zip(log_med, log_med_shifted)]
                path = os.path.join(*[spl for spl, log in zip(path.split(os.sep), media_extra) if not log])
                in_dict[key] = path
            else:
                in_dict[key] = None
        if isinstance(value, dict):
            modify_dict(value)
        if isinstance(value, list):
            [modify_dict(obj) for obj in value if isinstance(obj, dict)]                                



class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        Creation of JSON dictionary then to be used for recreation procedure.
        """
        templates = Workflow.objects.filter(type="DATABASE_TEMPLATE")
        instances = Workflow.objects.filter(type="USER_SESSION")
        templates_json, instances_json = dict(), dict()
        [templates_json.update({str(template.UUID): {'workflow': template.as_dict(), 'structure': template.get_structure_dict()}}) for template in templates]
        [instances_json.update({str(instance.UUID): {'workflow': instance.as_dict(), 'structure': instance.get_structure_dict()}}) for instance in instances]
        modify_dict(templates_json), modify_dict(instances_json)
        with open(os.path.join(os.getcwd(), "workflow_dict.json"), "w") as file:
            json.dump({'templates': templates_json, 'instances': instances_json}, file, indent=3)
