from django.forms import ModelForm
from django import forms



from BoltMan.models import Bolt_Geometry

class SingleassessmentBoltcaseBoltgeometryForm(forms.ModelForm):
    class Meta:
        model = Bolt_Geometry
        fields = '__all__'