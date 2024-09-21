from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_save
from website.generate_pk import generate_pk
import uuid
class ProjectUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    UUID = models.UUIDField(primary_key=True, verbose_name="UUID",   default=uuid.uuid4, editable=True)
    keycloak_UUID = models.UUIDField(primary_key=False, verbose_name="Keycloak User UUID",   default=uuid.uuid4, editable=True)
    logo = models.CharField(default='Default Project Logo', max_length=1000)
    current_project = models.ForeignKey("website.Project", blank=True, null=True, on_delete=models.SET_NULL)
    sandbox_project = models.ForeignKey("website.Project", blank=True, null=True,  related_name='%(class)s_sandbox', on_delete=models.SET_NULL)
    sandbox_vehicle = models.ForeignKey("website.Vehicle", blank=True, null=True, on_delete=models.SET_NULL)
    current_workflow_session = models.ForeignKey("NormMan.Workflow_Session", blank=True, null=True, on_delete=models.SET_NULL)
    authorised_projects =  models.ManyToManyField("website.Project", verbose_name="Authorised Projects ", related_name='%(class)s_auth',  blank=True,)
    tokens = models.ManyToManyField('website.Token', blank=True, symmetrical=False, related_name='users_with_token', help_text="Users available tokens")
    framework_connected = models.BooleanField(default =False,)    
    catia_connected = models.BooleanField(default =False,)
    framework_update = models.BooleanField(default =False,) #should be uptodate and function which ist checking and returning!
    expiration_date = models.DateField(null = True,)
    
    def __str__(self):
        return str(self.user.username)

@receiver(post_save, sender=User)
def create_projectuser(sender, instance, created, **kwargs):
    if created:
        # if 'temp_uuid' in dir(instance):
        #     new_pUser = ProjectUser.objects.create(user=instance, UUID=instance.temp_uuid)
        # else:
        new_pUser = ProjectUser.objects.create(user=instance)
        organisation_project = Project.objects.filter(name = "Organisation_LCA_Project" )
        if organisation_project:
            organisation_project = organisation_project.get()
        else:
            organisation_project = Project.objects.create(name = "Organisation_LCA_Project" )       
        new_pUser.authorised_projects.add(organisation_project)
        new_pUser.save()
        return


def check_user_sandbox(userobj):
    """
    This function checks if active ProjectUser has available Sandbox_Vehicle object and Sandbox Project Objects assigned. 
    If not they will be assigned or even created if necessary
    """
    from website.models import Vehicle
    from website.models import Vehicle    
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


@receiver(post_save, sender=User)
def save_projectuser(sender, instance, **kwargs):
    check_user_sandbox(instance)

from website.models import Project
@receiver(post_save, sender=Project)
def create(sender, instance, created, **kwargs):
    '''it is important to create anonymous user for 
     every project in case user will be removed from the whitelist all objects created from this user will be anonymized
    '''
    if created:   
        if instance.isusersandbox == False: #for user sandbox projects no anonymous projecst will be generated    
            anonymous_user = User.objects.create(username = 'anonymous_' + str(instance.UUID))# from digilab_user_auth import WhitelistedEdagUser
            anonymous_user.projectuser.authorised_projects.add(instance)
            anonymous_user.save()



