from django.forms import ModelForm
from django import forms



from BoltMan.models import Friction_Thread

class SingleassessmentFrictionThreadForm(forms.ModelForm):
    class Meta:
        model = Friction_Thread
        fields = ['f_class', 'colour', 'surface', 'precision', 'lubrication','friction_av', 'friction_min','friction_max', 'source', 'notes']

