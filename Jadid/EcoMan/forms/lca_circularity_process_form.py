
from django.forms import ModelForm
from django import forms
from django.forms import ValidationError
#from .models import *
from EcoMan.models import Analysis_Comparison
from EcoMan.models import Lca_Database_Process
from EcoMan.models import Instance_Idemat_Database_Process
from EcoMan.models import Lca_Part
from EcoMan.models import Utilisation_Process
from EcoMan.models import Circularity_Process
from website.models import Project
from ConceptMan.models import Part
from django.db.models import Q
from website.models import Vehicle

class CircularityInstanceUpdateForm(forms.ModelForm):
       
    def __init__(self, *args, **kwargs): 
        super(CircularityInstanceUpdateForm, self).__init__(*args, **kwargs)    
    class Meta:
        model = Circularity_Process
        fields = ('name','notes', 'lifetimeinkm')
        widgets = {
          'notes': forms.Textarea(attrs={'rows':4, }),
        }
    field_order = ['name', 'lifetimeinkm', 'notes',]   