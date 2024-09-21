from functools import wraps
from django.apps import apps
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

"""
General ToDo: for each security measure endpoint create inner body that does what should be done.
  Example: leading from project update, the resources are yielded based on given pre-definitions 
  and communicated further. The signature has to be complaint, but so can be the yielded resource 
  passed to next function, which means the decorator is able to produce value, not only to evaluate 
  execution.

In project security check, the user that is to posses an access to resource 
requested is to be checked for project right regarding the context.

ToDo: kwargs have to be defined generically, which means the name of has to be represented properly. Problem 
  might be, that different models have different structures.
  1. which ids and names do exist
  2. are they defined the same as in url?
  3. is project_field e.g. reference_project always the same?
"""

_yield_instance = lambda a, m, **kwargs: None if not (a is not None and m is not None) else get_object_or_404(apps.get_model(a, m), **kwargs)
_yield_project = lambda instance: None if instance is None else getattr(instance, 'project_model').reference_project
_is_owner = lambda i, r: False if (i is None or r is None) else i.owner.reference_projectuser == r.user.projectuser


def project_security_check(func, app_name=None, model_name=None, field=None):
    # Security Measure Level 1 - project check
    @wraps(func)
    def wrapper(request, *args, **kwargs):        
        requested_instance = _yield_instance(app_name, model_name, **kwargs)
        ref_project = _yield_project(requested_instance)
        condition = ref_project in request.user.projectuser.authorised_projects.all() # here probably better condition
        if condition:
            kwargs['requested_instance'] = requested_instance   # communication of created data
            return func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("You do not have permission to view this object.")
    return wrapper


def object_security_check(func, app_name=None, model_name=None, field=None):
    # Security Measure Level 2 - object check
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        requested_instance = kwargs.get('requested_instance', None)
        # ref_project = _yield_project(requested_instance)
        condition = requested_instance is not None
        if condition:
            return func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("You do not have permission to view this object.")
    return project_security_check(wrapper, app_name=app_name, model_name=model_name, field=field)


def owner_security_check(func, app_name=None, model_name=None, field=None, level=1):
    # Security Measure Level 3 - ownership check 
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        requested_instance = kwargs.get('requested_instance', None)
        # ref_project = _yield_project(requested_instance)
        if requested_instance:
            if _is_owner(requested_instance, request):
                return func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden("You do not have permission to view this object.")
    if level == 1:
        return project_security_check(wrapper, app_name=app_name, model_name=model_name, field=field)
    elif level == 2:
        return object_security_check(wrapper, app_name=app_name, model_name=model_name, field=field)