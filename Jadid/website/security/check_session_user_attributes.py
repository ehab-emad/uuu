
def check_if_user_in_roles(request, roles) -> bool:
    '''
    This function checks if user satisfies roles 
    '''
    # Check if the input is a list of strings, user cannot satisfy roles if one of the role is not a string
    if not isinstance(roles, list) or not all(isinstance(item, str) for item in roles):
        return False

    session_roles = request.session.get('roles', '').split(',')

    # Check if all roles are in session_roles
    for role in roles:
        if role not in session_roles:
            return False

    # If all roles are found, return True
    return True



def check_if_user_in_groups(request, groups) -> bool:
    '''
    This function checks if user satisfies groups 
    '''
    # Check if the input is a list of strings, user cannot satisfy roles if one of the role is not a string
    if not isinstance(groups, list) or not all(isinstance(item, str) for item in groups):
        return False

    session_groups = request.session.get('groups', '').split(',')

    # Check if all roles are in session_roles
    for role in groups:
        if role not in session_groups:
            return False

    # If all roles are found, return True
    return True