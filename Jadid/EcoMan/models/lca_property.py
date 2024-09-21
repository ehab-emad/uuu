from django.db import models
from django.forms.models import model_to_dict
from website.generate_pk import generate_pk
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
NONNEGATIVE_VALIDATOR = [MinValueValidator(0),]
class Lca_Property(models.Model):
    id = models.CharField(default=generate_pk, primary_key=True, max_length=255, unique=True)
    name = models.CharField(max_length=100,  unique=True, verbose_name ='Name For Python Usage')
    verbose_name = models.CharField(max_length=100,  default= 'Not defined', verbose_name ='Name For Humanoids')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey("EcoMan.ProjectUser_EcoMan_Ref", models.SET_NULL, blank=True,null=True,)
    note = models.CharField(max_length=1000,  default= 'Put your import comment here...', blank=False)
    source=models.CharField(max_length=1000,  default= 'Note', editable=True, blank=True, )
    unit = models.CharField(max_length=50,  default= '-', blank=False)


    PROP_TYPE_CHOICES= [
    ("CORE", ("LCA Core Property")),
    ("USER", ("LCA User Property")),
    ]
    prop_type = models.CharField(choices=PROP_TYPE_CHOICES, max_length=32, default = "CORE")

    class Meta:
        app_label = 'EcoMan'
    def __str__(self):
        return str(self.verbose_name)
#############################################################################################

    def as_dict(self) ->dict:
        '''this function will create custom dictionary for a part object
        '''
        entry = {}
        entry.update(model_to_dict(self, exclude =['process_model', 'logo'] ))
        return entry


    @classmethod
    def get_default_pk(cls):
        ''' this function allow to find not hardcoded foreignkey for analysis_comparison.primary_property field
            if it does not exists it will be created
        '''

        lca_property, created = cls.objects.get_or_create(
            name='carbon_footprint',
            defaults=dict(note='This property was created automatically and should be reviewed',
                	        verbose_name ='GWP (Global Warming Potential) [kg C02eq)',
                            unit='kg'),
        )
        return lca_property.pk


