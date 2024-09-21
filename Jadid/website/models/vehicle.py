from django.db import models as db_models
from django.urls import reverse
from django.conf import settings
from website.generate_pk import generate_pk
from django.db import models
from django.urls import reverse
from decimal import *
from django.core.validators import MinValueValidator, MaxValueValidator      
import uuid
PERCENTAGE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(100)]
NONNEGATIVE_VALIDATOR = [MinValueValidator(0),]


class Vehicle(db_models.Model):
    UUID = models.UUIDField(primary_key=True, verbose_name="UUID",   default=uuid.uuid4, editable=True)
    name = db_models.CharField(max_length=100,  default= 'DUMMY_CAR', editable=True, blank=True)
    created_at = db_models.DateTimeField(auto_now_add=True)
    updated_at = db_models.DateTimeField(auto_now=True)
    owner = db_models.ForeignKey(settings.AUTH_USER_MODEL, db_models.SET_NULL, blank=True,null=True,)
    project =db_models.ForeignKey("website.Project", help_text ="Select a Project for this vehicle", on_delete=db_models.CASCADE,  blank=True,null=True,)

    logo =db_models.CharField(default='Default Vehicle Logo', max_length=1000)
    is_favorite = db_models.BooleanField(default=False)

    target_weight = db_models.FloatField(editable=True, verbose_name= "Target Weight (kg)", default=0, validators=NONNEGATIVE_VALIDATOR,)
    estimated_weight = db_models.FloatField(editable=True, verbose_name= "Estmated Weight (kg)", default=0, validators=NONNEGATIVE_VALIDATOR,)
   
    #lifetime in km
    life_distance_in_km =db_models.IntegerField(editable=True, verbose_name= "Vehicle Lifetime Distance [km]", default = 250000)
    #life expectation
    life_time_in_years =db_models.IntegerField(editable=True, verbose_name= "Vehicle Lifetime [-] (years)", default = 10 )




    VC_CHOICES= [
    ("CLASS1", ("Class 1 - City Car (Example: VW UP!)")),
    ("CLASS2", ("Class 2 - Supermini (Example: VW Polo)")),
    ("CLASS3", ("Class 3 - Small Family Car (Example VW Golf)")),
    ("CLASS4", ("Class 4 - Compact Executive (Example: VW Passat)")),
    ("CLASS5", ("Class 5 - Executive Car (Example: MB E-class)")),
    ("CLASS6", ("Class 6 - Luxury Saloon (Example: MB S-class)")),
    ("CLASS7", ("Class 7 - Light Goods Transport (Example: VW Caddy)")),
    ("CLASS8", ("Class 8 - Medium Good Transport (Example: VW Transporter)")),
    ("CLASS9", ("Class 9 - Heavy Goods Transport (Example: VW Crafter)")),
    ("CLASS10", ("Class 10 - Mini SUV (Example: Opel Mokka)")),
    ("CLASS11", ("Class 11 - Small family SUV (Example Audi Q3)")),
    ("CLASS12", ("Class 12 - Large family SUV")),
    ("CLASS13", ("Class 13 - Executive SUV")),
    ("CLASS14", ("Class 14 - Small MPV")),
    ("CLASS15", ("Class 15 - Medium MPV")),
    ("CLASS16", ("Class 16 - Large MPV")),
    ("CLASS17", ("Class 17 - Light Trucks")),
    ("CLASS18", ("Class 18 - Heavy Trucks")),
    ]

    vehicle_classification = db_models.CharField(choices=VC_CHOICES, max_length=32, default="CLASS2")
    energy_source_model =db_models.OneToOneField("website.Energy_Source", verbose_name= "Model for primary and secondary energy source", on_delete=models.CASCADE, default=None, blank=True, null=True,)
    production_rate_model =db_models.OneToOneField("website.Production_Rate", verbose_name= "Model for production rate", on_delete=models.CASCADE, default=None, blank=True, null=True,)

    class Meta:
        app_label = 'website'

    def get_absolute_url(self):
        return reverse('ConceptMan', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name
