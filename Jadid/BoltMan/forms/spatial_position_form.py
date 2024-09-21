from django.forms import ModelForm
from django import forms



from BoltMan.models import Spatial_Position

class PositionForm(forms.ModelForm):
    class Meta:
        model = Spatial_Position
        fields = ['x', 'y', 'z', 'xn', 'yn','zn']