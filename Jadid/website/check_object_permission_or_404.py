from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from website.models import ProjectUser
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden

def check_object_permission_or_404(model, object_id, user, project_field='project_model'):
    # Retrieve the object
    obj = get_object_or_404(model, id=object_id)
    
    # Retrieve the project from the object using the specified project field
    project = getattr(obj, project_field).reference_project()
    
    # Check if the user is authorized for this project
    if ProjectUser.objects.filter(user=user, authorised_projects=project).exists():
        return obj
    else:
        raise HttpResponseForbidden("You do not have permission to view this object.")