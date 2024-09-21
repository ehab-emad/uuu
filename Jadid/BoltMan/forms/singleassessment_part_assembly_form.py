from django.forms import ModelForm
from django import forms



from BoltMan.models import Bolted_Part

class SingleassessmentPartForm(forms.ModelForm):
    class Meta:
        model = Bolted_Part
        fields = ['name', 'thickness', 'material']