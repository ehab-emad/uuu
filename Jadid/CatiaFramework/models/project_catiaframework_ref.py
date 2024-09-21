from django.db import models
from django.urls import reverse
from website.generate_pk import generate_pk
from website.models import Project
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

class Project_CatiaFramework_Ref(models.Model):
    UUID = models.UUIDField(primary_key=True, verbose_name="UUID",   default=uuid.uuid4, editable=True)


    def _get_reference_project(self):
        try:
            return Project.objects.filter(UUID = self.UUID).get()
        except:
            return None

    reference_project = property(_get_reference_project)

    def __str__(self):
        if self.reference_project:
            if self.reference_project.owner:
                return str(self.reference_project.name + " Owner: " + self.reference_project.owner.username)
            else: 
                return str(self.reference_project.name + " Owner: " + "None")
        else:
            return ""
    class Meta:
        app_label = 'CatiaFramework'
            

@receiver(post_save, sender=Project)
def create_projectuser_normman_ref(sender, instance, created, **kwargs):
    if created:
        Project_CatiaFramework_Ref.objects.create(UUID = instance.UUID)
    else:
        query = Project_CatiaFramework_Ref.objects.filter(UUID = instance.UUID)
        if not query:
            Project_CatiaFramework_Ref.objects.create(UUID = instance.UUID)

def _get_reference_project(UUID):
    return Project_CatiaFramework_Ref.objects.filter(UUID = UUID).get()
