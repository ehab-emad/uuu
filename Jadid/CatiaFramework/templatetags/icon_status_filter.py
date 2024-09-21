
from django import template
from django.utils.html import mark_safe
from CatiaFramework.models import Workflow_Stage, Workflow_Action, Workflow_Object, Workflow
import uuid
register = template.Library()

@register.filter
def status_icon(obj):
    """
    Custom template filter to get the status icon for YourModel instances.
    """

    if isinstance(obj, str):
        query = Workflow.objects.filter(UUID = obj)
        if not query:
            query = Workflow_Stage.objects.filter(UUID = obj)
        if not query:
            query = Workflow_Object.objects.filter(UUID = obj)
        if not query:
            query = Workflow_Action.objects.filter(UUID = obj)
        if query:
            obj = query.get()
            obj_UUID = str(obj.UUID)
            obj_class_name =  obj.__class__.__name__

    if isinstance(obj, dict):            
        obj_class_name =  obj["CLASS_name"]
        obj_UUID = obj["UUID"]
       



    if obj_class_name == "Workflow_Stage":
        return mark_safe(Workflow_Stage.objects.filter(UUID = obj_UUID).get().get_status_icon())
    if obj_class_name == "Workflow_Action":
        return mark_safe(Workflow_Action.objects.filter(UUID = obj_UUID).get().get_status_icon())
    if obj_class_name == "Workflow_Object":
        return mark_safe(Workflow_Object.objects.filter(UUID = obj_UUID).get().get_status_icon()) 
    if obj_class_name == "Workflow":
        return mark_safe(Workflow.objects.filter(UUID = obj_UUID).get().get_status_icon())

    # if obj["CLASS_name"] == "Workflow_Stage":
    #     return mark_safe(Workflow_Stage.objects.filter(UUID = obj["UUID"]).get().get_status_icon())
    # if obj["CLASS_name"] == "Workflow_Action":
    #     return mark_safe(Workflow_Action.objects.filter(UUID = obj["UUID"]).get().get_status_icon())
    # if obj["CLASS_name"] == "Workflow_Object":
    #     return mark_safe(Workflow_Object.objects.filter(UUID = obj["UUID"]).get().get_status_icon()) 
    # if obj["CLASS_name"] == "Workflow":
    #     return mark_safe(Workflow.objects.filter(UUID = obj["UUID"]).get().get_status_icon())


    return ''
