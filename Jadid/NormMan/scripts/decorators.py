from functools import wraps
from NormMan.scripts.validate_uuid import is_valid_uuid
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string

def render_allowed(func):
    """
    This decorator is constructed to obtain object whilst rendering it and should 
    offer its rendered shape only if there is a condition met. However, based on
    not implemented request as input argument into __init__ function of django's Model,
    there is no direct access to session information thus it cannot be decided whether
    to render object or not. for that, there might/must be implemented another, more
    advanced logic. For now, the wrapped is present but not utilized.
    """
    @wraps(func)
    def wrapper(object_to_render, *args, **kwargs):
        # If everything's OK
        return func(object_to_render, *args, **kwargs)
        # Otherwise, do not render or render restrictedly
    return wrapper

def user_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        # If everything's OK
        # return func(request, *args, **kwargs)
        # Otherwise, do not render or render restrictedly
        uuid = kwargs.get('uuid', None)
        if is_valid_uuid(uuid):
            from NormMan.models import NormParts_Shared_Component
            shared_component = get_object_or_404(NormParts_Shared_Component, UUID = uuid)
            if request.user.projectuser.UUID == shared_component.owner_id:
                return func(request, *args, **kwargs)
            else:
                context = {'shared_component': shared_component}
                data = {'html_form': render_to_string('modal/shared_component/user_auth.html', context, request=request,)}
                return JsonResponse(data)
    return wrapper