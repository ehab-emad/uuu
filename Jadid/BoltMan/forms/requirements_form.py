from django.forms import ModelForm
from django import forms



from BoltMan.models import Bolt_Requirements

class RequirementsForm(forms.ModelForm):
    class Meta:
        model = Bolt_Requirements
        fields = ['meaf', 'mesf', 'maxtemp', 'mintemp', 'elc']