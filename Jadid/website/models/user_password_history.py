#this model is used only in qlca standalone!

from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from website.generate_pk import generate_pk
from .projectuser import ProjectUser

class UserPasswordHistory(models.Model):
    id = models.CharField(default=generate_pk, primary_key=True, max_length=255, unique=True)
    date = models.DateTimeField(auto_now_add=True)
    password = models.CharField("password", max_length=128)
    project_user = models.ForeignKey(ProjectUser, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.password)
    class Meta:
        app_label = 'website'