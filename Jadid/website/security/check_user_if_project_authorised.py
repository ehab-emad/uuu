
def check_if_user_in_project(project, request = None, projectuser = None) -> bool:
    '''
    This function checks if user belongs to project 
    '''
    #find projectuser in input parameters
    if projectuser:
        pass
    if request and projectuser == None:
        projectuser = request.user.projectuser
    #get all projectuser authorised projects
    authorised_projects = request.user.projectuser.authorised_projects.all()

    return authorised_projects.filter(id=project.id).exists()
    