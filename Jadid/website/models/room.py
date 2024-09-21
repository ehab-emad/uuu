
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings

class Room(models.Model):
    name = models.CharField(max_length=128)
    online = models.ManyToManyField(to=User, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, models.SET_NULL, blank=True,null=True, related_name='%(class)s_Owner')
    def get_online_count(self):
        return self.online.count()

    def join(self, user):
        self.online.add(user)
        self.save()

    def leave(self, user):
        self.online.remove(user)
        self.save()

    def __str__(self):
        return f'{self.name} ({self.get_online_count()})'