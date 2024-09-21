from django.forms import ModelForm
from django import forms



from BoltMan.models import Friction_Head

class SingleassessmentFrictionHeadForm(forms.ModelForm):
    class Meta:
        model = Friction_Head
        fields = ['mat_1_name', 'mat_2_name', 'plating', 'colour', 'lubrication','friction_av', 'friction_min','friction_max', 'source', 'notes']
