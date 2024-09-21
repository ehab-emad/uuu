# Authentication utilities
from datetime import date, timedelta


def is_professional_user(groups, app = ""):
    """Checks if the user is a professional user for an app (if given) based on its groups"""
    if isinstance(groups, str):
        groups_list = groups.split(",")
    else:  
        groups_list = groups

    return len(list(filter(lambda g: "user-professional" in g and app in g, groups_list))) > 0

def is_account_expired(user):
    """Checks if the user account has expired"""
    return user.projectuser.expiration_date < date.today() if user.projectuser.expiration_date else False
