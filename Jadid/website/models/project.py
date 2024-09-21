from django.db import models
from django.conf import settings

import uuid
class Project(models.Model):
    UUID = models.UUIDField(primary_key=True, verbose_name="UUID",   default=uuid.uuid4, editable=True)
    name = models.CharField(max_length=100,  default= 'DUMMY_PROJECT', editable=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, models.SET_NULL, blank=True,null=True,)
    logo = models.ImageField(upload_to ='uploads/', null=True, blank=True, verbose_name = "Project Image")
    network_number = models.IntegerField( editable=True, blank=True, null=True,)
    project_manager=models.CharField(max_length=100,  default= 'Name, Surname', editable=True, blank=True)
    isusersandbox=models.BooleanField(default = False,)


    PROTECTIONCLASS_CHOICES= [
    ("PUBLIC", ("Public")),
    ("INTERNAL", ("Internal")),    
    ("CONFIDENTIAL", ("Confidential")),  
    ("STRICTLY_CONFIDENTIAL", ("Strictly Confidential")),      
    ] 
    protection_class = models.CharField(choices=PROTECTIONCLASS_CHOICES, verbose_name="Processes Visualisation Style",max_length=100, default="CONFIDENTIAL",)

    class Meta:
        app_label = 'website'

    def __str__(self):
        if self.owner:
            return str(self.name + " Owner: " + self.owner.username)
        else: 
            return str(self.name + " Owner: " + "None")
        
    @staticmethod
    def get_anonymous_projectuser(project_UUID):
        from website.models import ProjectUser
        from django.contrib.auth.models import User
        user = User.objects.filter(username = "anonymous_" + str(project_UUID)).first() 
        if user:
            return  user.projectuser
        else:
            #anonymous project user does not exists and has to be creted
            anonymous_user = User.objects.create(username = 'anonymous_' + str(project_UUID))
            anonymous_user.projectuser.authorised_projects.add(Project.objects.filter(UUID = project_UUID).first())
            anonymous_user.save()
            return anonymous_user.projectuser