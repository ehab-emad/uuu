from django.db import models
from django.urls import reverse
from website.generate_pk import generate_pk
from website.models import Project
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

class Project_EcoMan_Ref(models.Model):
    UUID = models.UUIDField(primary_key=True, verbose_name="UUID",   default=uuid.uuid4, editable=True)


    def _get_reference_project(self):
        query = Project.objects.filter(UUID = self.UUID)
        if query:
            return Project.objects.filter(UUID = self.UUID).get()
        else:
            return None

    reference_project = property(_get_reference_project)

    def __str__(self):
        if self.reference_project:
            name =  self.reference_project.name + " " + str(self.reference_project.UUID)
        else:
            name = "Orphan project"   

        return name
    
       
    
    class Meta:
        app_label = 'EcoMan'  


@receiver(post_save, sender=Project)
def create_projectuser_ecoman_ref(sender, instance, created, **kwargs):
    if created:
        Project_EcoMan_Ref.objects.create(UUID = instance.UUID)



