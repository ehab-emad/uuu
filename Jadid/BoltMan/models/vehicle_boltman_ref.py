from django.db import models
from website.models import Vehicle
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

class Vehicle_BoltMan_Ref(models.Model):
    UUID = models.UUIDField(primary_key=True, verbose_name="UUID",   default=uuid.uuid4, editable=True)


    def _get_reference_vehicle(self):
        return Vehicle.objects.filter(UUID = self.UUID).get()

    reference_vehicle = property(_get_reference_vehicle)

    def __str__(self):
        if self.reference_vehicle.owner:
            return str(self.reference_vehicle.name + " Owner: " + self.reference_vehicle.owner.username)
        else: 
            return str(self.reference_vehicle.name + " Owner: " + "None")
        
    class Meta:
        app_label = 'BoltMan'
            

@receiver(post_save, sender=Vehicle)
def create_vehicle_boltman_ref(sender, instance, created, **kwargs):
    if created:
        Vehicle_BoltMan_Ref.objects.create(UUID = instance.UUID)
