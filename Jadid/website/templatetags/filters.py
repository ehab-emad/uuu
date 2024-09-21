from django import template
from django.db.models import Q
import uuid

register = template.Library()

@register.filter
def split(value:str=None) -> uuid.UUID:    
    return uuid.UUID(value.split("/")[-3][-36:]) if value is not None else None


@register.filter
def validate_uuid(value:object=None) -> bool:
    if value is None: return False
    try:
        uuid.UUID(value, version = 4)
        return True
    except ValueError:
        return False    


@register.filter
def check_parent(request, cur_obj) -> bool:
    created_objects = request.user.projectuser.current_workflow_session.created_objects
    parent, is_child = None, True if "Type" in cur_obj["properties"] else False     
    for obj in created_objects.values():
        if "ParentUID" in cur_obj["properties"]:
            if obj["properties"]["UUID"]["value"] == cur_obj["properties"]["ParentUID"]["value"]:
                parent = obj
                break
    if parent is not None:
        return parent["properties"]["Selected"]["value"]        
    else:
        if is_child:
            return False
        else:
            return True


@register.filter
def check_project_instances(objects, request) -> int:
    return objects.filter(Q(project_model_id = request.user.projectuser.current_project_id) | Q(accessibility = "DATABASE_USERS")).count()
