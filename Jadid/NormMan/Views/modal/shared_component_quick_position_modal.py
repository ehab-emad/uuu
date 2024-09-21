import json 
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from NormMan.models import NormParts_Shared_Component


def shared_component_quick_position_modal(request, uuid) -> JsonResponse: 
    # -> This function opens a window for quick positioning tool.
    target = 'modal/shared_component_quick_position/shared_component_quick_position_modal.html'
    query_component = NormParts_Shared_Component.objects.filter(UUID = uuid)    
    shared_component = get_object_or_404(NormParts_Shared_Component, pk=uuid) if query_component else None
    if shared_component is None:
        return JsonResponse(dict())
    from NormMan.forms import NormPartSelectConfigurationForm
    form = NormPartSelectConfigurationForm(instance=shared_component)      
    data = {
        'form_is_valid': True if request.method == 'POST' else False,
        'html_form': render_to_string(target, {'form': form}, request=request)
    }
    return JsonResponse(data)


def shared_component_quick_position_callback(request):
    # -> Execution of a new position request
    object_execution_instances = list()
    return_dict = {
        "Name": None, 
        "Description": None,
        "shared_component" : None,
        "metadata": dict(),
        "parameters": dict(),        
        "required_objects": dict()
        }
    object_execution_instances.append({request.POST['instance_id']: return_dict})
    async_to_sync(get_channel_layer().group_send)(
        'chat_' + request.user.username,
        {
            'type': 'framework_command',
            'message': json.dumps({
                'user': request.user.username, 
                'trigger': "QuickPositionCallback",
                'framework_action_uuid': "7641437f-bc82-46f2-91f8-35f78c523998", # Hardcoded UUID based on currently defined Function UUID
                'executed_instances': object_execution_instances
            })
        }
    )    
    return JsonResponse(dict())


def shared_component_quick_position_submit(request):
    # -> Submit of a selected properties
    object_execution_instances = list()
    return_dict = {
        "Name": None, 
        "Description": None,
        "shared_component" : None,
        "metadata": dict(),
        "parameters": dict(),        
        "required_objects": dict()
        }
    object_execution_instances.append({request.POST['instance_id']: return_dict})
    async_to_sync(get_channel_layer().group_send)(
        'chat_' + request.user.username,
        {
            'type': 'framework_command',
            'message': json.dumps({                                                    
                'user': request.user.username, 
                'trigger': "execute_action",
                'framework_action_uuid': "aa609b37-2ad1-4a7a-bd2d-85433cac6eb9", # Hardcoded UUID based on currently defined Function UUID                
                'executed_instances': object_execution_instances,
                'shared_component_uuid' : request.POST['shared_component_uuid'],
                'parameters': request.POST['parameters'] ,
                'config': request.POST['config']
            })
        }
    )    
    return JsonResponse(dict())