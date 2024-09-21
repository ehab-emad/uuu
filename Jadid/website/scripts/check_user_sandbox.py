#functions check if user has sandbox project and vehicle if not it will create and assign foreign keys
from website.models import Project
from website.models import Vehicle

def check_user_sandbox(userobj):
    """
    This function checks if active ProjectUser has available Sandbox_Vehicle object and Sandbox Project Objects assigned. 
    If not they will be assigned or even created if necessary
    """
    if not userobj.is_authenticated:
        return 
    if userobj.projectuser.sandbox_project is None: 
        query = Project.objects.filter(isusersandbox= True ,  owner_id = userobj.id)
        if query:
            sandbox_project = query.first()
        else:
            sandbox_project = Project.objects.create(network_number = 0, name = "Sandbox Project", owner = userobj,  isusersandbox = True)
    else:
        sandbox_project = userobj.projectuser.sandbox_project
        sandbox_project.save() #trigger save function to trigger auomatic check functions during saving an object
        
    if userobj.projectuser.sandbox_vehicle is None:
        query = Vehicle.objects.filter(project__name= "Sandbox Project" ,  owner_id = userobj.id)
        if query:
            sandbox_vehicle = query.first()
        else:
            sandbox_vehicle = Vehicle.objects.create(project=sandbox_project, name="Sandbox Vehicle", owner = userobj, )     
    else:
        sandbox_vehicle = userobj.projectuser.sandbox_vehicle
        sandbox_vehicle.save() #trigger save function to trigger auomatic check functions during saving an object


    #Check if sandbox_vehicle has non empty Energy Source model 

    userobj.projectuser.sandbox_project = sandbox_project
    userobj.projectuser.sandbox_vehicle = sandbox_vehicle
    userobj.projectuser.authorised_projects.add(sandbox_project)
    if not userobj.projectuser.current_project:
        userobj.projectuser.current_project = sandbox_project
    if not userobj.projectuser.authorised_projects.exists():
         userobj.projectuser.authorised_projects.add(sandbox_project)

    userobj.projectuser.save()