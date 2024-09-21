from django import template
from CatiaFramework.models import Workflow_Action

register = template.Library()

@register.filter
def get_action(uuid:str = None) -> Workflow_Action:
    if uuid is None: return None
    try:
        query = Workflow_Action.objects.filter(UUID = uuid)
        if query:
            # We suppose there is only one specific action with specified uuid
            return query.first()
        else:
            return None
    except ValueError:
        return None
    
@register.filter
def stringify_field(uuid:object = None) -> str:
    if uuid is None: return None
    try:
        str_uuid = str(uuid)
        return str_uuid
    except ValueError:
        return None