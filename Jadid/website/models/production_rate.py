
from django.db import models
from django.urls import reverse
from website.models import Vehicle
from website.generate_pk import generate_pk
from django.core.validators import MinValueValidator, MaxValueValidator
from django.dispatch import receiver
from django.db.models.signals import pre_save       
NONNEGATIVE_VALIDATOR = [MinValueValidator(0),]

class Production_Rate(models.Model):
    id = models.CharField(default=generate_pk, primary_key=True, max_length=255, unique=True)    
    name = models.CharField(max_length=100,  default= 'Not defined', editable=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.CharField(max_length=100,  default= 'Put your comment here...', editable=True, blank=True)

    production_time = models.IntegerField(editable=True, verbose_name= "Production Time [-] (years)", default = 5, blank=True, null=True, validators=NONNEGATIVE_VALIDATOR,)    
    production_rate_start = models.IntegerField(editable=True, verbose_name= "Production Rate at the Start of the Production [-] (units/year)", default = 0, blank=True, null=True, validators=NONNEGATIVE_VALIDATOR,)    
    production_rate_end = models.IntegerField(editable=True, verbose_name= "Production Rate at the End of the Production [-] (units/year)", default = 100000, blank=True, null=True, validators=NONNEGATIVE_VALIDATOR,)    
    production_rate_extremum_y = models.IntegerField(editable=True, verbose_name= "Min or Max Production Rate for Quadratic Model [-] (units/year)", default = 150000, blank=True, null=True, validators=NONNEGATIVE_VALIDATOR,)    
    production_rate_extremum_x = models.IntegerField(editable=True, verbose_name= "Year of Min Max Production [-] (year)", blank=True, null=True, default = 3, validators=NONNEGATIVE_VALIDATOR,)    

    PRODUCTION_RATE_MODEL_CHOICES= [
    ("FLAT", ("Flat")),
    ("LINEAR", ("Linear")),
    ("QUADRATIC", ("Quadratic")),
    ]
    approximation_model = models.CharField(choices=PRODUCTION_RATE_MODEL_CHOICES, max_length=32, default="FLAT")

    produced_units = models.IntegerField(editable=True, verbose_name= "Total Manufactured Units", blank=True, null=True, validators=NONNEGATIVE_VALIDATOR,)    


    def calc_parabola_vertex(self, x1, y1, x2, y2, x3, y3):
        denom = (x1-x2) * (x1-x3) * (x2-x3)
        A     = (x3 * (y2-y1) + x2 * (y1-y3) + x1 * (y3-y2)) / denom
        B     = (x3*x3 * (y1-y2) + x2*x2 * (y3-y1) + x1*x1 * (y2-y3)) / denom
        C     = (x2 * x3 * (x2-x3) * y1+x3 * x1 * (x3-x1) * y2+x1 * x2 * (x1-x2) * y3) / denom
        return A,B,C

    def calculate_produced_units(self):
        if self.approximation_model == "FLAT":
            self.produced_units = self.production_time * self.production_rate_start
        if self.approximation_model == "LINEAR":
            self.produced_units = 0.5 * self.production_time * abs(self.production_rate_start - self.production_rate_end)
        if self.approximation_model == "QUADRATIC":
            a,b,c = self.calc_parabola_vertex(0, self.production_rate_start, self.production_rate_extremum_x, self.production_rate_extremum_y, self.production_time, self.production_rate_end)

            integral = 1/3 * a * self.production_time**3 + b/2 * self.production_time**2 + c * self.production_time 
            self.produced_units = integral


    class Meta:
        app_label = 'website'
    def __str__(self):
        return str("ID:" + self.id)
    
    def save(self, *args, **kwargs): 
        self.calculate_produced_units()
        super(Production_Rate, self).save(*args, **kwargs)     

    @receiver(pre_save, sender=Vehicle)
    def create_production_rate(sender, instance,  **kwargs):
        if instance._state.adding:
              Production_Rate.objects.get_or_create(vehicle=instance)
        else:
            if hasattr(instance, 'production_rate_model') and instance.production_rate_model is None:
                  Production_Rate.objects.get_or_create(vehicle=instance)

