from django.forms import ModelForm
from django import forms



from BoltMan.models import Washer

class SingleassessmentWasherForm(forms.ModelForm):
    class Meta:
        model = Washer
        fields = ['washer_type', 'material', 'thickness', 'odiameter', 'idiameter','norm']