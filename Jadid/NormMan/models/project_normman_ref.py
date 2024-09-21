from django.db import models
from django.urls import reverse
from website.generate_pk import generate_pk
from website.models import Project
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

class Project_NormMan_Ref(models.Model):
    UUID = models.UUIDField(primary_key=True, verbose_name="UUID",   default=uuid.uuid4, editable=True)


    def _get_reference_project(self):
        return Project.objects.filter(UUID = self.UUID).get()

    reference_project = property(_get_reference_project)

    def __str__(self):
        if self.reference_project.owner:
            return str(self.reference_project.name + " Owner: " + self.reference_project.owner.username)
        else: 
            return str(self.reference_project.name + " Owner: " + "None")
        
    class Meta:
        app_label = 'NormMan'
            

@receiver(post_save, sender=Project)
def create_projectuser_normman_ref(sender, instance, created, **kwargs):
    if created:
        Project_NormMan_Ref.objects.create(UUID = instance.UUID)

