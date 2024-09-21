import inspect
from functools import wraps
from urllib.parse import urlparse
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.shortcuts import resolve_url
from .keycloak_manager import keycloak_manager
from django.shortcuts import redirect
from .auth import is_account_expired
from django.http import JsonResponse
from collections.abc import Iterable
def _get_function_arguments_dict(func, *args, **kwargs):
    """
    Gets request function and returns dictionary of its arguments.
    """
    fcn_spec = inspect.getfullargspec(func)
    args_dict = kwargs
    for index, arg in enumerate(args):
        args_dict[fcn_spec.args[index+1]] = arg # +1 because the first argument (request) is skipped
    return args_dict

def _check_request(condition_function, permission_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Universal wrapper for checking permission to open the view based on request data.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapper_view(request, *args, **kwargs):
            args_dict = _get_function_arguments_dict(view_func, *args, **kwargs)
            if condition_function(request, args_dict):
                return view_func(request, *args, **kwargs)
            else:
                path = request.build_absolute_uri()
                resolved_login_url = resolve_url(permission_url or settings.LOGIN_URL)
                # If the login url is the same scheme and net location then just
                # use the path as the "next" url.
                login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
                current_scheme, current_netloc = urlparse(path)[:2]
                if (not login_scheme or login_scheme == current_scheme) and (
                    not login_netloc or login_netloc == current_netloc
                ):
                    path = request.get_full_path()
                from django.contrib.auth.views import redirect_to_login

                #here it is important to differentiate if we are not hanfling ajax request if yes return redirect pattern
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    # Create a dictionary with the url_redirect property
                    data = {
                        'url_redirect': resolved_login_url,
                        'status': 'error',
                        'message': 'User not permitted: ' + permission_url,
                    }
                    return JsonResponse(data)
                else:
                    return redirect_to_login(path, resolved_login_url, redirect_field_name)

                
        return _wrapper_view

    return decorator

def _check_keycloak_status(function=None):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapper_view(request, *args, **kwargs):
            refresh_token = request.session.get('refresh_token', None)
            # print(f"{group_name} in {session_groups}")
            if keycloak_manager.is_user_logged_in(refresh_token):
                request.session['expiration_timestamp'] = keycloak_manager.get_expiration_timestamp(refresh_token)
                return view_func(request, *args, **kwargs)                
            else:
                return redirect('/user/login')
        return _wrapper_view
    if function:
        return decorator(function)
    return decorator

## Checking for a account expiration
def _condition_account_not_expired(request, args_dict) -> bool:
    """
    Function that checks that the account has not expired from request.
    """
    return not is_account_expired(request.user)

def _account_not_expired(
    function=None, redirect_field_name=REDIRECT_FIELD_NAME, permission_url="/user/login"
):
    """
    Decorator for views that checks that the user account does not expired, redirecting
    to the error page if necessary.
    """
    actual_decorator = _check_request(
        condition_function=_condition_account_not_expired,
        permission_url=permission_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

## Checking for a group access
def _condition_account_in_group_factory(app_group=None,  group_names = None, role_names = None):
    """
    Factory for a condition that checks for a group access. The factory is needed for putting group name in a condition.
    """
    def _condition_account_in_group(request, args_dict) -> bool:
        session_groups = request.session.get('groups', '').split(',')
        session_roles = request.session.get('roles', '').split(',')

        # Check if app_group is in session_groups, return False if not
        if app_group not in session_groups:
            return False

        # Check if any group in group_names is not in session_groups
        if group_names:
            for group in group_names:
                if group not in session_groups:
                    return False

        # Check if any role in role_names is not in session_roles
        if role_names:                
            for role in role_names:
                if role not in session_roles:
                    return False

        # If all conditions are met, return True
        return True
    return _condition_account_in_group
## Checking for a group access
def _group_required(
    function=None, redirect_field_name=REDIRECT_FIELD_NAME, permission_url="/user/login", app_group=None,  group_names = None, role_names = None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = _check_request(
        condition_function=_condition_account_in_group_factory(app_group,  group_names, role_names),
        permission_url=permission_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

## Public functions/decorators

def account_not_expired(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None, permission_url="/err/account_expired"):
    """
    Decorator for views that checks that the user is logged in and that the user account does not expired.
    """
    return login_required(_account_not_expired(function, redirect_field_name, permission_url), redirect_field_name, login_url)

def group_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None, permission_url="/err/not_in_group", app_group=None,  group_names = None, role_names = None):
    """
    Decorator for views that checks that the user is logged in and that the user is in the group.
    """
    return login_required(_group_required(function, redirect_field_name, permission_url, app_group,  group_names, role_names), redirect_field_name, login_url)

def check_keycloak_status(function=None):
    """
    Decorator for views that checks that the user is logged in and that the user is in the group.
    """
    return _check_keycloak_status(function)

def keycloak_user_permissions(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None, permission_url="/err/not_in_group", app_group=None,  group_names = None, role_names = None):
    """
    Decorator for views that checks that the user is logged in and that the user is in the group.
    """
    return login_required(_group_required(function, redirect_field_name, permission_url, app_group,  group_names, role_names), redirect_field_name, login_url)

def group_required_account_not_expired(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None, permission_url="/err/not_in_group", app_group=None,  group_names = None, role_names = None):
    """
    Decorator for views that checks that the user is logged in, the user account does not expired and that the user is in the group.
    """
    return login_required(_account_not_expired(_group_required(function, redirect_field_name, permission_url, app_group,  group_names, role_names), redirect_field_name, "/err/account_expired"), redirect_field_name, login_url)