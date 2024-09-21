from django.db import models
from django.urls import reverse
from decimal import *
from website.generate_pk import generate_pk
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator
from django.core.exceptions import ValidationError
from EcoMan.QLCA_Idemat_Calculation import import_lca_constant
PERCENTAGE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(100)]
NONNEGATIVE_VALIDATOR = [MinValueValidator(0),]

class Lca_Database_Group(models.Model):
    identifier = models.CharField(max_length=3, validators=[MinLengthValidator(3)])    
    name = models.CharField(max_length=100,  default= 'Not defined', editable=True,)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.CharField(max_length=100,  default= 'Put your comment here...', editable=True, blank=True)
    category_model = models.ForeignKey("EcoMan.Lca_Database_Category", verbose_name="Category of the Group", on_delete=models.CASCADE,  null=True,)   

    class Meta:
        app_label = 'EcoMan'
    def __str__(self):
        return str(self.name)  