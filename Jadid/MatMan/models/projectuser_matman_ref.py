from django.db import models
from website.models import ProjectUser
from django.dispatch import receiver
from django.db.models.signals import post_save
from website.models import ProjectUser
import uuid
class ProjectUser_MatMan_Ref(models.Model):
    UUID = models.UUIDField(primary_key=True, verbose_name="UUID",   default=uuid.uuid4, editable=True)
    nickname = models.CharField(max_length=100,  default= 'Not defined', editable=True, blank=True)
    def __str__(self):
        return str(self.nickname)

    class Meta:
        app_label = 'MatMan'

    def _get_reference_projectuser(self):
        return ProjectUser.objects.filter(UUID = self.UUID).get()

    reference_projectuser = property(_get_reference_projectuser)


@receiver(post_save, sender=ProjectUser)
def create_projectuser_conceptman_ref(sender, instance, created, **kwargs):
    if created:
        ProjectUser_MatMan_Ref.objects.create(UUID = instance.UUID, nickname = instance.user.username)
