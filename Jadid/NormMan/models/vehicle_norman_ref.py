from django.db import models
from django.urls import reverse
from website.generate_pk import generate_pk
from website.models import Vehicle
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

class Vehicle_NormMan_Ref(models.Model):
    UUID = models.UUIDField(primary_key=True, verbose_name="UUID",   default=uuid.uuid4, editable=True)


    def _get_reference_vehicle(self):
        return Vehicle.objects.filter(UUID = self.UUID).get()

    reference_project = property(_get_reference_vehicle)

    def __str__(self):
        if self.owner:
            return str(self.name + " Owner: " + self.owner.username)
        else: 
            return str(self.name + " Owner: " + "None")
        
    class Meta:
        app_label = 'NormMan'
            

@receiver(post_save, sender=Vehicle)
def create_vehicle_conceptman_ref(sender, instance, created, **kwargs):
    if created:
        Vehicle_NormMan_Ref.objects.create(UUID = instance.UUID)
